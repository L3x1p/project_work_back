"""Quick test script to debug LLM service connection"""
import asyncio
import httpx
import os

#LLAMA_CHAT_API_URL = os.getenv("LLAMA_CHAT_API_URL", "http://25.22.135.242:8002")
LLAMA_CHAT_API_URL = os.getenv("LLAMA_CHAT_API_URL", "http://localhost:8002")

async def test_connection():
    print(f"Testing connection to {LLAMA_CHAT_API_URL}")
    
    # Test 1: Health check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{LLAMA_CHAT_API_URL}/health")
            print(f"✅ Health check: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Chat endpoint
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0)) as client:
            print(f"\nTesting POST to {LLAMA_CHAT_API_URL}/chat")
            response = await client.post(
                f"{LLAMA_CHAT_API_URL}/chat",
                json={
                    "message": "Hello, this is a test",
                    "temperature": 0.7,
                    "max_tokens": 100,
                    "top_p": 0.9
                },
                headers={"Content-Type": "application/json"}
            )
            print(f"✅ Chat endpoint: {response.status_code}")
            print(f"   Response: {response.json()}")
    except httpx.ConnectError as e:
        print(f"❌ Connection error: {e}")
        print(f"   Cannot connect to {LLAMA_CHAT_API_URL}/chat")
        print(f"   Make sure the service is running and accessible")
    except httpx.TimeoutException as e:
        print(f"❌ Timeout error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP error: {e.response.status_code}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())

