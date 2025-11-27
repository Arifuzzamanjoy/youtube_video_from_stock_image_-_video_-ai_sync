# Automated Video Content Generation System

## Overview
This system automatically generates complete product review videos from simple inputs like product names and keywords. It uses AI to generate content, creates narration, downloads stock footage, and compiles everything into a polished final video.

## Features
- 🤖 **AI Content Generation** using Google Gemini (Free)
- 🎨 **Image Generation** using Hugging Face Stable Diffusion
- 🎤 **Text-to-Speech** using Hugging Face or Google TTS
- 🎬 **Stock Video Download** from Pexels & Pixabay
- 🎞️ **Video Compilation** with transitions and effects
- 📝 **Automatic Descriptions** with SEO optimization

## Installation & Setup

### 1. Virtual Environment (Already Created)
```bash
cd /root/Agent/content
source venv/bin/activate
```

### 2. Dependencies (Already Installed)
All required Python packages are installed in the virtual environment.

### 3. API Keys (Configured in .env)
The following API keys are set up:
- ✅ Gemini API: For content generation
- ✅ Hugging Face API: For image and audio generation
- ✅ Pexels API: For stock videos
- ✅ Pixabay API: For additional stock videos

### 4. System Requirements
- FFmpeg (for video processing)
- Python 3.10+
- Linux/Ubuntu (currently configured)

## Usage

### Quick Start
```bash
# Using the run script (recommended)
./run.sh

# Or directly with Python
source venv/bin/activate
python main.py --product "Mechanical Keyboard" --keywords features performance design
```

### Command Line Options

**Single Product Mode:**
```bash
python main.py --product "Product Name" --keywords keyword1 keyword2
```

**Batch Mode** (processes multiple products from products.txt):
```bash
python main.py --batch
```

**Custom Output Format:**
```bash
python main.py --product "Product Name" --format mp4
```

Available formats: mp4, avi, mov, webm

## Project Structure

```
/root/Agent/content/
├── main.py                      # Main orchestrator
├── generate_content.py          # AI content generation (Gemini)
├── generate_audio.py            # Text-to-speech (Hugging Face/gTTS)
├── generate_image.py            # Image generation (Hugging Face)
├── download_stock_video.py      # Stock video downloader (Pexels/Pixabay)
├── generate_product_intro_video.py  # Intro video creator
├── generate_video_single.py     # Individual segment creator
├── generate_video_final.py      # Final video compiler
├── convert_video.py             # Video format converter
├── generate_description.py      # SEO description generator
├── .env                         # API keys (DO NOT SHARE)
├── products.txt                 # Product list for batch processing
├── venv/                        # Virtual environment
├── audios/                      # Generated audio files
├── assets/                      # Generated images
├── videos/                      # Output videos
└── logs/                        # Execution logs
```

## Workflow

1. **Content Generation** → Gemini AI generates video script
2. **Audio Generation** → Hugging Face converts text to speech
3. **Image Generation** → Hugging Face creates product images
4. **Stock Videos** → Downloads from Pexels/Pixabay
5. **Intro Video** → Creates branded opening sequence
6. **Video Segments** → Converts images to video with effects
7. **Final Compilation** → Combines everything with transitions
8. **Output** → Final video ready for upload

## Output

The final video includes:
- Branded intro sequence (5 seconds)
- AI-generated narration throughout
- Dynamic image sequences with Ken Burns effect
- Stock footage relevant to keywords
- Professional transitions between clips
- Background music (optional)
- SEO-optimized description

**Typical Output:**
- Resolution: 1920x1080 (Full HD)
- Duration: 30-45 seconds
- Format: MP4 (H.264 + AAC)
- Location: `videos/final_video_YYYYMMDD_HHMMSS.mp4`

## API Information

### Gemini API (Content Generation)
- Model: gemini-1.5-flash
- Free tier: Available
- Purpose: Generate video scripts with AI

### Hugging Face API (Images & Audio)
- Image Model: stabilityai/stable-diffusion-2-1
- Audio Model: espnet/kan-bayashi_ljspeech_vits
- Purpose: Generate visuals and narration

### Pexels API (Stock Videos)
- Free tier: 200 requests/hour
- Purpose: Download high-quality stock footage

### Pixabay API (Stock Videos)
- Free tier: Available
- Purpose: Alternative stock footage source

## Troubleshooting

**API Rate Limits:**
If you hit rate limits, the system will fall back to:
- Images: Placeholder generation with PIL
- Audio: Google TTS (gTTS) as fallback
- Videos: Use cached content

**FFmpeg Issues:**
Ensure FFmpeg is installed:
```bash
sudo apt install ffmpeg
```

**Missing Dependencies:**
Reinstall requirements:
```bash
source venv/bin/activate
pip install -r requirements_updated.txt
```

## Logs

Execution logs are saved in `logs/video_gen_YYYYMMDD_HHMMSS.log`

## Example

```bash
# Generate video for "Wireless Mouse"
./run.sh

# When prompted, enter: Wireless Mouse
# Or press Enter to process all products in products.txt
```

This will create a complete video in ~2-4 minutes with:
- AI-generated script about the wireless mouse
- Professional narration
- Product images
- Stock footage of office/tech scenes
- Smooth transitions and effects

## Notes

- First run may take longer due to model loading on Hugging Face
- Keep your .env file secure (API keys)
- Videos are saved with timestamps to avoid overwriting
- Check logs/ directory for detailed execution information

## Support

For issues or questions, check:
1. Log files in logs/
2. .env file configuration
3. API key validity
4. FFmpeg installation

---

**Ready to generate your first video? Run: `./run.sh`**
