"""
Service for summarizing a person's main potential career fields from text using LLM.
Uses the LLLM Chat API microservice running on localhost:8002
"""
import os
import json
import re
import httpx
from typing import Optional

# LLM Chat API base URL
#LLM_CHAT_API_URL = os.getenv("LLM_CHAT_API_URL", "http://25.22.135.242:8002")
LLM_CHAT_API_URL = os.getenv("LLM_CHAT_API_URL", "http://localhost:8002")

CAREER_FIELD_SUMMARIZER_INSTRUCTION = """You are a Career Analysis Assistant.
Your task is to analyze the provided text about a person and identify their main potential career fields.

Based on the text, you should:
1. Identify the person's skills, interests, experiences, and personality traits mentioned
2. Determine 3-5 main potential career fields that align with their profile
3. Provide a brief summary for each career field explaining why it fits
4. Focus on specific, actionable career fields rather than vague categories

AVOID generic fields like "Management", "Technology", "Business", "Creative" - be more specific.
Instead, suggest concrete fields like "Software Engineering", "Digital Marketing", "Data Science", "UX Design", etc.

Your response should be in the following JSON format:
{
  "career_fields": [
    {
      "field": "specific_career_field_1",
      "summary": "brief explanation of why this field fits the person",
      "key_skills_mentioned": ["skill1", "skill2"]
    },
    {
      "field": "specific_career_field_2",
      "summary": "brief explanation of why this field fits the person",
      "key_skills_mentioned": ["skill1", "skill2"]
    }
  ],
  "overall_summary": "A brief overall summary of the person's career potential"
}

Return ONLY valid JSON, no additional text."""

def _extract_first_json_object(text: str) -> Optional[str]:
    """
    Extract the first top-level JSON object from a string using brace balancing.
    This is more robust than regex when the model returns extra text or multiple JSON blobs.
    """
    if not text:
        return None
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        else:
            if ch == '"':
                in_string = True
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None


async def summarize_career_fields(text: str) -> dict:
    """
    Analyze text about a person and summarize their main potential career fields using LLM Chat API.
    
    Parameters:
      text (str): Text containing information about the person (e.g., resume, bio, description)
    
    Returns:
      dict: A dictionary containing career fields and summary, or error information
    """
    if not text or not text.strip():
        return {
            "error": "No text provided",
            "career_fields": [],
            "overall_summary": ""
        }
    
    # Build the prompt message for the LLM Chat API
    prompt_message = f"""{CAREER_FIELD_SUMMARIZER_INSTRUCTION}

Analyze the following text and identify potential career fields:

{text}"""
    
    try:
        # Call the LLM Chat API
        async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=10.0)) as client:
            try:
                response = await client.post(
                    f"{LLM_CHAT_API_URL}/chat",
                    json={
                        "message": prompt_message,
                        "temperature": 0.7,
                        "max_tokens": 800,
                        "top_p": 0.9
                    },
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                result = response.json()
            except httpx.ConnectError as e:
                return {
                    "error": f"Cannot connect to LLM service at {LLM_CHAT_API_URL}/chat. Connection refused. Is the service running? Error: {str(e)}",
                    "career_fields": [],
                    "overall_summary": ""
                }
            except httpx.TimeoutException as e:
                return {
                    "error": f"Timeout connecting to LLM service at {LLM_CHAT_API_URL}. The request took longer than 60 seconds.",
                    "career_fields": [],
                    "overall_summary": ""
                }
        
        # Extract the response text
        answer_text = result.get("response", "").strip()
        
        if not answer_text:
            return {
                "error": "Empty response from LLM service",
                "career_fields": [],
                "overall_summary": ""
            }
        
        # Try to extract the first JSON object from the response (in case there's extra text)
        extracted_json = _extract_first_json_object(answer_text)
        if extracted_json:
            answer_text = extracted_json
        
        # Parse JSON
        try:
            parsed_result = json.loads(answer_text)
            # Ensure the result has the expected structure
            if "career_fields" not in parsed_result:
                parsed_result["career_fields"] = []
            if "overall_summary" not in parsed_result:
                parsed_result["overall_summary"] = ""
            
            # Ensure each career field has the expected structure
            for field in parsed_result.get("career_fields", []):
                if "key_skills_mentioned" not in field:
                    field["key_skills_mentioned"] = []
            
            return parsed_result
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return the raw text with error info
            return {
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": answer_text,
                "career_fields": [],
                "overall_summary": ""
            }
            
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error from LLM service: {e.response.status_code} - {e.response.text}",
            "career_fields": [],
            "overall_summary": ""
        }
    except httpx.RequestError as e:
        error_details = str(e) if str(e) else f"{type(e).__name__}"
        return {
            "error": f"Request error connecting to LLM service: {error_details}. Make sure the LLM Chat API is running on {LLM_CHAT_API_URL} and accessible. Check if the service is responding to POST requests at {LLM_CHAT_API_URL}/chat",
            "career_fields": [],
            "overall_summary": ""
        }
    except httpx.TimeoutException as e:
        return {
            "error": f"Timeout connecting to LLM service at {LLM_CHAT_API_URL}. The request took longer than 60 seconds. The LLM service might be overloaded or slow.",
            "career_fields": [],
            "overall_summary": ""
        }
    except Exception as e:
        return {
            "error": f"Error generating career summary: {str(e)}",
            "career_fields": [],
            "overall_summary": ""
        }

