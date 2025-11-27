#!/usr/bin/env python3
"""
Quick test script to verify all components are working
"""

import os
import sys
from dotenv import load_dotenv

print("=" * 60)
print("  SYSTEM VERIFICATION TEST")
print("=" * 60)

# Load environment variables
load_dotenv()

# Test 1: Environment Variables
print("\n[1] Testing Environment Variables...")
tests = {
    "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
    "PEXELS_API_KEY": os.getenv("PEXELS_API_KEY"),
    "PIXABAY_API_KEY": os.getenv("PIXABAY_API_KEY")
}

all_passed = True
for key, value in tests.items():
    status = "✓ PASS" if value else "✗ FAIL"
    print(f"  {key}: {status}")
    if not value:
        all_passed = False

# Test 2: Python Imports
print("\n[2] Testing Python Dependencies...")
dependencies = [
    ("google.generativeai", "Gemini API"),
    ("requests", "HTTP Requests"),
    ("PIL", "Image Processing"),
    ("gtts", "Text-to-Speech"),
    ("dotenv", "Environment Variables")
]

for module, name in dependencies:
    try:
        __import__(module)
        print(f"  {name}: ✓ PASS")
    except ImportError:
        print(f"  {name}: ✗ FAIL")
        all_passed = False

# Test 3: Directory Structure
print("\n[3] Testing Directory Structure...")
directories = ["audios", "assets", "videos", "logs"]
for directory in directories:
    exists = os.path.exists(directory)
    status = "✓ PASS" if exists else "✗ FAIL"
    print(f"  {directory}/: {status}")
    if not exists:
        os.makedirs(directory, exist_ok=True)
        print(f"    → Created directory")

# Test 4: FFmpeg
print("\n[4] Testing FFmpeg...")
import subprocess
try:
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if result.returncode == 0:
        version = result.stdout.split('\n')[0]
        print(f"  FFmpeg: ✓ PASS")
        print(f"    → {version}")
    else:
        print(f"  FFmpeg: ✗ FAIL")
        all_passed = False
except FileNotFoundError:
    print(f"  FFmpeg: ✗ FAIL (not installed)")
    print(f"    → Install with: sudo apt install ffmpeg")
    all_passed = False

# Test 5: Gemini API Connection
print("\n[5] Testing Gemini API Connection...")
try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'test successful' in 3 words")
    print(f"  Gemini API: ✓ PASS")
    print(f"    → Response: {response.text[:50]}...")
except Exception as e:
    print(f"  Gemini API: ✗ FAIL")
    print(f"    → Error: {str(e)[:100]}")
    all_passed = False

# Final Summary
print("\n" + "=" * 60)
if all_passed:
    print("  ✓ ALL TESTS PASSED!")
    print("  System is ready to generate videos.")
    print("\n  Run: ./run.sh to start")
else:
    print("  ✗ SOME TESTS FAILED!")
    print("  Please fix the issues above before running.")
print("=" * 60)

sys.exit(0 if all_passed else 1)
