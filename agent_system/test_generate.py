import asyncio
import httpx

# async def test_non_stream_response():
#     async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
#         # Prepare the payload according to the InitStoryRequest schema
#         payload = {"user_id": 1}
#         # Make a POST request to create a new story and get the full response
#         response = await client.post("story/stories/", json=payload)
#         print("Status Code:", response.status_code)

#         # Retrieve the story_id from the response headers
#         story_id = response.headers.get("story_id")
#         print(f"Created story with ID: {story_id}")

#         # Get the full story content from the response body
#         story_content = response.text
#         print("Story content:")
#         print(story_content)


# async def test_init_story_endpoint():
#     async with httpx.AsyncClient(base_url="https://sc2.galaxyadvisors.com/api", timeout=60.0) as client:
#         # Prepare the login payload
#         login_payload = {"email": "123@test.com", "password": "123"}
#         # Make a POST request to the login endpoint
#         login_response = await client.post("/auth/login/", json=login_payload)
#         print("Login Status Code:", login_response.status_code)

#         # Check if login was successful
#         if login_response.status_code == 200:
#             print("Login successful")
#             # Extract access_token from login response
#             access_token = login_response.json().get("access_token")
#             if not access_token:
#                 print("Access token not found in login response")
#                 return
#         else:
#             print("Login failed")
#             return

#         # Prepare the payload according to the InitStoryRequest schema
#         cookies = {"access_token": access_token}
#         # Make a POST request to create a new story and stream the response
#         async with client.stream(
#             "POST", "/story/stories/", cookies=cookies
#         ) as response:
#             print("Status Code:", response.status_code)

#             # Retrieve the story_id from the response headers
#             story_id = response.headers.get("story_id")
#             print(f"Created story with ID: {story_id}")

#             # Stream the story content from the response body
#             print("Streaming story content:")
#             async for chunk in response.aiter_text():
#                 print(chunk, end="", flush=True)


async def test_answer_story_endpoint():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # Prepare the login payload
        login_payload = {"email": "nik4zerg@gmail.com", "password": "123"}
        # Make a POST request to the login endpoint
        login_response = await client.post("/auth/login/", json=login_payload)
        print("Login Status Code:", login_response.status_code)

        # Check if login was successful
        if login_response.status_code == 200:
            print("Login successful")
            # Extract access_token from login response
            access_token = login_response.json().get("access_token")
            if not access_token:
                print("Access token not found in login response")
                return
        else:
            print("Login failed")
            return

        # Prepare the payload for the answer_story endpoint
        answer_payload = {
            "story_id": 20,  # Replace with the actual story_id you want to test
            "answer_text": "Run away!",
        }
        cookies = {"access_token": access_token}

        # Make a PUT request to the answer_story endpoint
        async with client.stream(
            "PUT", "story/stories/{story_id}", json=answer_payload, cookies=cookies
        ) as response:
            print("Status Code:", response.status_code)

            # Stream the story content from the response body
            print("Streaming story content:")
            async for chunk in response.aiter_text():
                print(chunk, end="", flush=True)


if __name__ == "__main__":
    # asyncio.run(test_init_story_endpoint())
    asyncio.run(test_answer_story_endpoint())
