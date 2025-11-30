from agent_system.prompt_building.game_master import DNDGameMaster
from sqlalchemy.orm import Session
from postgres_db.models import UserTrait, JobOrientationResult, Adventure
from agent_system.prompt_building.llama_profession_analysis import llama_analysis

import os
import csv
from fastapi import HTTPException
from agent_system.social_network.data_parser import get_reddit_data, get_youtube_data
from agent_system.quality_evaluation.youtube_keywords_summarizer_agent import (
    summarize_youtube_keywords,
)

# Load all ISCO categories from CSV on module load
ISOCSV_PATH = os.path.join(os.path.dirname(__file__), "ISCO_categories.csv")
all_categories = []
try:
    with open(ISOCSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            all_categories.append(
                {
                    "ISCO Code": row["ISCO Code"].strip(),
                    "Name": row["Name"].strip(),
                    "Qualities": (
                        [q.strip() for q in row["Qualities"].split(",")]
                        if row["Qualities"]
                        else []
                    ),
                }
            )
except Exception as e:
    print(f"Error loading ISCO_categories.csv: {e}")

# Separate first-level and second-level categories.
first_level_categories = [cat for cat in all_categories if len(cat["ISCO Code"]) == 1]
second_level_categories = [cat for cat in all_categories if len(cat["ISCO Code"]) > 1]

# Group second-level categories by their parent (first-level) code.
second_level_group = {}
for cat in second_level_categories:
    parent_code = cat["ISCO Code"][0]  # assumes parent's code is the first character
    second_level_group.setdefault(parent_code, []).append(cat)


def get_best_fit_second_level_categories(
    user_id: int, db: Session, user_trait_avgs=None
):
    """
    Query the UserTrait record for the user and, using the loaded ISCO categories,
    compute a matching score for each second-level category based on the user's trait scores.
    Returns the top 3 best-fit categories with their computed scores.
    """
    if user_trait_avgs is None:
        user_traits = db.query(UserTrait).filter(UserTrait.user_id == user_id).first()
        if not user_traits:
            raise HTTPException(status_code=404, detail="User traits not found")

        # Compute average for each user trait (assumes each value is a list of numbers)
        user_trait_avgs = {}
        for trait, scores in user_traits.trait_json.items():
            user_trait_avgs[trait] = sum(scores) / len(scores) if scores else 0
    else:
        user_trait_avgs = user_trait_avgs

    # First, for each first-level category compute an average score based on its Qualities.
    first_scores = []
    for cat in first_level_categories:
        qualities = cat.get("Qualities", [])
        print(f"User trait avgs: {user_trait_avgs}")
        if qualities:
            score_first = sum(user_trait_avgs.get(q, 0) for q in qualities) / len(
                qualities
            )
        else:
            score_first = 0
        first_scores.append((cat, score_first))
    # Select the top 3 first-level categories.
    best_first_level = sorted(first_scores, key=lambda x: x[1], reverse=True)[:3]

    paths = []
    # For each best first-level category, examine its second-level children.
    for first_cat, score_first in best_first_level:
        # Get children whose parent code matches the first-level category's ISCO Code.
        children = second_level_group.get(first_cat["ISCO Code"], [])
        second_scores = []
        for child in children:
            quals = child.get("Qualities", [])
            if quals:
                score_second = sum(user_trait_avgs.get(q, 0) for q in quals) / len(
                    quals
                )
            else:
                score_second = 0
            second_scores.append((child, score_second))
        # Select top 3 second-level categories for the current first-level category.
        best_children = sorted(second_scores, key=lambda x: x[1], reverse=True)[:3]
        for child, score_second in best_children:
            total = round((score_first + score_second) / 2, 2)
            paths.append(
                {
                    "first_level": {**first_cat, "score": score_first},
                    "second_level": {**child, "score": score_second},
                    "total_score": total,
                }
            )

    # Out of the (up to) 9 paths, select the top 3 by total score.
    final_result = sorted(paths, key=lambda x: x["total_score"], reverse=True)[:3]
    final_professions = []
    for path in final_result:
        second = path["second_level"]
        isco_code = second["ISCO Code"]
        final_professions.append(
            {
                "isco_code": isco_code,
                "profession_name": second["Name"],
                "qualities": second["Qualities"],
                "total_score": path["total_score"],
            }
        )
    return {"professions": final_professions}


def update_job_orientation(story: DNDGameMaster, db: Session, user_id: int):
    user_traits = db.query(UserTrait).filter(UserTrait.user_id == user_id).first()
    user_traits.trait_json = story.qualities
    db.commit()


async def create_job_orientation_results(
    story: DNDGameMaster, db: Session, user_id: int
):

    # condition to check if all qualities inside story.qualities have at least 4 scores
    # Example usage of get_reddit_data
    reddit_data_str = get_reddit_data(user_id, db)
    # print(reddit_data_str)  # This will print the formatted Reddit data string

    # Example usage of get_youtube_data
    youtube_keywords = get_youtube_data(user_id, db)
    youtube_keywords_summary = await summarize_youtube_keywords(youtube_keywords)
    # print(youtube_data_str)  # This will print the formatted YouTube data string

    if all(len(scores) >= 2 for scores in story.qualities.values()):
        isco_classification_data = get_best_fit_second_level_categories(user_id, db)

        # Call llama_analysis function with YouTube data
        analysis_results = await llama_analysis(
            reddit_data=reddit_data_str,
            youtube_data=youtube_keywords_summary,  # Pass YouTube data
            isco_classification_data=isco_classification_data,
            reflection_text=None,
        )

        # Process the results and store them in the database
        print("ANALYSIS RESULTS:", analysis_results)
        for result in analysis_results.get("professions", []):
            job_orientation_result = JobOrientationResult(
                name=result["profession_name"],
                profession=True,
                parent_adventure_id=story.story_id,
                description=result["justification"],
                isco_code=result["isco_code"],
                # score from isco_classification_data where isco_code matches
                score=next(
                    (
                        item["total_score"]
                        for item in isco_classification_data.get("professions", [])
                        if item["isco_code"] == result["isco_code"]
                    ),
                    None,
                ),
            )
            db.add(job_orientation_result)

        db.commit()
    else:
        # create qulity based results
        results_number = 3
        # calculate top 3 qualities
        top_qualities = sorted(
            story.qualities, key=lambda x: sum(story.qualities[x]), reverse=True
        )[:results_number]

        for quality in top_qualities:
            result = JobOrientationResult(
                name=f"{quality}",
                profession=False,
                parent_adventure_id=story.story_id,
            )

            db.add(result)

        db.commit()


async def debug_update_job_orientation_results(
    db: Session,
    user_id: int,
    reddit: bool,
    youtube: bool,
    traits,
):
    """
    Debug function to update the profession-related fields of job orientation results
    for the first adventure (sorted by adventure_id) for a given user.

    This function conditionally retrieves Reddit and YouTube data according to the flags
    provided, and forwards the provided traits dictionary to both the ISCO classification
    and analysis functions. It then overrides all profession-related fields (name,
    justification/description, isco_code, score, and profession flag) in the
    JobOrientationResult records while keeping ID fields (like result_id and
    parent_adventure_id) unchanged. Finally, it returns a dict containing the
    isco_classification_data and the new analysis.
    """
    # Retrieve the first Adventure for the user (sorted by adventure_id)
    first_story = (
        db.query(Adventure)
        .filter(Adventure.user_id == user_id)
        .order_by(Adventure.adventure_id)
        .first()
    )
    if not first_story:
        print(f"No adventure found for user_id {user_id}.")
        return {}

    # Retrieve all JobOrientationResults associated with this adventure
    job_results = (
        db.query(JobOrientationResult)
        .filter(JobOrientationResult.parent_adventure_id == first_story.adventure_id)
        .all()
    )
    if not job_results:
        print(
            f"No job orientation results found for adventure_id {first_story.adventure_id}."
        )
        return {}

    # Conditionally retrieve Reddit data if enabled
    reddit_data_str = get_reddit_data(user_id, db) if reddit else ""

    # Conditionally retrieve YouTube data if enabled
    youtube_keywords_summary = ""
    if youtube:
        youtube_keywords = get_youtube_data(user_id, db)
        youtube_keywords_summary = await summarize_youtube_keywords(youtube_keywords)

    # Retrieve ISCO classification data, passing the traits if provided
    isco_classification_data = get_best_fit_second_level_categories(
        user_id, db, user_trait_avgs=traits
    )

    # Run the analysis with the provided traits
    new_analysis = await llama_analysis(
        reddit_data=reddit_data_str if reddit else None,
        youtube_data=youtube_keywords_summary if youtube else None,
        isco_classification_data=isco_classification_data,
        reflection_text=None,
        traits=traits,
    )
    new_professions = new_analysis.get("professions", [])

    # Use the minimum count to avoid index errors
    update_count = min(len(job_results), len(new_professions))
    if update_count < len(job_results):
        print(
            f"Warning: Mismatch in count. Updating {update_count} out of {len(job_results)} job results."
        )

    for idx in range(update_count):
        job = job_results[idx]
        new_prof = new_professions[idx]

        # Override all profession-related fields
        job.name = new_prof.get("profession_name", job.name)
        job.description = new_prof.get("justification", job.description)
        job.isco_code = new_prof.get(
            "isco_code", job.isco_code
        )  # override isco_code with new value
        new_score = next(
            (
                item.get("total_score")
                for item in isco_classification_data.get("professions", [])
                if item.get("isco_code") == new_prof.get("isco_code")
            ),
            job.score,
        )
        job.score = new_score
        job.profession = True

    db.commit()

    return {
        "isco_classification_data": isco_classification_data,
        "new_analysis": new_analysis,
    }
