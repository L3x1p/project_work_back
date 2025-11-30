from agent_system.prompt_building.prompt_builder import Prompt
import logging
from logging import Formatter
import random


class DNDGameMaster:
    def __init__(self, story_id, story_title=""):
        self.prompts: list[Prompt] = list()
        self.chapter_number = 0
        self.max_chapters = 10
        self.story_id = story_id  # Will be updated when loading the record from DB
        self.qualities_to_assess = []
        self.story_title = story_title

        # Setup logging
        self.logger = logging.getLogger("DNDGameMaster")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:  # Prevent duplicate handlers
            # Create file handler for logging to a file
            file_handler = logging.FileHandler("game_log.txt", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            # Create console handler for logging to the console
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # Define a formatter
            formatter = Formatter(
                fmt="%(name)s - %(levelname)s - %(message)s",
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Add handlers to the logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        self.qualities: dict[str, list[int]] = {
            "Entrepreneurialism": [],
            "Drive for Power": [],
            "Result Orientation": [],
            "Creativity": [],
            "Risk Tolerance": [],
            "Leadership": [],
            "Teamwork": [],
            "Extroversion": [],
            "Attention to Detail": [],
            "Emotional Stability": [],
            "Ethical Guidelines": [],
        }

        # Disable propagation to avoid duplicate logs
        self.logger.propagate = False

    def load_story_data(
        self,
        prompts: list[Prompt],
        max_chapters: int,
        qualities: dict[str, list[int]],
        qualities_to_assess: list[str],
        story_title: str,
    ):
        self.prompts = prompts
        self.max_chapters = max_chapters
        self.qualities = qualities
        self.chapter_number = len(prompts) - 1
        self.qualities_to_assess = qualities_to_assess
        self.story_title = story_title

        # self.logger.info(
        #     f"INITIALIZED STORY WITH CURRENT CHAPTER NUMBER: {self.chapter_number}"
        # )

    def update_qualities(self, quality: str, score: int):
        self.qualities[quality].append(score)
        self.logger.info(f"Qualities updated: {quality} with score: {score}")

    def get_least_assessed_quality(self) -> str:
        """
        Find the quality with the fewest assessments so far.
        If there's a tie, it picks one at random.
        """
        # Sort by length of the list of scores
        qualities_by_count = sorted(self.qualities.items(), key=lambda x: len(x[1]))
        # Get how many have the minimal count
        min_count = len(qualities_by_count[0][1])
        # Filter out all with the same min count
        least_assessed = [
            q for q, scores in qualities_by_count if len(scores) == min_count
        ]
        # Pick at random among the least assessed
        return random.choice(least_assessed)
