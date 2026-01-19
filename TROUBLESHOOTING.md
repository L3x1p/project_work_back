# Troubleshooting PDF Extraction

## Issue: "Nothing happens when I press Extract Text"

### Step 1: Check Browser Console

1. **Open Developer Tools:**
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
   - Or `Cmd+Option+I` (Mac)

2. **Go to Console tab**

3. **Look for errors:**
   - Red errors indicate JavaScript problems
   - Network errors show connection issues

4. **Check the logs:**
   - You should see messages like:
     - "Form submitted"
     - "File selected: ..."
     - "Fetching to: http://localhost:8000/extract-text"

### Step 2: Verify Server is Running

```bash
# Check if server is running
curl http://localhost:8000/

# Or test the endpoint
python test_pdf_endpoint.py
```

### Step 3: Check Server Logs

When you click "Extract Text", you should see a request in your server terminal:
```
INFO:     127.0.0.1:xxxxx - "POST /extract-text HTTP/1.1" 200 OK
```

If you don't see this, the request isn't reaching the server.

### Step 4: Common Issues

#### Issue: CORS Error
**Error:** `Access to fetch at 'http://localhost:8000' from origin 'file://' has been blocked by CORS policy`

**Solution:** 
- The HTML file must be served from a web server, not opened as `file://`
- Use a simple HTTP server:
  ```bash
  # Python 3
  python -m http.server 8080
  
  # Then open: http://localhost:8080/index.html
  ```

#### Issue: Connection Refused
**Error:** `Network error: Failed to fetch`

**Solution:**
- Make sure FastAPI server is running:
  ```bash
  uvicorn main:app --reload
  ```
- Check the server is on port 8000
- Try accessing: http://localhost:8000/docs

#### Issue: Button Not Clickable
**Symptom:** Button is grayed out or doesn't respond

**Solution:**
- Make sure you've selected a PDF file first
- The button should say "Extract Text" (not "Select a PDF first")
- Check browser console for JavaScript errors

#### Issue: 400 Bad Request
**Error:** "File must be a PDF"

**Solution:**
- Make sure you're uploading a `.pdf` file
- Some browsers might not detect PDF type correctly
- Try a different PDF file

#### Issue: 500 Internal Server Error
**Error:** "Error extracting text from PDF"

**Solution:**
- Check if `pdfplumber` is installed:
  ```bash
  pip install pdfplumber
  ```
- Check server logs for detailed error message
- The PDF might be corrupted or password-protected

### Step 5: Manual Testing

Test the endpoint directly:

```bash
# Using curl
curl -X POST "http://localhost:8000/extract-text" \
  -F "file=@your-file.pdf"

# Using Python
python test_pdf_endpoint.py your-file.pdf
```

### Step 6: Check Network Tab

1. Open Developer Tools → **Network** tab
2. Click "Extract Text"
3. Look for a request to `/extract-text`
4. Check:
   - Status code (should be 200)
   - Request payload (should show file)
   - Response (should show JSON with text)

## Quick Fixes

### Fix 1: Serve HTML from HTTP Server

Instead of opening `index.html` directly, serve it:

```bash
# In the project directory
python -m http.server 8080

# Then open: http://localhost:8080/index.html
```

### Fix 2: Update API URL

If your server runs on a different port, update line 401 in `index.html`:

```javascript
const response = await fetch('http://localhost:YOUR_PORT/extract-text', {
```

### Fix 3: Check Dependencies

```bash
pip install -r requirements.txt
```

## Still Not Working?

1. **Check browser console** (F12) for errors
2. **Check server terminal** for request logs
3. **Test endpoint directly** with `test_pdf_endpoint.py`
4. **Verify server is running** on port 8000
5. **Try a different browser** (Chrome, Firefox, Edge)

## Debug Mode

The HTML now includes console logging. Check the browser console to see:
- When form is submitted
- What file is selected
- When request is sent
- What response is received






