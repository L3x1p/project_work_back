"""
Simple test script to verify the PDF extraction endpoint works with LLM career analysis
Run this to test if the server endpoint is working correctly
"""

import requests
import sys
import json
import os

BASE_URL = "http://localhost:8000"
LLAMA_API_URL = os.getenv("LLAMA_CHAT_API_URL", "http://localhost:8002")

def test_endpoint():
    """Test if the endpoint is accessible"""
    print("Testing PDF extraction endpoint with LLM career analysis...")
    print(f"Server URL: {BASE_URL}")
    print(f"LLM Service URL: {LLAMA_API_URL}")
    print()
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Backend server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend server!")
        print("   Make sure the server is running: uvicorn main:app --reload")
        return False
    
    # Test 2: Check if LLM service is running
    try:
        response = requests.get(f"{LLAMA_API_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            if health.get("model_loaded"):
                print(f"✅ LLM service is running and model is loaded")
            else:
                print(f"⚠️  LLM service is running but model is not loaded")
        else:
            print(f"⚠️  LLM service responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to LLM service at {LLAMA_API_URL}!")
        print("   Make sure the LLaMA Chat API is running on port 8002")
        return False
    except Exception as e:
        print(f"⚠️  Could not check LLM service health: {e}")
    
    # Test 3: Check if pdfplumber is installed
    try:
        import pdfplumber
        print("✅ pdfplumber is installed")
    except ImportError:
        print("❌ ERROR: pdfplumber is not installed!")
        print("   Run: pip install pdfplumber")
        return False
    
    # Test 4: Check if httpx is installed (for LLM service calls)
    try:
        import httpx
        print("✅ httpx is installed")
    except ImportError:
        print("❌ ERROR: httpx is not installed!")
        print("   Run: pip install httpx")
        return False
    
    print("\n✅ All basic checks passed!")
    print("\nTo test with a real PDF:")
    print("   python test_pdf_endpoint.py <path-to-pdf-file>")
    
    # Test 5: If PDF file provided, test extraction and career analysis
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        print(f"\n📄 Testing with PDF: {pdf_path}")
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                print("   Sending PDF to server...")
                response = requests.post(f"{BASE_URL}/extract-text", files=files, timeout=120)
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success! Processed PDF")
                    print(f"   Pages: {data.get('pages', 0)}")
                    print(f"   Characters: {data.get('characters', 0)}")
                    print(f"   Filename: {data.get('filename', 'N/A')}")
                    
                    # Check for errors
                    if data.get('error'):
                        print(f"\n⚠️  Error from LLM service: {data['error']}")
                        if data.get('raw_response'):
                            print(f"\nRaw LLM Response:")
                            print(data['raw_response'])
                    
                    # Print career fields analysis
                    print("\n" + "="*80)
                    print("CAREER FIELDS ANALYSIS:")
                    print("="*80)
                    
                    career_fields = data.get('career_fields', [])
                    if career_fields:
                        print(f"\nFound {len(career_fields)} potential career fields:\n")
                        for i, field in enumerate(career_fields, 1):
                            print(f"{i}. {field.get('field', 'N/A')}")
                            print(f"   Summary: {field.get('summary', 'N/A')}")
                            skills = field.get('key_skills_mentioned', [])
                            if skills:
                                print(f"   Key Skills: {', '.join(skills)}")
                            print()
                    else:
                        print("No career fields identified.")
                    
                    overall_summary = data.get('overall_summary', '')
                    if overall_summary:
                        print("\n" + "-"*80)
                        print("OVERALL SUMMARY:")
                        print("-"*80)
                        print(overall_summary)
                    
                    print("="*80)
                    
                    # Also print as JSON for debugging
                    print("\n" + "="*80)
                    print("FULL JSON RESPONSE:")
                    print("="*80)
                    print(json.dumps(data, indent=2))
                    print("="*80)
                else:
                    print(f"❌ Error: {response.status_code}")
                    print(f"   Response: {response.text}")
        except FileNotFoundError:
            print(f"❌ File not found: {pdf_path}")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    return True

if __name__ == "__main__":
    test_endpoint()

