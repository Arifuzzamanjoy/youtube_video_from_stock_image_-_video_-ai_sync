#!/usr/bin/env python3
"""
Audio generation module for creating voiceover narration using TTS.
Supports multiple TTS engines: Hugging Face, Google TTS, pyttsx3.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Directory for audio files
AUDIO_DIR = Path("audios")
AUDIO_DIR.mkdir(exist_ok=True)


def generate_audio(text: str, output_filename: Optional[str] = None, 
                   engine: str = "gemini", voice: str = "en") -> str:
    """
    Generate audio from text using text-to-speech.
    
    Args:
        text: Text to convert to speech
        output_filename: Optional custom filename
        engine: TTS engine to use ('gemini', 'gtts', 'pyttsx3', 'azure')
        voice: Voice/language code
    
    Returns:
        Path to generated audio file
    """
    logger.info(f"Generating audio using {engine} engine for {len(text)} characters")
    
    # Validate text length for longer reviews
    if len(text) < 500:
        logger.warning(f"Text too short for 60-90s video: {len(text)} chars. Expected 800-1200 words.")
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"narration_{timestamp}.mp3"
    
    output_path = AUDIO_DIR / output_filename
    
    try:
        if engine == "huggingface" or engine == "hf":
            audio_path = generate_with_huggingface(text, str(output_path))
        elif engine == "gtts":
            audio_path = generate_with_gtts(text, str(output_path), voice)
        elif engine == "pyttsx3":
            audio_path = generate_with_pyttsx3(text, str(output_path))
        else:
            # Default to Hugging Face if available, otherwise gtts
            if os.getenv("HUGGINGFACE_API_KEY"):
                audio_path = generate_with_huggingface(text, str(output_path))
            else:
                logger.warning(f"Hugging Face API not available, falling back to gtts")
                audio_path = generate_with_gtts(text, str(output_path), voice)
        
        logger.info(f"Audio generated successfully: {audio_path}")
        return audio_path
        
    except Exception as e:
        logger.error(f"Failed to generate audio: {str(e)}")
        raise


def generate_with_huggingface(text: str, output_path: str) -> str:
    """
    Generate audio using Hugging Face Inference API.
    """
    try:
        import requests
        import time
        
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            logger.warning("HUGGINGFACE_API_KEY not set, falling back to gTTS")
            return generate_with_gtts(text, output_path)
        
        # Using Facebook's MMS-TTS model
        API_URL = "https://router.huggingface.co/models/facebook/mms-tts-eng"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        logger.info("Generating audio with Hugging Face TTS...")
        
        # Retry logic for model loading
        max_retries = 2
        for attempt in range(max_retries):
            response = requests.post(API_URL, headers=headers, json={"inputs": text}, timeout=30)
            
            if response.status_code == 503:
                logger.info(f"Model loading, attempt {attempt + 1}/{max_retries}...")
                time.sleep(10)
                continue
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                logger.info(f"Generated audio with Hugging Face: {output_path}")
                return output_path
            else:
                logger.warning(f"HuggingFace TTS failed: {response.status_code}")
                break
        
        # Fallback to gTTS
        logger.info("Falling back to gTTS")
        return generate_with_gtts(text, output_path)
        
    except Exception as e:
        logger.error(f"Hugging Face TTS failed: {str(e)}, falling back to gTTS")
        return generate_with_gtts(text, output_path)


def generate_with_gtts(text: str, output_path: str, lang: str = "en") -> str:
    """Generate audio using Google Text-to-Speech."""
    try:
        from gtts import gTTS
        
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_path)
        
        logger.info(f"Generated audio with gTTS: {output_path}")
        return output_path
        
    except ImportError:
        logger.error("gTTS not installed. Install with: pip install gtts")
        raise
    except Exception as e:
        logger.error(f"gTTS generation failed: {str(e)}")
        raise


def generate_with_pyttsx3(text: str, output_path: str) -> str:
    """Generate audio using pyttsx3 (offline TTS)."""
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        
        # Configure voice properties
        engine.setProperty('rate', 150)  # Speed
        engine.setProperty('volume', 0.9)  # Volume
        
        # Get available voices
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        logger.info(f"Generated audio with pyttsx3: {output_path}")
        return output_path
        
    except ImportError:
        logger.error("pyttsx3 not installed. Install with: pip install pyttsx3")
        raise
    except Exception as e:
        logger.error(f"pyttsx3 generation failed: {str(e)}")
        raise



    except Exception as e:
        logger.error(f"Hugging Face generation failed: {str(e)}")
        # Fallback to gTTS
        return generate_with_gtts(text, output_path, "en")


def get_audio_duration(audio_path: str) -> float:
    """
    Get duration of audio file in seconds.
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Duration in seconds
    """
    try:
        from pydub import AudioSegment
        
        audio = AudioSegment.from_file(audio_path)
        duration = len(audio) / 1000.0  # Convert to seconds
        
        logger.info(f"Audio duration: {duration:.2f} seconds")
        return duration
        
    except ImportError:
        logger.warning("pydub not installed, cannot get audio duration")
        return 0.0
    except Exception as e:
        logger.error(f"Failed to get audio duration: {str(e)}")
        return 0.0


def combine_audio_files(audio_files: list, output_path: str) -> str:
    """
    Combine multiple audio files into one.
    
    Args:
        audio_files: List of audio file paths
        output_path: Output file path
    
    Returns:
        Path to combined audio file
    """
    try:
        from pydub import AudioSegment
        
        combined = AudioSegment.empty()
        
        for audio_file in audio_files:
            audio = AudioSegment.from_file(audio_file)
            combined += audio
        
        combined.export(output_path, format="mp3")
        
        logger.info(f"Combined {len(audio_files)} audio files into {output_path}")
        return output_path
        
    except ImportError:
        logger.error("pydub not installed")
        raise
    except Exception as e:
        logger.error(f"Failed to combine audio files: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    test_text = "This is a test of the audio generation system. It should create a clear voice."
    
    try:
        audio_file = generate_audio(test_text, "test_audio.mp3", engine="gtts")
        print(f"Audio generated: {audio_file}")
        
        duration = get_audio_duration(audio_file)
        print(f"Duration: {duration:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {e}")
