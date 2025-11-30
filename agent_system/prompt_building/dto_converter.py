import re

from agent_system.prompt_building.game_master import DNDGameMaster
from agent_system.prompt_building.prompt_builder import Prompt

# If you have these instruction strings defined elsewhere, import them here:
from agent_system.prompt_building.instructions import (
    BEGINNING_INSTRUCTION,
    ENDING_INSTRUCTION,
    MULTIPLE_CHOICE_INSTRUCTION,
    OPEN_CHOICE_INSTRUCTION,
)


def extract_options_from_assistant_text(assistant_text: str):
    """
    Given the assistant text for a multiple-choice scenario,
    extract the possible options using regex (e.g. "Option 1: Yes\nOption 2: No\n").
    """
    # Example pattern: "Option 1: Foo\nOption 2: Bar\n"
    options = re.findall(r"Option\s+\d+:\s+(.*?)\n", assistant_text)
    return options


def story_to_dto(story: DNDGameMaster):
    """
    Given a list of Prompt objects (each of which has .prompt_list with system/user/assistant entries),
    build a JSON-like dictionary structure that captures the story beginning,
    any chapters (open or multiple choice), the ending if present, and the raw prompts.

    - The system text determines if we're dealing with a Beginning, Chapter, or Ending.
    - If the system text contains MULTIPLE_CHOICE_INSTRUCTION, parse assistant text for options.
    - If user text is missing, then 'response' is marked as None (unanswered).
    - If system text has BEGINNING_INSTRUCTION => story beginning.
    - If system text has ENDING_INSTRUCTION => story ending.
    - Otherwise if system text has OPEN_CHOICE_INSTRUCTION or MULTIPLE_CHOICE_INSTRUCTION => a story chapter.

    Additionally:
    - We store the **exact** content of all prompts under "full_prompts" to allow full reconstruction later.
    """

    # We will collect data in these variables
    beginning_text = None
    ending_text = None
    chapters = []

    # For restoration: store the *full* prompt data exactly.
    full_prompts_data = []

    for prompt_obj in story.prompts:

        # Keep a copy of the .prompt_list to store in the final JSON "as is"
        # (so we can reconstruct later with zero modifications).
        raw_prompt_list = []
        for comp in prompt_obj.prompt_list:
            # Copy each dictionary exactly (role + text)
            raw_prompt_list.append({"role": comp["role"], "text": comp["text"]})

        # Also parse for story structure
        system_text = None
        user_answer = None
        assistant_text = None

        user_text_counter = 0
        for component in prompt_obj.prompt_list:
            role = component["role"]
            text = component["text"]

            if role == "system":
                system_text = text
            elif role == "user":
                if user_text_counter != 0:
                    user_answer = text
                user_text_counter += 1
            elif role == "assistant":
                assistant_text = text

        # Add to the "full_prompts" container

        full_prompts_data.append({"prompt_list": raw_prompt_list})

        # If there's no system text, skip or handle differently
        if not system_text:
            continue

        # ----------------------------------------------------
        # Identify which type of "chapter" or "section" this is
        # ----------------------------------------------------
        if BEGINNING_INSTRUCTION in system_text:
            # The story beginning (keep the text EXACT)
            beginning_text = assistant_text

        elif ENDING_INSTRUCTION in system_text:
            # The story ending
            ending_text = assistant_text

        elif (MULTIPLE_CHOICE_INSTRUCTION in system_text) or (
            OPEN_CHOICE_INSTRUCTION in system_text
        ):
            # This is a story chapter
            is_multiple_choice = MULTIPLE_CHOICE_INSTRUCTION in system_text

            # If there's no user text, story is paused (unanswered => None)
            if not user_answer:
                chapter_response = None
            else:
                chapter_response = user_answer

            # For multiple choice, parse the assistant text for options
            if is_multiple_choice and assistant_text:
                raw_assistant_text = assistant_text
                options = extract_options_from_assistant_text(raw_assistant_text)
                # Remove all lines starting with "Option <number>: " from the assistant text
                assistant_text = re.sub(
                    r"Option\s+\d+:\s.*(?:\n|$)", "", raw_assistant_text
                ).strip()
            else:
                options = []

            chapters.append(
                {
                    "story_text": (
                        assistant_text.replace("<|eot_id|>", "")
                        if isinstance(assistant_text, str)
                        else assistant_text
                    ),
                    "response": (
                        chapter_response.replace("<|eot_id|>", "")
                        if isinstance(chapter_response, str)
                        else chapter_response
                    ),
                    "open_ended": not is_multiple_choice,
                    # Include options if we have them
                    "options": options if is_multiple_choice else None,
                }
            )

        else:
            # If system text doesn't match any recognized instruction, do nothing or handle fallback
            pass

    # --------------------------------------------------------
    # Build the final JSON structure
    # --------------------------------------------------------

    back_data = {
        "max_chapters": story.max_chapters,
        "story_id": story.story_id,
        "qualities": story.qualities,
        "full_prompts": full_prompts_data,
        "qualities_to_assess": story.qualities_to_assess,
        "story_title": story.story_title,
    }

    front_data = {
        "story_id": story.story_id,
        "max_chapters": story.max_chapters,
        "story": {
            "name": story.story_title,
            "beginning": (
                beginning_text.replace("<|eot_id|>", "")
                if isinstance(beginning_text, str)
                else beginning_text
            ),
            "chapters": chapters,
            "ending": (
                ending_text.replace("<|eot_id|>", "")
                if isinstance(ending_text, str)
                else ending_text
            ),
        },
    }

    return front_data, back_data


def dto_to_story(story_data) -> DNDGameMaster:
    """
    Given a JSON structure (as produced by parse_prompts_into_story),
    reconstruct and return the original list of Prompt objects with identical text.

    'prompt_class' should be the Prompt class definition you use in your code.
    (We pass it in so we can instantiate the same class type.)
    """

    reconstructed_prompts = []
    # Read the "full_prompts" data
    if "full_prompts" not in story_data:
        story = DNDGameMaster(story_data["story_id"])
        return story

    for prompt_info in story_data["full_prompts"]:
        # Create a new Prompt instance
        new_prompt = Prompt()

        # Directly assign the prompt_list from the stored data
        # so it perfectly matches the original
        new_prompt.prompt_list = prompt_info["prompt_list"]

        reconstructed_prompts.append(new_prompt)

    story = DNDGameMaster(story_data["story_id"])
    story.load_story_data(
        reconstructed_prompts,
        story_data["max_chapters"],
        story_data["qualities"],
        story_data["qualities_to_assess"],
        story_data["story_title"],
    )

    return story
