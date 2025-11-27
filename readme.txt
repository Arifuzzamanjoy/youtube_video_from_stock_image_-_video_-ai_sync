# Automated Video Content Generation System

## 📋 Overview

This is an automated video content generation system that creates professional product review videos from text descriptions. The system handles the entire pipeline from content creation to final video compilation.

## 🏗️ Architecture

The project follows a modular architecture with the following components:

### Core Modules

1. **main.py** - Main orchestrator that coordinates the entire pipeline
2. **generate_content.py** - Content generation and script creation
3. **generate_description.py** - Video description and metadata generation
4. **generate_audio.py** - Text-to-speech audio generation
5. **generate_image.py** - AI-powered image generation
6. **download_stock_video.py** - Stock video downloading from Pexels/Pixabay
7. **generate_video_single.py** - Individual video segment creation
8. **generate_product_intro_video.py** - Intro/outro video generation
9. **generate_video_final.py** - Final video compilation and editing
10. **convert_video.py** - Video format conversion and optimization

### Directory Structure

```
content/
├── assets/              # Generated images and graphics
├── audios/              # Generated audio narrations
├── chrome_user_data/    # Browser data for web scraping
├── ffmpeg/              # FFmpeg binaries (if needed)
├── logs/                # Application logs
├── transitions/         # Transition effects
├── videos/              # Output videos and segments
├── main.py              # Main entry point
├── generate_*.py        # Generation modules
├── convert_video.py     # Video conversion utilities
├── download_stock_video.py  # Stock video downloader
├── requirements.txt     # Python dependencies
├── keywords.txt         # Keywords for content
├── products.txt         # Product list
├── product_intro.txt    # Intro text template
└── google-credentials.json  # API credentials
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed and in PATH
- API keys for optional services:
  - Pexels API (for stock videos)
  - OpenAI API (for AI image generation)
  - Stability AI API (for image generation)
  - Azure Speech API (for TTS)

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # macOS
   brew install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Set up environment variables:**
   ```bash
   # Create .env file
   cat > .env << EOF
   PEXELS_API_KEY=your_pexels_key
   OPENAI_API_KEY=your_openai_key
   STABILITY_API_KEY=your_stability_key
   AZURE_SPEECH_KEY=your_azure_key
   AZURE_SPEECH_REGION=eastus
   EOF
   ```

4. **Configure Google credentials (optional):**
   - Edit `google-credentials.json` with your service account credentials

### Basic Usage

**Generate a video for a single product:**
```bash
python main.py --product "Mechanical Keyboard" --keywords features productivity
```

**Batch process multiple products:**
```bash
python main.py --batch --keywords technology innovation
```

**Specify output format:**
```bash
python main.py --product "USB-C Hub" --format mp4
```

## 📖 Detailed Usage

### Pipeline Workflow

The system executes the following steps:

1. **Content Generation** - Creates script from product name and keywords
2. **Description Generation** - Generates video description and metadata
3. **Audio Generation** - Converts script to speech using TTS
4. **Image Generation** - Creates product images using AI
5. **Stock Video Download** - Downloads relevant stock footage
6. **Intro Video Creation** - Generates opening sequence
7. **Segment Creation** - Creates individual video clips
8. **Final Compilation** - Combines all elements into final video

### Module Usage Examples

**Generate content only:**
```python
from generate_content import generate_content

content = generate_content("Gaming Mouse", ["performance", "features"])
print(content)
```

**Generate audio narration:**
```python
from generate_audio import generate_audio

audio_file = generate_audio("Your narration text here", engine="gtts")
```

**Create video from images:**
```python
from generate_video_single import create_video_from_image

video = create_video_from_image("image.png", "output.mp4", duration=5.0)
```

## 🔧 Configuration

### Product Configuration

Edit `products.txt` to add products:
```
Wireless Mouse
Mechanical Keyboard
USB-C Hub
```

### Keywords Configuration

Edit `keywords.txt` to customize content themes:
```
technology
productivity
innovation
```

### Intro Text Template

Edit `product_intro.txt` to customize intro:
```
Welcome to our product showcase! Today we're featuring...
```

## 📦 Output

The system generates:

- **Final Video** - `videos/final_video_TIMESTAMP.mp4`
- **Audio Files** - `audios/narration_TIMESTAMP.mp3`
- **Images** - `assets/image_TIMESTAMP_N.png`
- **Logs** - `logs/video_gen_TIMESTAMP.log`

## 🎨 Customization

### Modify TTS Engine

In `generate_audio.py`, change the engine:
```python
audio = generate_audio(text, engine="pyttsx3")  # or "gtts", "azure"
```

### Adjust Video Quality

In `convert_video.py`, modify quality settings:
```python
video = convert_video_format(input, quality="high")  # or "medium", "low"
```

### Change Video Resolution

In `generate_video_single.py`:
```python
create_video_from_image(image, output, resolution="3840x2160")  # 4K
```

## 🐛 Troubleshooting

**FFmpeg not found:**
- Ensure FFmpeg is installed and in your PATH
- Test with `ffmpeg -version`

**API key errors:**
- Verify your API keys in `.env` file
- Check API quotas and limits

**Memory issues with large videos:**
- Reduce video resolution
- Process fewer segments at once
- Use lower quality settings

**Audio generation fails:**
- Try different TTS engine
- Check internet connection for cloud TTS
- Install required audio codecs

## 📝 API Keys Setup

### Pexels API
1. Sign up at https://www.pexels.com/api/
2. Get your API key
3. Add to `.env`: `PEXELS_API_KEY=your_key`

### OpenAI API
1. Sign up at https://platform.openai.com/
2. Create API key
3. Add to `.env`: `OPENAI_API_KEY=your_key`

### Stability AI
1. Sign up at https://platform.stability.ai/
2. Get API key
3. Add to `.env`: `STABILITY_API_KEY=your_key`

## 🔒 Security Notes

- Never commit API keys to version control
- Use `.env` file for sensitive credentials
- Keep `google-credentials.json` secure
- Regularly rotate API keys

## 📊 Performance Optimization

- **Parallel Processing**: Process multiple segments simultaneously
- **Caching**: Reuse downloaded stock videos
- **Quality Presets**: Use appropriate quality for your needs
- **Batch Mode**: Process multiple products in one run

## 🤝 Contributing

This is a template project. Customize it for your needs:
- Add new TTS providers
- Integrate additional stock video sources
- Implement custom transitions
- Add subtitle generation
- Enhance AI content generation

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues and questions:
- Check the logs in `logs/` directory
- Review module documentation in source files
- Verify FFmpeg installation
- Test individual modules separately

## 🎯 Roadmap

Potential enhancements:
- [ ] Automatic subtitle generation
- [ ] Multi-language support
- [ ] Custom transition effects
- [ ] Real-time preview
- [ ] Web interface
- [ ] Cloud deployment support
- [ ] Batch processing optimization
- [ ] Template system for different video styles

---

**Note**: This system requires proper API credentials for full functionality. Without API keys, it will use fallback methods (placeholder images, offline TTS, etc.)
