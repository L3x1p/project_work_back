# Testing LLM Integration Guide

## Prerequisites

1. **Backend server** running on `http://localhost:8000`
2. **LLM service** running on `http://localhost:8002` (your LLaMA Chat API)

## Setting Environment Variables in PowerShell

In PowerShell, use `$env:` instead of `export`:

```powershell
# Set the LLM API URL (optional, defaults to http://localhost:8002)
$env:LLAMA_CHAT_API_URL = "http://localhost:8002"

# Verify it's set
echo $env:LLAMA_CHAT_API_URL
```

**Note:** This setting only lasts for the current PowerShell session. To make it permanent, you can:
- Add it to your PowerShell profile
- Or set it in your system environment variables
- Or create a `.env` file (if using python-dotenv)

## Testing Methods

### Method 1: Using the Test Script (Recommended)

```powershell
# Make sure both servers are running, then:
python test_pdf_endpoint.py test.pdf
```

This will:
- Check if both servers are running
- Extract text from the PDF
- Send it to the LLM service for career analysis
- Display the results

### Method 2: Using curl (PowerShell)

```powershell
# Test with a PDF file
curl -X POST "http://localhost:8000/extract-text" `
  -F "file=@test.pdf" `
  | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Method 3: Using Python Requests Directly

```python
import requests

# Test the endpoint
with open('test.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/extract-text',
        files={'file': f},
        timeout=120  # LLM processing may take time
    )
    
data = response.json()
print(f"Career Fields: {data.get('career_fields', [])}")
print(f"Summary: {data.get('overall_summary', '')}")
```

### Method 4: Using the Frontend (if available)

If you have the frontend running, you can upload a PDF through the web interface at `index.html`.

## Expected Response Format

```json
{
  "filename": "resume.pdf",
  "pages": 2,
  "characters": 1234,
  "career_fields": [
    {
      "field": "Software Engineering",
      "summary": "Strong technical background in programming...",
      "key_skills_mentioned": ["Python", "JavaScript", "React"]
    },
    {
      "field": "Data Science",
      "summary": "Experience with data analysis and machine learning...",
      "key_skills_mentioned": ["Python", "SQL", "Pandas"]
    }
  ],
  "overall_summary": "Candidate shows strong technical skills..."
}
```

## Troubleshooting

### Error: "Cannot connect to LLM service"
- Make sure the LLaMA Chat API is running on port 8002
- Check: `curl http://localhost:8002/health`

### Error: "Failed to parse JSON response"
- The LLM might have returned extra text. Check the `raw_response` field in the error.
- Try adjusting the prompt or temperature settings.

### Timeout Errors
- LLM processing can take 30-60 seconds. Increase timeout in your client.
- Check if the LLM service is responding: `curl http://localhost:8002/health`

### Empty Career Fields
- The PDF might not have enough information
- The LLM might need better prompting
- Check the `error` field in the response for details

## Quick Health Check

```powershell
# Check backend
curl http://localhost:8000/

# Check LLM service
curl http://localhost:8002/health

# Both should return 200 OK
```

