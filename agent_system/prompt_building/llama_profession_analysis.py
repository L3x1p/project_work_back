from agent_system.prompt_building.prompt_builder import Prompt
from agent_system.prompt_building.instructions import SUGGEST_PROFESSION_INSTRUCTION
from typing import Optional, Dict, Any
from agent_system.vllm_connection import generate


def parse_model_response(text):
    """
    Converts structured text into a custom JSON format.

    Args:
        text (str): The input text in structured format.

    Returns:
        dict: JSON-formatted dictionary.
    """
    try:
        print(f"MODEL ANSWER: {text}")
        # Parse the text into a Python object
        data = eval(text)

        # Transform the data into the required structure
        transformed_data = {"professions": []}

        for item in data:
            profession_name = f"{item['profession']} at {item['field']}"
            justification = item["justification"]
            isco_code = item["isco_code"]
            transformed_data["professions"].append(
                {
                    "profession_name": f"{profession_name}",
                    "justification": f"{justification}",
                    "isco_code": f"{isco_code}",
                }
            )
        print(f"PARSED DATA: {transformed_data}")
        return transformed_data
    except Exception as e:
        return {"error": str(e)}


async def llama_analysis(
    reddit_data: Optional[str] = None,
    youtube_data: Optional[str] = None,
    traits: Optional[Dict[str, float]] = None,
    isco_classification_data: Optional[Dict[str, Any]] = None,
    reflection_text: Optional[str] = None,
):
    choose_profession_prompt = Prompt()
    choose_profession_prompt.add_role_tag("system")
    suggestion_1 = f"{isco_classification_data['professions'][0]['profession_name']}, user demonstrated: {isco_classification_data['professions'][0]['qualities']}, ISCO_code: {isco_classification_data['professions'][0]['isco_code']}"
    suggestion_2 = f"{isco_classification_data['professions'][1]['profession_name']}, user demonstrated: {isco_classification_data['professions'][1]['qualities']}, ISCO_code: {isco_classification_data['professions'][1]['isco_code']}"
    suggestion_3 = f"{isco_classification_data['professions'][2]['profession_name']}, user demonstrated: {isco_classification_data['professions'][2]['qualities']}, ISCO_code: {isco_classification_data['professions'][2]['isco_code']}"
    choose_profession_prompt.add_instruction(
        SUGGEST_PROFESSION_INSTRUCTION.format(
            profession_1_suggestion=suggestion_1,
            profession_2_suggestion=suggestion_2,
            profession_3_suggestion=suggestion_3,
        )
    )
    choose_profession_prompt.add_role_tag("user")

    instructions = []
    if reddit_data is not None:
        instructions.append(f"Reddit Data:\n{reddit_data}\n")

    if youtube_data is not None:
        instructions.append(f"YouTube Data:\n{youtube_data}\n")

    if traits is not None:
        formatted_traits = "\n".join(
            [f"{key}: {value}/6" for key, value in traits.items()]
        )
        instructions.append(f"Traits Evaluation (Scale 0-6):\n{formatted_traits}\n")

    if reflection_text is not None:
        instructions.append(f"Reflection Text:\n{reflection_text}\n")

    instructions.append(
        "Based on the given inputs, analyze my strengths, areas of improvement, and suggest potential job roles.\n..."
    )
    user_instruction = "Here is data about me:\n" + "\n".join(instructions)

    # print(f"USER INSTRUCTION: {user_instruction}")
    choose_profession_prompt.add_instruction(user_instruction)
    choose_profession_prompt.add_role_tag("assistant")

    max_retries = 4
    retry_count = 0
    initial_temperature = 0.8
    final_dict = {"error": "Failed to parse response"}
    while retry_count < max_retries:
        current_temperature = max(initial_temperature - retry_count*0.1, 0.4)
        res = await generate(
            choose_profession_prompt,
            max_new_tokens=700,
            temperature=current_temperature,
        )
        # print(f"MODEL ANSWER with temperature {current_temperature}: {res['answer']}")
        final_dict = parse_model_response(res["answer"])
        if "error" not in final_dict:
            break  # Successfully parsed, exit loop.
        retry_count += 1
    return final_dict


if __name__ == "__main__":
    # Example usage
    reddit_data_example = "User has been active on career-related subreddits, frequently discussing leadership and problem-solving topics."
    traits_example = {
        "Commitment": 4.5,
        "Entrepreneurial Spirit": 5.0,
        "Authority": 3.8,
        "Recognition": 4.2,
        "Achievement": 5.5,
    }

    isco_classification_data_example = {
        "professions": [
            {
                "ISCO Code": "61",
                "name": "Market-oriented Skilled Agricultural Workers",
                "qualities": [
                    "Result Orientation",
                    "Risk Tolerance",
                    "Entrepreneurialism",
                ],
                "total_scrore": 9.583333333333332,
            },
            {
                "ISCO Code": "62",
                "name": "Market-oriented Skilled Forestry, Fishery and Hunting Workers",
                "qualities": [
                    "Risk Tolerance",
                    "Emotional Stability",
                    "Entrepreneurialism",
                ],
                "total_scrore": 9.25,
            },
            {
                "ISCO Code": "63",
                "name": "Subsistence Farmers, Fishers, Hunters and Gatherers",
                "qualities": [
                    "Risk Tolerance",
                    "Emotional Stability",
                    "Entrepreneurialism",
                ],
                "total_scrore": 9.25,
            },
        ]
    }
    reflection_text_example = "I am a highly motivated individual who values creativity and leadership. I enjoy taking initiative and working on projects that challenge me to think outside the box."

    result = llama_analysis(
        reddit_data=None,
        youtube_data=None,
        traits=None,
        isco_classification_data=isco_classification_data_example,
        reflection_text=None,
    )
    import json

    print(json.dumps(result, indent=4, sort_keys=True))
