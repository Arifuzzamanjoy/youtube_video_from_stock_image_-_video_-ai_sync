#!/usr/bin/env python3
"""
Subtitle generation module for adding captions to videos.
Generates SRT subtitle files from audio using speech recognition.
"""

import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import subprocess
import json

logger = logging.getLogger(__name__)


def generate_subtitles_from_text(text: str, audio_duration: float, output_path: str) -> str:
    """
    Generate SRT subtitles from text by splitting into timed segments.
    
    Args:
        text: Full narration text
        audio_duration: Duration of audio in seconds
        output_path: Path to save SRT file
    
    Returns:
        Path to generated SRT file
    """
    logger.info("Generating subtitles from text")
    
    # Split text into sentences
    sentences = split_into_sentences(text)
    
    # Calculate timing for each sentence
    time_per_sentence = audio_duration / len(sentences) if sentences else 0
    
    # Generate SRT content
    srt_content = []
    current_time = 0.0
    
    for i, sentence in enumerate(sentences, 1):
        start_time = format_srt_time(current_time)
        end_time = format_srt_time(current_time + time_per_sentence)
        
        srt_content.append(f"{i}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(sentence.strip())
        srt_content.append("")  # Blank line between entries
        
        current_time += time_per_sentence
    
    # Write SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_content))
    
    logger.info(f"Generated SRT with {len(sentences)} subtitle segments: {output_path}")
    return output_path


def split_into_sentences(text: str) -> List[str]:
    """Split text into short phrases for mobile-friendly subtitles"""
    import re
    
    # Split text into words
    words = text.split()
    phrases = []
    current_phrase = []
    
    for word in words:
        current_phrase.append(word)
        # Create subtitle every 4-5 words or at punctuation
        if len(current_phrase) >= 4 or word.endswith(('.', '!', '?', ',', ':')):
            phrase_text = ' '.join(current_phrase).strip('.,!?:')
            if phrase_text:
                phrases.append(phrase_text)
            current_phrase = []
    
    # Add remaining words
    if current_phrase:
        phrase_text = ' '.join(current_phrase).strip('.,!?:')
        if phrase_text:
            phrases.append(phrase_text)
    
    return phrases if phrases else ["No subtitles"]


def format_srt_time(seconds: float) -> str:
    """Format seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def add_subtitles_to_video(video_path: str, subtitle_path: str, output_path: str) -> str:
    """
    Burn subtitles into video optimized for YouTube Shorts (vertical format).
    
    Args:
        video_path: Input video path
        subtitle_path: SRT subtitle file path
        output_path: Output video path
    
    Returns:
        Path to video with burned-in subtitles
    """
    logger.info(f"Adding subtitles to video: {video_path}")
    
    try:
        # Escape special characters in subtitle path for FFmpeg
        subtitle_path_escaped = subtitle_path.replace('\\', '/').replace(':', '\\:')
        
        # Optimized for vertical 1080x1920 Shorts format
        cmd = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f"subtitles={subtitle_path_escaped}:force_style='FontName=Arial Bold,FontSize=32,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=4,Outline=3,Shadow=2,MarginV=120,Alignment=2'",
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'copy',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Subtitles added successfully: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to add subtitles: {e.stderr}")
        # Fallback: return original video if subtitles fail
        logger.warning("Returning original video without subtitles")
        return video_path
    except Exception as e:
        logger.error(f"Unexpected error adding subtitles: {str(e)}")
        return video_path


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration using FFprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            audio_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        
        return duration
        
    except Exception as e:
        logger.error(f"Failed to get audio duration: {str(e)}")
        return 0.0


if __name__ == "__main__":
    # Test subtitle generation
    logging.basicConfig(level=logging.INFO)
    
    test_text = """
    Welcome to our product review. Today we're looking at an amazing wireless mouse.
    This device offers incredible precision and comfort. Let's explore its features.
    The ergonomic design ensures all-day comfort. RGB lighting adds a stylish touch.
    """
    
    srt_path = "test_subtitles.srt"
    subtitles = generate_subtitles_from_text(test_text, 30.0, srt_path)
    print(f"Generated subtitles: {subtitles}")
