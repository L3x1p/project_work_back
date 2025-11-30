import os
from fastapi.responses import StreamingResponse
from agent_system.prompt_building.prompt_builder import Prompt
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the server IP from the environment variable
server_ip = os.getenv("SERVER_IP")

vllm_client = AsyncOpenAI(
    base_url=f"{server_ip}/v1",  # Use the server IP from the environment variable
    api_key="no-key-required",
)


async def generate(
    prompt_obj: Prompt,
    max_new_tokens: int = 500,
    temperature: float = 0.6,
    top_p: float = 0.8,
    stream: bool = False,
    repetition_penalty: float = 1.2,
    top_k: int = 40,
) -> dict:
    """
    Generates text asynchronously based on the provided prompt.

    Parameters:
      prompt_obj: Prompt object with the current conversation history.
      url: API endpoint to send the request (placeholder, not used in this example).
      max_new_tokens: Maximum number of new tokens to generate.
      temperature: Sampling temperature.
      top_k: Top_k sampling parameter.
      top_p: Top_p (nucleus) sampling parameter.
      repetition_penalty: Penalty for token repetition.
      stream: Whether to stream the response or return it fully.

    Returns:
      If stream=True: A StreamingResponse that streams the generated text.
      Otherwise: A dictionary with keys "answer", "prompt_in", and "prompt_out".

    This function is designed to work in a future version replacing the send() method.
    """
    # Prepare the input prompt using your Prompt object
    prompt_in = prompt_obj.get_prompt()

    # Construct the payload for text completion
    payload = {
        "model": "meta-llama/Llama-3.1-8B-Instruct",  # Replace with your model name if needed
        "prompt": prompt_in,
        "max_tokens": max_new_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": stream,
    }

    # For streaming responses, return a StreamingResponse that yields chunks of text.
    if stream:

        async def generate_stream():
            # Request stream from vLLM API using async call
            stream_response = await vllm_client.completions.create(**payload)
            async for chunk in stream_response:
                if hasattr(chunk.choices[0], "text") and chunk.choices[0].text:
                    yield chunk.choices[0].text

        return StreamingResponse(generate_stream(), media_type="text/plain")
    else:
        # Non-streaming call: retrieve the full response asynchronously
        response = await vllm_client.completions.create(**payload)
        full_text = response.choices[0].text
        return {
            "answer": full_text,
            "prompt_in": prompt_in,
            "prompt_out": prompt_obj.get_prompt(),
        }
