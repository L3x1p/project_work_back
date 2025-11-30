# LLaMA Chat API Documentation

## Overview

The LLaMA Chat API is a RESTful service that provides access to a local LLaMA 3.1B model running on your RTX 4070 Super GPU. The service runs on `localhost:8002` and provides endpoints for chat interactions, conversation management, and health monitoring.

## Quick Start

### 1. Start the Service

```bash
python api_service.py
```

Or with a custom model path:
```bash
python api_service.py path/to/model.gguf
```

The service will start on `http://localhost:8002`

### 2. Access API Documentation

Once running, visit:
- **Interactive API Docs**: http://localhost:8002/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8002/redoc (ReDoc)

## API Endpoints

### Base URL
```
http://localhost:8002
```

---

### `GET /`
**Info endpoint**

Returns basic service information.

**Response:**
```json
{
  "service": "LLaMA Chat API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### `GET /health`
**Health check endpoint**

Check if the service and model are ready.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

**Status Codes:**
- `200`: Service is healthy
- `503`: Model not loaded (if `model_loaded: false`)

---

### `POST /chat`
**Send a chat message (non-streaming)**

Send a message and receive a complete response.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "optional-session-id",
  "temperature": 0.7,
  "max_tokens": 512,
  "top_p": 0.9
}
```

**Parameters:**
- `message` (string, required): Your message to the AI
- `session_id` (string, optional): Session ID for conversation history. If not provided, a new session is created and returned.
- `temperature` (float, optional, default: 0.7): Sampling temperature (0.0-2.0). Higher = more creative, Lower = more focused.
- `max_tokens` (int, optional, default: 512): Maximum number of tokens in the response.
- `top_p` (float, optional, default: 0.9): Nucleus sampling parameter (0.0-1.0).

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you for asking. How can I assist you today?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "tokens_used": null
}
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "temperature": 0.7
  }'
```

**Example using Python:**
```python
import requests

response = requests.post(
    "http://localhost:8002/chat",
    json={
        "message": "What is Python?",
        "temperature": 0.7
    }
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Session ID: {data['session_id']}")
```

**Example with session (conversation history):**
```python
import requests

session_id = None

# First message
response = requests.post(
    "http://localhost:8002/chat",
    json={"message": "My name is Alice"}
)
session_id = response.json()["session_id"]

# Follow-up message (maintains context)
response = requests.post(
    "http://localhost:8002/chat",
    json={
        "message": "What's my name?",
        "session_id": session_id
    }
)
print(response.json()["response"])  # Should remember Alice
```

---

### `POST /chat/stream`
**Send a chat message (streaming)**

Send a message and receive a streaming response using Server-Sent Events (SSE).

**Request Body:** (Same as `/chat`)

**Response:** Server-Sent Events stream

**Example using Python:**
```python
import requests
import json

response = requests.post(
    "http://localhost:8002/chat/stream",
    json={"message": "Tell me a short story"},
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            if 'token' in data:
                print(data['token'], end='', flush=True)
            elif 'done' in data:
                print("\n[Stream complete]")
                break
```

**Example using JavaScript (Browser):**
```javascript
const eventSource = new EventSource('http://localhost:8002/chat/stream', {
  method: 'POST',
  body: JSON.stringify({ message: 'Hello!' }),
  headers: { 'Content-Type': 'application/json' }
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.token) {
    console.log(data.token);
  }
};
```

**Note:** For browser-based SSE, you may need to use a library like `fetch` with streaming or a WebSocket alternative, as EventSource only supports GET requests.

---

### `POST /chat/clear`
**Clear conversation history**

Clear the conversation history for a specific session.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "status": "cleared",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8002/chat/clear" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id"}'
```

---

### `GET /sessions`
**List active sessions**

Get a list of all active session IDs.

**Response:**
```json
{
  "sessions": [
    "session-id-1",
    "session-id-2"
  ],
  "count": 2
}
```

---

## Session Management

### How Sessions Work

- Each conversation is tracked by a `session_id`
- If you don't provide a `session_id`, a new one is automatically generated
- Conversation history is maintained for the last 5 exchanges per session
- Sessions are stored in memory (will be lost on server restart)
- Use the same `session_id` across requests to maintain conversation context

### Best Practices

1. **Store the session_id**: Save the `session_id` from the first response to maintain context
2. **Clear when done**: Use `/chat/clear` when starting a new conversation topic
3. **Session limits**: History is limited to 5 exchanges to manage context window

---

## Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
  "detail": "Message cannot be empty"
}
```

**404 Not Found:**
```json
{
  "detail": "Session not found"
}
```

**503 Service Unavailable:**
```json
{
  "detail": "Model not loaded"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Generation error: [error message]"
}
```

---

## Integration Examples

### Python Client Example

```python
import requests

class LLMChatClient:
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.session_id = None
    
    def chat(self, message, temperature=0.7):
        """Send a message and get response"""
        payload = {
            "message": message,
            "temperature": temperature
        }
        if self.session_id:
            payload["session_id"] = self.session_id
        
        response = requests.post(
            f"{self.base_url}/chat",
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        self.session_id = data["session_id"]
        return data["response"]
    
    def clear(self):
        """Clear conversation history"""
        if self.session_id:
            requests.post(
                f"{self.base_url}/chat/clear",
                json={"session_id": self.session_id}
            )
            self.session_id = None

# Usage
client = LLMChatClient()
print(client.chat("Hello!"))
print(client.chat("What did I just say?"))
client.clear()
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

class LLMChatClient {
  constructor(baseUrl = 'http://localhost:8002') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
  }

  async chat(message, temperature = 0.7) {
    const payload = {
      message,
      temperature
    };
    if (this.sessionId) {
      payload.session_id = this.sessionId;
    }

    const response = await axios.post(`${this.baseUrl}/chat`, payload);
    this.sessionId = response.data.session_id;
    return response.data.response;
  }

  async clear() {
    if (this.sessionId) {
      await axios.post(`${this.baseUrl}/chat/clear`, {
        session_id: this.sessionId
      });
      this.sessionId = null;
    }
  }
}

// Usage
const client = new LLMChatClient();
client.chat('Hello!').then(response => console.log(response));
```

### cURL Examples

**Simple chat:**
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain quantum computing"}'
```

**Chat with custom parameters:**
```bash
curl -X POST "http://localhost:8002/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a haiku about AI",
    "temperature": 0.9,
    "max_tokens": 100
  }'
```

---

## Configuration

### Environment Variables

- `MODEL_PATH`: Path to the GGUF model file (default: `qwen2.5-3b-instruct-q4_k_m.gguf`)

### Command Line Arguments

```bash
python api_service.py [model_path]
```

---

## Performance Tips

1. **Temperature**: Lower values (0.3-0.7) for factual responses, higher (0.8-1.2) for creative tasks
2. **Max Tokens**: Adjust based on expected response length (default 512 is usually sufficient)
3. **Session Management**: Clear sessions when switching topics to free memory
4. **Streaming**: Use `/chat/stream` for better user experience with long responses

---

## CORS Configuration

The service is configured to allow CORS from all origins by default. For production, update the CORS settings in `api_service.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Troubleshooting

### Service won't start
- Check if port 8002 is already in use
- Verify the model file exists
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Model not loading
- Verify CUDA is installed: `nvidia-smi`
- Check model file path is correct
- Ensure llama-cpp-python is installed with GPU support

### Slow responses
- Reduce `max_tokens` for shorter responses
- Check GPU utilization with `nvidia-smi`
- Consider using a smaller quantization (Q4 instead of Q5)

### Out of memory
- Reduce `n_ctx` in model loading (currently 4096)
- Use a smaller quantization model
- Clear sessions more frequently

---

## License

This API service is provided as-is for local use.


