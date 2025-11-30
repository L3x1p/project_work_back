from agent_system.prompt_building.game_master import DNDGameMaster
from agent_system.prompt_building.prompt_builder import Prompt

from agent_system.prompt_building.instructions import (
    BEGINNING_INSTRUCTION,
    ENDING_INSTRUCTION,
    MULTIPLE_CHOICE_INSTRUCTION,
    OPEN_CHOICE_INSTRUCTION,
    STORY_BEGIN,
    STORY_COMES_CLIMAX,
    STORY_CLIMAX_PASSED,
    STORY_FINAL_CHAPTERS,
    EVAL_INSTRUCTION,
)
import random
import re
import json


def continue_story(story: DNDGameMaster):
    if story.chapter_number <= story.max_chapters:

        chosen_quality = story.get_least_assessed_quality()

        vars_or_open = random.randint(0, 1)
        # vars_or_open = 0 if story.chapter_number % 2 == 0 else 1
        # vars_or_open = 0

        instruction = (
            OPEN_CHOICE_INSTRUCTION
            if vars_or_open == 1
            else MULTIPLE_CHOICE_INSTRUCTION
        )

        continue_story_prompt = Prompt()
        continue_story_prompt.add_role_tag("system")
        continue_story_prompt.add_instruction(
            f"You're tough but fair DND-like gamemaster. Only write story text, DO NOT tell user anything from instructions."
            f" DO NOT make story long. {instruction}"
            f" Your story part should test user's quality of their choice in context of profession quality. "
        )
        continue_story_prompt.add_role_tag("user")

        story_end_percentage = int(story.chapter_number / story.max_chapters * 100)
        if story_end_percentage < 20:
            story_percentage_finished_instruction = STORY_BEGIN
        elif 20 <= story_end_percentage <= 50:
            story_percentage_finished_instruction = STORY_COMES_CLIMAX
        elif 50 <= story_end_percentage < 90:
            story_percentage_finished_instruction = STORY_CLIMAX_PASSED
        else:
            story_percentage_finished_instruction = STORY_FINAL_CHAPTERS

        continue_story_prompt.add_instruction(
            f"Write story part. This is part {story.chapter_number} out of {story.max_chapters}. "
            f"{story_percentage_finished_instruction}"
            f"Make it clear and short. Make this story part check my quality: {chosen_quality}. "
        )
        continue_story_prompt.add_role_tag("assistant")

        story.prompts.append(continue_story_prompt)

        total_prompt = sum(story.prompts, Prompt())
        story.qualities_to_assess.append(chosen_quality)
        story.logger.info(f"SETTED QUALITY ASSESSMENT: {chosen_quality}")

        story.chapter_number += 1
        # res = story.send(total_prompt)

        return total_prompt


def init_story(story: DNDGameMaster):

    adventure_titles = [
        # Classic Fantasy Adventures
        "The Tomb of the Forgotten King,   Ancient crypt haunted by a restless monarch's spirit.",
        "The Cursed Peaks of Frostbane,   Icy mountains plagued by frost giants and a chilling curse.",
        "The Labyrinth of the Emerald Minotaur,   Sprawling underground maze guarded by a monstrous minotaur.",
        "The Siege of Ravenwatch Keep,   Defend a castle under siege by undead forces.",
        "The Crystal Caverns of Silverdeep,   Glittering caves with sentient crystals and Underdark terrors.",
        # Urban Intrigue Adventures
        "The Masquerade of Midnight,   Uncover a deadly conspiracy during a lavish masked ball.",
        "The Gilded Shadows of Larkspur,   Investigate high-profile thefts in a noble district.",
        "The Bazaar of Broken Promises,   Navigate a mystical marketplace where contracts are sealed with souls.",
        "The Clockwork Conspiracy,   Expose a cabal sabotaging the city's defenses with mechanical constructs.",
        "The Warlock's Web,   Unravel a power struggle between guilds backed by fiendish patrons.",
        # High Seas and Coastal Adventures
        "The Siren's Song,   Sail to an uncharted island plagued by shipwrecks and a mysterious song.",
        "The Coral Throne,   Broker peace between rival aquatic kingdoms beneath the waves.",
        "The Ghost Fleet of Blackwater Bay,   Track down ghostly pirate ships terrorizing coastal villages.",
        "The Lighthouse of Eternal Dawn,   Investigate an abandoned lighthouse that still emits light.",
        "The Leviathan's Wake,   Survive an encounter with a colossal sea monster awakening from the depths.",
        # Otherworldly and Exotic Adventures
        "The Shard of Infinity,   Explore a floating island in the Astral Sea guarding a powerful artifact.",
        "The Dreamscape of the Sleeping God,   Enter a shared dreamworld to rescue those trapped in a god's mind.",
        "The Obsidian Spire,   Climb a blackened tower guarded by strange constructs and alien riddles.",
        "The Sands of Time,   Unravel a temporal anomaly in a desert temple with unpredictable time flows.",
        "The Verdant Dominion,   Survive a jungle overrun by sentient plants ruled by a treant king.",
    ]

    topic = random.choice(adventure_titles)

    story_title = topic.split(",")[0]
    story.story_title = story_title

    init_prompt = Prompt()
    init_prompt.add_role_tag("system")
    init_prompt.add_instruction(
        f"{BEGINNING_INSTRUCTION} {topic} Don't speak from gamemaster perspective, Only tell the story beginning."
    )
    init_prompt.add_role_tag("user")
    init_prompt.add_instruction(
        "Start the story please. Only outline, no call to action yet."
    )
    init_prompt.add_role_tag("assistant")

    # res = story.send(init_prompt)
    story.prompts.append(init_prompt)
    return init_prompt, topic.split(",")[0]


def answer_chapter(story: DNDGameMaster, text):
    chapter_prompt = story.prompts[story.chapter_number]
    chapter_prompt.add_role_tag("user")
    chapter_prompt.add_instruction(text)


def extract_score(model_answer: str) -> int:
    """
    Extracts the score from the model's function call response.

    Args:
        model_answer (str): The model's response containing a function call.

    Returns:
        int: The extracted score. Returns -1 if the score is not found or parsing fails.
    """
    try:
        # Find the JSON payload within the model's response
        match = re.search(
            r"<function=submit_quality_assessment>(.*?)</function>", model_answer
        )
        if not match:
            raise ValueError("Function call format not found.")

        # Extract JSON string and parse it
        print(f"EXTRACTED: {match.group(1)}")
        payload = json.loads(match.group(1))
        return payload.get("score", -1)
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Error extracting score: {e}")
        return -1


def evaluate_quality(story: DNDGameMaster, quality: str):

    chapter_prompt = story.prompts[story.chapter_number]

    eval_prompt = Prompt()
    eval_prompt.add_role_tag("system")

    eval_prompt.add_instruction(EVAL_INSTRUCTION)
    eval_prompt.add_role_tag("user")
    eval_prompt.add_instruction(f"Assess my previous answer for quality: {quality}")
    eval_prompt.add_role_tag("assistant")

    combined_prompt = chapter_prompt + eval_prompt

    # res = story.send(combined_prompt, temperature=0.2, top_p=20, top_k=20)
    return combined_prompt
    # story.logger.info(f"MODEL EVALUATION of quality: {quality}, {res['answer']}")
    # score = extract_score(res["answer"])
    # story.update_qualities(quality, score)
    # return res


def end_story(story: DNDGameMaster):
    end_prompt = Prompt()
    end_prompt.add_role_tag("system")
    end_prompt.add_instruction(ENDING_INSTRUCTION)
    end_prompt.add_role_tag("user")

    end_prompt.add_instruction(
        "Please come up with a story ending, that will reflect my choices. It should unveil the secret."
    )
    end_prompt.add_role_tag("assistant")

    story.prompts.append(end_prompt)
    total_prompt = sum(story.prompts, Prompt())

    # res = story.send(total_prompt)

    return total_prompt


if __name__ == "__main__":
    story = DNDGameMaster(1)
    prompt = init_story(story)
    print(prompt.get_prompt())
    answer_chapter(story, "I'm a software engineer")
    print("--------------------------------")
    prompt = continue_story(story)
    answer_chapter(story, "I'm a software engineer")
    print(prompt.get_prompt())
