from agent_system.vllm_connection import generate
from agent_system.prompt_building.prompt_builder import Prompt
from agent_system.prompt_building.instructions import (
    YOUTUBE_KEYWORDS_SUMMARIZER_INSTRUCTION,
)


async def summarize_youtube_keywords(
    youtube_subscriptions: str,
) -> dict:
    """
    Analyze YouTube subscription channel names to extract keywords and summarize interests.

    This function builds a prompt using the instruction defined in YOUTUBE_KEYWORDS_SUMMARIZER_INSTRUCTION,
    adds the YouTube subscriptions as user input, and then calls generate() to perform the summarization.

    Parameters:
      youtube_subscriptions (str): A text containing the names (or list) of YouTube subscriptions.
      max_new_tokens (int): Maximum number of new tokens to generate (default is 300).

    Returns:
      dict: A JSON-parsed dictionary containing two keys:
             "keywords" - a list of strings,
             "summary"  - a string summarizing the interests.
    """
    prompt_obj = Prompt()
    # Set the system instruction for summarizing YouTube keywords.
    prompt_obj.add_role_tag("system")
    prompt_obj.add_instruction(YOUTUBE_KEYWORDS_SUMMARIZER_INSTRUCTION)

    # Add the YouTube subscriptions content as the user message.
    prompt_obj.add_role_tag("user")
    prompt_obj.add_instruction(f"Subscriptions:\n{youtube_subscriptions}")

    # Set the assistant role so the model responds.
    prompt_obj.add_role_tag("assistant")

    # Generate output using the vLLM connection.
    result = await generate(prompt_obj)
    print(result["answer"])
    return result["answer"]
