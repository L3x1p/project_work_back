import asyncio
from fastapi import HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from agent_system.prompt_building.game_master import DNDGameMaster
from agent_system.prompt_building.game_master_ops import (
    init_story,
    continue_story,
    evaluate_quality,
    answer_chapter,
    extract_score,
    end_story,
)
from agent_system.prompt_building.dto_converter import story_to_dto, dto_to_story
from agent_system.vllm_connection import generate
from postgres_db.models import Adventure, UserTrait
from typing import Optional
from agent_system.quality_evaluation.job_orientation_results import (
    update_job_orientation,
    create_job_orientation_results,
)
from postgres_db.models import JobOrientationResult
import re


def insert_story(story: DNDGameMaster, db: Session):
    # Convert story to DTO format
    front_data, back_data = story_to_dto(story)

    # Update the adventure record with the story structure
    adventure = (
        db.query(Adventure).filter(Adventure.adventure_id == story.story_id).first()
    )
    if not adventure:
        raise HTTPException(status_code=404, detail="Adventure not found")

    adventure.story_structure = back_data
    db.commit()


async def create_story_service(
    story_request, db: Session, user_id: int
) -> StreamingResponse:
    # check if story_request.parent_result_id is None
    if story_request.parent_result_id is None:
        # check if there is root adventure for this user
        adventures = db.query(Adventure).filter(Adventure.user_id == user_id).all()
        if adventures:
            raise HTTPException(
                status_code=400, detail="User already has ROOT adventure"
            )
    else:
        # check if the parent_result_id exists in the JobOrientationResult table
        parent_result = (
            db.query(JobOrientationResult)
            .filter(JobOrientationResult.result_id == story_request.parent_result_id)
            .first()
        )
        print(f"PARENT RESULT: {parent_result}")
        if not parent_result:
            raise HTTPException(
                status_code=400, detail="Parent result ID does not exist"
            )

    # Create the Adventure record
    new_adventure = Adventure(
        user_id=user_id,
        story_structure={},
        parent_result_id=story_request.parent_result_id,
    )
    db.add(new_adventure)
    db.commit()
    db.refresh(new_adventure)

    # Initialize story context
    story = DNDGameMaster(story_id=new_adventure.adventure_id)

    # Load user traits (or create default ones if none exist) and bind to story.qualities
    user_traits = db.query(UserTrait).filter(UserTrait.user_id == user_id).first()
    if user_traits:
        story.qualities = user_traits.trait_json
    else:
        default_traits = {
            "Teamwork": [],
            "Creativity": [],
            "Leadership": [],
            "Extroversion": [],
            "Risk Tolerance": [],
            "Drive for Power": [],
            "Entrepreneurialism": [],
            "Ethical Guidelines": [],
            "Result Orientation": [],
            "Attention to Detail": [],
            "Emotional Stability": [],
        }
        user_traits = UserTrait(user_id=user_id, trait_json=default_traits)
        db.add(user_traits)
        db.commit()
        db.refresh(user_traits)

    # Generate the initial prompt and topic for the story
    init_prompt, topic = init_story(story)

    # Update the adventure with the temporary story structure
    temp_story = DNDGameMaster(story_id=new_adventure.adventure_id, story_title=topic)
    temp_story.qualities = user_traits.trait_json

    _, back_data = story_to_dto(temp_story)
    new_adventure.story_structure = back_data
    db.commit()

    # Generate LLM streaming response based on the initial prompt
    stream_response = await generate(init_prompt, stream=True)
    queue = asyncio.Queue()

    async def process_stream():
        full_text = ""
        try:
            async for chunk in stream_response.body_iterator:
                full_text += chunk
                await queue.put(chunk)
            # Finalize the story processing
            story.prompts[-1].add_instruction(full_text)
            await queue.put(None)

            # Update the adventure record with the final story structure
            insert_story(story, db)
        except Exception as e:
            await queue.put(None)
            print(f"Error in process_stream: {e}")
            raise

    # Shield the processing to protect it from cancellation
    processing_task = asyncio.shield(asyncio.create_task(process_stream()))

    async def event_generator():
        sliding_window = []  # buffer to hold up to 10 chunks
        while True:
            chunk = await queue.get()
            if chunk is None:
                # Flush any remaining chunks in the sliding window.
                while sliding_window:
                    yield sliding_window.pop(0)
                break
            sliding_window.append(chunk)

            # If the sliding window grows larger than 10, yield and remove the oldest chunk.
            if len(sliding_window) > 10:
                yield sliding_window.pop(0)

            # Join the sliding window and check for the Option pattern.
            joined_window = "".join(sliding_window)
            if re.search(r"Option\s+\d+:\s", joined_window):
                # Pattern detected: yield only the text up to the last newline.
                last_newline_index = joined_window.rfind("\n")
                if last_newline_index != -1:
                    yield joined_window[: last_newline_index + 1]
                else:
                    yield ""
                break
        await processing_task

    return StreamingResponse(
        event_generator(),
        media_type="text/plain",
        headers={"story_id": str(new_adventure.adventure_id)},
    )


def get_story(story_id: int, db: Session):
    """
    Retrieve a story by its ID.
    """
    # Get the adventure record from the database
    adventure = db.query(Adventure).filter(Adventure.adventure_id == story_id).first()

    if not adventure:
        raise HTTPException(status_code=404, detail="Story not found")

    # If there is no stored story structure, return an initial placeholder object
    if not adventure.story_structure:
        return {
            "story_id": story_id,
            "max_chapters": 0,
            "story": {
                "name": "",
                "beginning": "Story is still being generated...",
                "chapters": [],
                "ending": None,
            },
        }

    # Convert stored story structure back to DNDGameMaster object
    story = dto_to_story(adventure.story_structure)

    # Convert to DTO format and return front-end data
    front_data, _ = story_to_dto(story)
    front_data["story_title_id"] = (
        adventure.story_structure["story_title"]
        .replace(" ", "_")
        .replace("`", "")
        .replace("'", "")
        .lower()
    )

    return front_data


def delete_user_stories(user_id: int, db: Session):
    """
    Delete all stories/adventures associated with a user.
    """
    # Get all adventures for this user
    adventures = db.query(Adventure).filter(Adventure.user_id == user_id).all()

    if not adventures:
        raise HTTPException(status_code=404, detail="No stories found for this user")

    # Delete all adventures for this user
    for adventure in adventures:
        db.delete(adventure)

    db.commit()

    return {"message": f"Successfully deleted all stories for user {user_id}"}


async def stream_with_update(
    stream_response, story: DNDGameMaster, db: Session, update_fn
):
    """
    Process a streaming response and update the story at the end.
    """
    queue = asyncio.Queue()

    async def process_stream():
        full_text = ""
        try:
            async for chunk in stream_response.body_iterator:
                full_text += chunk
                await queue.put(chunk)
            story.prompts[-1].add_instruction(full_text)
            await queue.put(None)  # End signal

            # Call the update function (synchronously)
            update_fn(story, db)
        except Exception as e:
            await queue.put(None)
            print(f"Error in process_stream: {e}")
            raise

    # Shield the task from cancellation.
    protected_task = asyncio.shield(asyncio.create_task(process_stream()))

    async def event_generator():
        sliding_window = []  # buffer to hold up to 10 chunks
        while True:
            chunk = await queue.get()
            if chunk is None:
                # Flush any remaining chunks in the sliding window.
                while sliding_window:
                    yield sliding_window.pop(0)
                break
            sliding_window.append(chunk)

            # If the sliding window grows larger than 10, yield and remove the oldest chunk.
            if len(sliding_window) > 10:
                yield sliding_window.pop(0)

            # Join the sliding window and check for the Option pattern.
            joined_window = "".join(sliding_window)
            if re.search(r"Option\s+\d+:\s", joined_window):
                # Pattern detected: yield only the text up to the last newline.
                last_newline_index = joined_window.rfind("\n")
                if last_newline_index != -1:
                    yield joined_window[: last_newline_index + 1]
                else:
                    yield ""
                break
        await protected_task

    return StreamingResponse(event_generator(), media_type="text/plain")


async def continue_story_service(
    story: DNDGameMaster, db: Session, answer_text: Optional[str] = None
):
    """
    Combine continuation flow for both initial chapter (chapter_number == 0) and subsequent chapters (chapter_number > 0 up to max_chapters).
    When chapter_number > 0, the provided answer_text is used to update the story,
    otherwise the story is simply continued.
    """
    if story.chapter_number > 0 and story.chapter_number <= story.max_chapters:
        # Process the answer and update story qualities
        answer_chapter(story, answer_text)
        eval_prompt = evaluate_quality(story, story.qualities_to_assess[-1])
        eval_response = await generate(
            eval_prompt, stream=False, top_p=0.95, temperature=0.4
        )
        score = extract_score(eval_response["answer"])
        story.update_qualities(story.qualities_to_assess[-1], score)

    cont_prompt = continue_story(story)
    stream_response = await generate(cont_prompt, stream=True)
    response = await stream_with_update(stream_response, story, db, update_story)
    response.headers["story_id"] = str(story.story_id)
    return response


def update_story(story: DNDGameMaster, db: Session):
    _, back_data = story_to_dto(story)
    adventure = (
        db.query(Adventure).filter(Adventure.adventure_id == story.story_id).first()
    )
    adventure.story_structure = back_data
    db.commit()


async def end_story_service(
    story: DNDGameMaster, db: Session, user_id: int, answer_text: str
):
    """
    Handles ending the story when chapter_number > max_chapters.
    Processes the final answer, evaluates quality, generates ending prompt,
    updates user traits, and streams the final response.
    """
    # Process the user's final answer
    answer_chapter(story, answer_text)
    eval_prompt = evaluate_quality(story, story.qualities_to_assess[-1])
    eval_response = await generate(
        eval_prompt, stream=False, top_p=0.95, temperature=0.4
    )
    score = extract_score(eval_response["answer"])
    story.update_qualities(story.qualities_to_assess[-1], score)

    # Retrieve user traits, update with story qualities, and commit changes
    update_job_orientation(story, db, user_id)
    # Try to create job orientation results, retrying if necessary
    await create_job_orientation_results(story, db, user_id)
    # Generate ending prompt and streaming response
    end_prompt = end_story(story)
    stream_response = await generate(end_prompt, stream=True)

    response = await stream_with_update(stream_response, story, db, update_story)
    response.headers["story_id"] = str(story.story_id)
    return response


def get_all_stories_by_user_id_service(user_id: int, db: Session):
    """
    Retrieve all stories for a given user ID.
    """
    # Fetch all adventures for the given user_id
    adventures = db.query(Adventure).filter(Adventure.user_id == user_id).all()

    if not adventures:
        raise HTTPException(status_code=404, detail="No stories found for the user.")

    # Convert each adventure's story structure back to DNDGameMaster objects
    gms = [dto_to_story(adventure.story_structure) for adventure in adventures]
    stories = []
    for gm in gms:
        front, _ = story_to_dto(gm)
        stories.append(front)

    # Sort stories by story_id and limit to the first 3
    stories.sort(key=lambda x: x["story_id"])
    stories = stories[:3]
    content = {"stories": stories}
    return JSONResponse(content=content)


def get_main_menu_map(user_id: int, db: Session):
    adventures = db.query(Adventure).filter(Adventure.user_id == user_id).all()

    if not adventures:
        raise HTTPException(status_code=404, detail="No stories found for the user.")

    # Convert each adventure's story structure back to DNDGameMaster objects

    stories = []
    for adventure in adventures:
        job_orientation_results = (
            db.query(JobOrientationResult)
            .filter(JobOrientationResult.parent_adventure_id == adventure.adventure_id)
            .all()
        )
        stories.append(
            {
                "story_id": adventure.adventure_id,
                "created_at": adventure.created_at,
                "story_title": adventure.story_structure["story_title"],
                "max_chapters": adventure.story_structure["max_chapters"],
                "job_orientation_results": [
                    {
                        "id": result.result_id,
                        "name": result.name,
                        "profession": result.profession,
                        "description": result.description,
                        "isco_code": result.isco_code,
                        "score": result.score,
                    }
                    for result in job_orientation_results
                ],
                "parent_result_id": adventure.parent_result_id,
                "story_title_id": adventure.story_structure["story_title"]
                .replace(" ", "_")
                .replace("`", "")
                .replace("'", "")
                .lower(),
            }
        )

    return stories
