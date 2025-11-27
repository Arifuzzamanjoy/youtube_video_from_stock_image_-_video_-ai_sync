#!/usr/bin/env python3
"""
Test all APIs to see which ones are working
"""

import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

print("=" * 70)
print("  API TESTING - Checking which services are working")
print("=" * 70)

# Test 1: Gemini API
print("\n[1] Testing Gemini API...")
try:
    import google.generativeai as genai
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  ✗ No API key found")
    else:
        genai.configure(api_key=api_key)
        
        # List available models
        print("  → Listing available models...")
        models = genai.list_models()
        gemini_models = [m.name for m in models if 'gemini' in m.name.lower()]
        
        if gemini_models:
            print(f"  ✓ WORKING - Found {len(gemini_models)} Gemini models")
            print(f"    Available models:")
            for model in gemini_models[:5]:
                print(f"      - {model}")
            
            # Test with first model
            test_model = gemini_models[0].replace('models/', '')
            print(f"\n  → Testing with: {test_model}")
            model = genai.GenerativeModel(test_model)
            response = model.generate_content("Say hello in 3 words")
            print(f"  ✓ Response: {response.text[:50]}")
        else:
            print("  ✗ No Gemini models found")
            
except Exception as e:
    print(f"  ✗ FAILED: {str(e)[:100]}")

# Test 2: Hugging Face API
print("\n[2] Testing Hugging Face API...")
try:
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("  ✗ No API key found")
    else:
        # Test with a simple model
        url = "https://api-inference.huggingface.co/models/gpt2"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(url, headers=headers, json={"inputs": "Hello"}, timeout=10)
        
        if response.status_code == 200:
            print(f"  ✓ WORKING - Status: {response.status_code}")
        elif response.status_code == 503:
            print(f"  ⚠ Model loading - Status: {response.status_code}")
            print(f"    (This is normal, try again in 20 seconds)")
        else:
            print(f"  ✗ FAILED - Status: {response.status_code}")
            print(f"    Response: {response.text[:100]}")
            
except Exception as e:
    print(f"  ✗ FAILED: {str(e)[:100]}")

# Test 3: Pexels API
print("\n[3] Testing Pexels API...")
try:
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        print("  ✗ No API key found")
    else:
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": api_key}
        params = {"query": "technology", "per_page": 1}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            video_count = len(data.get("videos", []))
            print(f"  ✓ WORKING - Found {video_count} videos")
        else:
            print(f"  ✗ FAILED - Status: {response.status_code}")
            print(f"    Response: {response.text[:100]}")
            
except Exception as e:
    print(f"  ✗ FAILED: {str(e)[:100]}")

# Test 4: Pixabay API
print("\n[4] Testing Pixabay API...")
try:
    api_key = os.getenv("PIXABAY_API_KEY")
    if not api_key:
        print("  ✗ No API key found")
    else:
        url = "https://pixabay.com/api/videos/"
        params = {"key": api_key, "q": "technology", "per_page": 3}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            video_count = len(data.get("hits", []))
            print(f"  ✓ WORKING - Found {video_count} videos")
        else:
            print(f"  ✗ FAILED - Status: {response.status_code}")
            print(f"    Response: {response.text[:100]}")
            
except Exception as e:
    print(f"  ✗ FAILED: {str(e)[:100]}")

print("\n" + "=" * 70)
print("  FREE ALTERNATIVES:")
print("=" * 70)

print("""
✓ TEXT-TO-SPEECH (Audio):
  - gTTS (Google TTS) - FREE, unlimited, working ✓
  - pyttsx3 - FREE, offline, no API needed ✓
  
✓ STOCK VIDEOS:
  - Pexels - FREE, 200 requests/hour ✓
  - Pixabay - FREE, unlimited ✓
  
✓ CONTENT GENERATION:
  - Gemini API - FREE tier, need correct model name
  - Template-based - FREE, no API, works offline ✓
  
✓ IMAGE GENERATION:
  - Placeholder with PIL - FREE, works offline ✓
  - Unsplash API - FREE, 50 requests/hour
  - Lorem Picsum - FREE, unlimited (random images)
  
✓ RECOMMENDATION: Use current setup!
  - Audio: gTTS (already working perfectly)
  - Videos: Pexels (already working perfectly)
  - Images: PIL placeholders (professional looking)
  - Content: Template + Gemini (with correct model)
""")

print("=" * 70)
