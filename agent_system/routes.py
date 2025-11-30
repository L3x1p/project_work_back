from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from postgres_db.database_ops import get_db
from agent_system.quality_evaluation.job_orientation_results import (
    debug_update_job_orientation_results,
)
from agent_system.schemas import InitStoryRequest, SubmitAnswerRequest
from agent_system.quality_evaluation.traits_conversion_services import (
    convert_to_ocean,
)
from agent_system.story_update_services import (
    create_story_service,
    get_story as get_story_service,
    delete_user_stories as delete_user_stories_service,
    continue_story_service,
    end_story_service,
    get_all_stories_by_user_id_service,
    get_main_menu_map,
)
import logging
from postgres_db.models import Adventure, UserTrait
from agent_system.prompt_building.dto_converter import story_to_dto, dto_to_story
from auth.jwt_handler import verify_access_token
from typing import Optional, Dict
router = APIRouter()
logging.basicConfig(level=logging.INFO)
logging.getLogger("openai").setLevel(logging.WARNING)


@router.post("/stories/")
async def create_story(
    story_request: InitStoryRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_access_token),
):
    return await create_story_service(story_request, db, user_id)


@router.get("/stories/{story_id}")
def get_story(story_id: int, db: Session = Depends(get_db)):
    return get_story_service(story_id, db)


@router.delete("/users/stories")
def delete_user_stories(
    db: Session = Depends(get_db), user_id: int = Depends(verify_access_token)
):
    return delete_user_stories_service(user_id, db)


@router.put("/stories/{story_id}")
async def answer_story(
    story_request: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    # Get the story from the database
    adventure = (
        db.query(Adventure)
        .filter(Adventure.adventure_id == story_request.story_id)
        .first()
    )

    if not adventure:
        raise HTTPException(status_code=404, detail="Story not found")

    # Convert stored story structure back to DNDGameMaster object
    story = dto_to_story(adventure.story_structure)
    front, _ = story_to_dto(story)
    if front["story"]["beginning"] is None:
        raise HTTPException(status_code=400, detail="Story not properly initialized")

    if story.chapter_number > story.max_chapters + 1:
        raise HTTPException(
            status_code=400, detail="Cannot submit answer. The story has already ended."
        )
    elif story.chapter_number > story.max_chapters:
        # Delegate ending logic to the new service function.
        return await end_story_service(
            story,
            db,
            adventure.user_id,
            answer_text=story_request.answer_text,
        )
    elif story.chapter_number <= story.max_chapters:
        # Use the new combined continue flow
        return await continue_story_service(
            story, db, answer_text=story_request.answer_text
        )


@router.get("/users/stories")
def get_all_stories_by_user_id(
    user_id: int = Depends(verify_access_token), db: Session = Depends(get_db)
):
    return get_all_stories_by_user_id_service(user_id, db)


@router.get("/users/stories/map")
def get_stories_map(
    user_id: int = Depends(verify_access_token), db: Session = Depends(get_db)
):
    return get_main_menu_map(user_id, db)


# endpoint to delete user traits
@router.delete("/users/traits")
def delete_user_traits(
    db: Session = Depends(get_db), user_id: int = Depends(verify_access_token)
):
    db.query(UserTrait).filter(UserTrait.user_id == user_id).delete()
    db.commit()
    return {"message": "User traits deleted"}


@router.get("/users/data/diagrams")
def get_data_diagrams(
    user_id: int = Depends(verify_access_token), db: Session = Depends(get_db)
):
    """
    Endpoint to retrieve data diagrams for a user.
    Returns visualization data based on user's traits and job orientation results.
    """
    # Get user traits

    user_traits = db.query(UserTrait).filter(UserTrait.user_id == user_id).first()

    if not user_traits:
        return {"ocean": {}, "traits": {}}
    traits_dict = user_traits.trait_json

    # Calculate average for each trait and round to 2 decimal places
    traits_avg = {
        trait: round(sum(scores) / len(scores), 2) if scores else 0.0
        for trait, scores in traits_dict.items()
    }

    # Check if all traits have at least one value
    all_traits_have_values = all(len(scores) > 0 for scores in traits_dict.values())

    if not all_traits_have_values:
        # If any trait is missing values, only return traits data
        return {"ocean": {}, "traits": {}}

    ocean_scores = convert_to_ocean(traits_dict)

    # Round OCEAN scores to 2 decimal places
    ocean_rounded = {factor: round(score, 2) for factor, score in ocean_scores.items()}

    return {"ocean": ocean_rounded, "traits": traits_avg}


# REMOVE ------------------------\/------------------------------
class JobOrientationUpdateParams(BaseModel):
    reddit: bool = True
    youtube: bool = True
    traits: Optional[Dict[str, int]] = {
        "Entrepreneurialism": 0,
        "Drive for Power": 0,
        "Result Orientation": 0,
        "Creativity": 0,
        "Risk Tolerance": 0,
        "Leadership": 0,
        "Teamwork": 0,
        "Extroversion": 0,
        "Attention to Detail": 0,
        "Emotional Stability": 0,
        "Ethical Guidelines": 0,
    }


@router.post("/users/debug/job-orientation-results")
async def debug_job_orientation_results(
    params: JobOrientationUpdateParams,
    user_id: int = Depends(verify_access_token),
    db: Session = Depends(get_db),
):
    return await debug_update_job_orientation_results(
        db, user_id, params.reddit, params.youtube, params.traits
    )


# REMOVE -----------------------/\-------------------------------
