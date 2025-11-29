"""
Simple test script to verify the PDF extraction endpoint works
Run this to test if the server endpoint is working correctly
"""

import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint():
    """Test if the endpoint is accessible"""
    print("Testing PDF extraction endpoint...")
    print(f"Server URL: {BASE_URL}")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server!")
        print("   Make sure the server is running: uvicorn main:app --reload")
        return False
    
    # Test 2: Try to access endpoint without file (should fail)
    try:
        response = requests.post(f"{BASE_URL}/extract-text")
        print(f"✅ Endpoint exists (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Error accessing endpoint: {e}")
        return False
    
    # Test 3: Check if pdfplumber is installed
    try:
        import pdfplumber
        print("✅ pdfplumber is installed")
    except ImportError:
        print("❌ ERROR: pdfplumber is not installed!")
        print("   Run: pip install pdfplumber")
        return False
    
    print("\n✅ All basic checks passed!")
    print("\nTo test with a real PDF:")
    print("   python test_pdf_endpoint.py <path-to-pdf-file>")
    
    # Test 4: If PDF file provided, test extraction
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"\n📄 Testing with PDF: {pdf_path}")
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{BASE_URL}/extract-text", files=files)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success! Extracted {len(data.get('text', ''))} characters")
                    print(f"   Pages: {data.get('pages', 0)}")
                    print(f"   Filename: {data.get('filename', 'N/A')}")
                    
                    # Print the extracted text
                    print("\n" + "="*80)
                    print("EXTRACTED TEXT:")
                    print("="*80)
                    if data.get('text'):
                        print(data['text'])
                    else:
                        print(data.get('message', 'No text found'))
                    print("="*80)
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   Response: {response.text}")
        except FileNotFoundError:
            print(f"❌ File not found: {pdf_path}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

if __name__ == "__main__":
    test_endpoint()

