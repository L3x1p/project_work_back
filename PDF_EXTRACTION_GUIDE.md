# PDF Text Extraction Guide

## Overview

The API now includes a PDF text extraction endpoint that processes PDF files and returns the extracted text. No storage - just process and return!

## API Endpoint

### POST `/extract-text`

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file in `file` field

**Response:**
```json
{
  "filename": "document.pdf",
  "text": "Extracted text content...",
  "pages": 5,
  "characters": 1234
}
```

**Error Response:**
```json
{
  "detail": "Error message here"
}
```

## Usage Examples

### Using cURL

```bash
curl -X POST "http://localhost:8000/extract-text" \
  -F "file=@/path/to/document.pdf"
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/extract-text"
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    data = response.json()
    print(data["text"])
```

### Using JavaScript/Fetch

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/extract-text', {
    method: 'POST',
    body: formData
});

const data = await response.json();
console.log(data.text);
```

## Web UI

A beautiful HTML interface is provided in `index.html` for easy testing.

### To use the web UI:

1. **Start your FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```

2. **Open the HTML file:**
   - Simply double-click `index.html` in your file browser
   - Or open it in a web browser
   - The UI will connect to `http://localhost:8000`

3. **Features:**
   - Drag & drop PDF files
   - Click to browse files
   - Real-time extraction
   - Copy extracted text to clipboard
   - Shows file info and statistics

## Installation

Make sure you have the required dependency:

```bash
pip install pdfplumber
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## How It Works

1. **Client uploads PDF** → Server receives file as `multipart/form-data`
2. **Server reads file** → Loads PDF into memory (BytesIO)
3. **Extract text** → Uses `pdfplumber` to extract text from all pages
4. **Return text** → Sends extracted text as JSON response
5. **Clean up** → File is discarded (no storage)

## Limitations

- **Scanned PDFs**: If a PDF contains only images (scanned documents), no text will be extracted. You'd need OCR (Optical Character Recognition) for those.
- **File size**: Very large PDFs might take longer to process
- **Memory**: Large PDFs are loaded into memory

## Error Handling

The endpoint handles:
- ✅ Invalid file types (non-PDF files)
- ✅ Empty or corrupted PDFs
- ✅ PDFs with no extractable text
- ✅ Server errors

## Testing

1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

2. Open `index.html` in your browser

3. Upload a PDF and see the extracted text!

## Notes

- Files are **not stored** on the server
- Processing happens **in memory**
- No database required for this feature
- Perfect for one-off conversions and quick tools


