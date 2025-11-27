#!/usr/bin/env python3
"""
Product intro video generation module.
Creates opening sequences and product introduction videos.
"""

import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


def generate_product_intro(product_name: str,
                          intro_text: Optional[str] = None,
                          duration: float = 0.8,
                          background_video: Optional[str] = None) -> str:
    """
    Generate product introduction video.
    
    Args:
        product_name: Name of the product
        intro_text: Optional custom intro text
        duration: Duration of intro in seconds (default 2.0 for faster hook)
        background_video: Optional background video path
    
    Returns:
        Path to generated intro video
    """
    logger.info(f"Generating product intro for: {product_name}")
    
    output_dir = Path("videos")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"intro_{product_name.replace(' ', '_')}_{timestamp}.mp4"
    
    # Load intro text from file if not provided
    if intro_text is None:
        intro_file = Path("product_intro.txt")
        if intro_file.exists():
            with open(intro_file, 'r') as f:
                intro_text = f.read().strip()
        else:
            intro_text = f"Introducing: {product_name}"
    
    try:
        if background_video and os.path.exists(background_video):
            # Use background video with text overlay
            intro_path = create_intro_with_video(
                product_name,
                intro_text,
                background_video,
                str(output_path),
                duration
            )
        else:
            # Create intro from scratch with animated text
            intro_path = create_animated_intro(
                product_name,
                intro_text,
                str(output_path),
                duration
            )
        
        logger.info(f"Product intro created: {intro_path}")
        return intro_path
        
    except Exception as e:
        logger.error(f"Failed to create product intro: {str(e)}")
        raise


def create_animated_intro(product_name: str, intro_text: str,
                         output_path: str, duration: float) -> str:
    """
    Create animated intro video with text.
    
    Args:
        product_name: Product name
        intro_text: Intro text
        output_path: Output video path
        duration: Video duration
    
    Returns:
        Path to created intro video
    """
    logger.info("Creating animated intro")
    
    try:
        # Clean text for FFmpeg (escape special characters)
        product_clean = product_name.replace("'", "\\'").replace(":", "\\:")
        intro_clean = intro_text[:50].replace("'", "\\'").replace(":", "\\:")
        
        # Create gradient background with animated text for reels
        # Fast intro: fade in 0.2s, display 0.4s, fade out 0.2s = 0.8s total
        filter_complex = (
            f"color=c=0x1a1a2e:s=1080x1920:d={duration}[bg];"
            f"[bg]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"text='{product_clean}':"
            f"fontsize=90:"
            f"fontcolor=white:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2:"
            f"alpha='if(lt(t,0.2),t*5,if(lt(t,{duration-0.2}),1,(1-t+{duration-0.2})*5))'"
        )
        
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x16213e:s=1080x1920:d={duration}",
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "25",
            "-y",
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Animated intro created: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create animated intro: {str(e)}")
        # Fallback to simple version
        return create_simple_intro(product_name, output_path, duration)


def create_intro_with_video(product_name: str, intro_text: str,
                           background_video: str, output_path: str,
                           duration: float) -> str:
    """
    Create intro using background video with text overlay.
    
    Args:
        product_name: Product name
        intro_text: Intro text
        background_video: Background video path
        output_path: Output video path
        duration: Video duration
    
    Returns:
        Path to created intro video
    """
    logger.info("Creating intro with background video")
    
    try:
        # Trim background video to duration
        trimmed_bg = output_path.replace('.mp4', '_bg_temp.mp4')
        
        trim_cmd = [
            "ffmpeg",
            "-i", background_video,
            "-t", str(duration),
            "-c", "copy",
            "-y",
            trimmed_bg
        ]
        
        subprocess.run(trim_cmd, capture_output=True, text=True, check=True)
        
        # Add text overlays
        filter_complex = (
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
            f"text='{product_name}':"
            f"fontsize=100:"
            f"fontcolor=white:"
            f"bordercolor=black:"
            f"borderw=3:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2-80:"
            f"alpha='if(lt(t,0.5),t*2,if(lt(t,{duration-0.5}),1,({duration}-t)*2))',"
            f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
            f"text='{intro_text[:60]}':"
            f"fontsize=36:"
            f"fontcolor=white:"
            f"bordercolor=black:"
            f"borderw=2:"
            f"x=(w-text_w)/2:"
            f"y=(h-text_h)/2+80:"
            f"alpha='if(lt(t,1),0,if(lt(t,1.5),(t-1)*2,if(lt(t,{duration-0.5}),1,({duration}-t)*2)))'"
        )
        
        cmd = [
            "ffmpeg",
            "-i", trimmed_bg,
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Clean up temp file
        if os.path.exists(trimmed_bg):
            os.remove(trimmed_bg)
        
        logger.info(f"Intro with background video created: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create intro with video: {str(e)}")
        # Fallback to simple version
        return create_simple_intro(product_name, output_path, duration)


def create_simple_intro(product_name: str, output_path: str,
                       duration: float = 0.8) -> str:
    """
    Create simple intro video (fallback method).
    
    Args:
        product_name: Product name
        output_path: Output video path
        duration: Video duration
    
    Returns:
        Path to created intro video
    """
    logger.info("Creating simple intro (fallback)")
    
    try:
        # Quick 2-second intro with fade - reels format (1080x1920)
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x1a1a2e:s=1080x1920:d={duration}",
            "-vf", (
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{product_name}':"
                f"fontsize=70:"
                f"fontcolor=white:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2:"
                f"alpha='if(lt(t,0.3),t/0.3,if(lt(t,{duration-0.3}),1,({duration}-t)/0.3))'"
            ),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Simple intro created: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to create simple intro: {str(e)}")
        raise


def create_outro(duration: float = 5.0) -> str:
    """
    Create outro/ending video.
    
    Args:
        duration: Duration of outro in seconds
    
    Returns:
        Path to created outro video
    """
    logger.info("Creating outro video")
    
    output_dir = Path("videos")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"outro_{timestamp}.mp4"
    
    outro_text = "Thanks for Watching!\\nLike & Subscribe"
    
    try:
        cmd = [
            "ffmpeg",
            "-f", "lavfi",
            "-i", f"color=c=0x1a1a2e:s=1920x1080:d={duration}",
            "-vf", (
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{outro_text}':"
                f"fontsize=70:"
                f"fontcolor=white:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2"
            ),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-y",
            str(output_path)
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Outro created: {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Failed to create outro: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    try:
        intro = generate_product_intro("Test Product", duration=3)
        print(f"Intro created: {intro}")
        
        outro = create_outro(duration=3)
        print(f"Outro created: {outro}")
        
    except Exception as e:
        print(f"Error: {e}")
