#!/usr/bin/env python3
"""
Video conversion and format handling module.
Supports conversion between different video formats using ffmpeg.
"""

import os
import logging
import subprocess
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def convert_video_format(input_path: str, output_format: str = "mp4",
                        output_path: Optional[str] = None,
                        codec: str = "libx264",
                        quality: str = "medium") -> str:
    """
    Convert video to different format.
    
    Args:
        input_path: Input video path
        output_format: Output format (mp4, avi, mov, webm)
        output_path: Optional output path
        codec: Video codec to use
        quality: Quality preset (low, medium, high)
    
    Returns:
        Path to converted video
    """
    logger.info(f"Converting {input_path} to {output_format}")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_suffix(f".{output_format}"))
    
    # If input and output are the same, skip conversion
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        logger.info(f"File already in {output_format} format, skipping conversion: {input_path}")
        return input_path
    
    # Quality presets
    quality_settings = {
        "low": {"crf": "28", "preset": "fast"},
        "medium": {"crf": "23", "preset": "medium"},
        "high": {"crf": "18", "preset": "slow"}
    }
    
    settings = quality_settings.get(quality, quality_settings["medium"])
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", codec,
            "-crf", settings["crf"],
            "-preset", settings["preset"],
            "-c:a", "aac",
            "-b:a", "192k",
            "-y",  # Overwrite output file
            output_path
        ]
        
        logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Video converted successfully: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg conversion failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise


def resize_video(input_path: str, width: int, height: int,
                output_path: Optional[str] = None) -> str:
    """
    Resize video to specific dimensions.
    
    Args:
        input_path: Input video path
        width: Target width
        height: Target height
        output_path: Optional output path
    
    Returns:
        Path to resized video
    """
    logger.info(f"Resizing video to {width}x{height}")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_stem(f"{input_file.stem}_resized"))
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale={width}:{height}",
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Video resized: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Resize failed: {str(e)}")
        raise


def trim_video(input_path: str, start_time: float, duration: float,
              output_path: Optional[str] = None) -> str:
    """
    Trim video to specific duration.
    
    Args:
        input_path: Input video path
        start_time: Start time in seconds
        duration: Duration in seconds
        output_path: Optional output path
    
    Returns:
        Path to trimmed video
    """
    logger.info(f"Trimming video from {start_time}s for {duration}s")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_stem(f"{input_file.stem}_trimmed"))
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Video trimmed: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Trim failed: {str(e)}")
        raise


def compress_video(input_path: str, target_size_mb: Optional[int] = None,
                   output_path: Optional[str] = None) -> str:
    """
    Compress video to reduce file size.
    
    Args:
        input_path: Input video path
        target_size_mb: Optional target size in MB
        output_path: Optional output path
    
    Returns:
        Path to compressed video
    """
    logger.info(f"Compressing video: {input_path}")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_stem(f"{input_file.stem}_compressed"))
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "libx264",
            "-crf", "28",
            "-c:a", "aac",
            "-b:a", "128k",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Video compressed: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Compression failed: {str(e)}")
        raise


def extract_audio(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Extract audio from video.
    
    Args:
        input_path: Input video path
        output_path: Optional output path
    
    Returns:
        Path to extracted audio file
    """
    logger.info(f"Extracting audio from: {input_path}")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_suffix(".mp3"))
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vn",  # No video
            "-acodec", "libmp3lame",
            "-ab", "192k",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Audio extracted: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Audio extraction failed: {str(e)}")
        raise


def add_watermark(input_path: str, watermark_path: str,
                 position: str = "bottom_right",
                 output_path: Optional[str] = None) -> str:
    """
    Add watermark to video.
    
    Args:
        input_path: Input video path
        watermark_path: Path to watermark image
        position: Watermark position (top_left, top_right, bottom_left, bottom_right)
        output_path: Optional output path
    
    Returns:
        Path to watermarked video
    """
    logger.info(f"Adding watermark to: {input_path}")
    
    if output_path is None:
        input_file = Path(input_path)
        output_path = str(input_file.with_stem(f"{input_file.stem}_watermarked"))
    
    # Position mapping
    positions = {
        "top_left": "10:10",
        "top_right": "main_w-overlay_w-10:10",
        "bottom_left": "10:main_h-overlay_h-10",
        "bottom_right": "main_w-overlay_w-10:main_h-overlay_h-10"
    }
    
    overlay_pos = positions.get(position, positions["bottom_right"])
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-i", watermark_path,
            "-filter_complex", f"overlay={overlay_pos}",
            "-codec:a", "copy",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Watermark added: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Watermark failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Video conversion module ready")
    print("Available functions:")
    print("- convert_video_format()")
    print("- resize_video()")
    print("- trim_video()")
    print("- compress_video()")
    print("- extract_audio()")
    print("- add_watermark()")
