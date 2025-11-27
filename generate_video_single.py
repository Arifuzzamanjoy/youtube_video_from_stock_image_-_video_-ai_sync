#!/usr/bin/env python3
"""
Single video segment generation module.
Creates individual video clips from images and stock footage.
"""

import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds."""
    try:
        import subprocess
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0


def generate_single_video(images: List[str], stock_videos: List[str],
                         audio_path: Optional[str] = None,
                         duration_per_clip: float = 2.5) -> List[str]:
    """
    Generate individual video segments from images and stock footage.
    Interleaves stock videos and product images for variety.
    
    Args:
        images: List of image paths
        stock_videos: List of stock video paths
        audio_path: Optional audio narration path
        duration_per_clip: Duration for each image clip in seconds
    
    Returns:
        List of generated video segment paths (videos and images interleaved)
    """
    # Pattern: VVVV-I-VVVV-I-VVVV-I-VVVV-I-VVVV-I (V=video, I=image)
    # 25 segments total: 20 videos + 5 images (80/20 ratio)
    pattern = [0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]  # 0=video, 1=image
    
    # Adjust segment duration based on audio if provided
    if audio_path and os.path.exists(audio_path):
        audio_duration = get_audio_duration(audio_path)
        # Calculate optimal segment duration: audio_duration / 25 segments
        optimal_duration = audio_duration / 25.0
        # Clamp between 2.0s (fast) and 2.5s (no freezing) for good pacing
        duration_per_clip = max(2.0, min(2.5, optimal_duration))
        logger.info(f"Audio: {audio_duration:.1f}s -> Segment duration: {duration_per_clip:.1f}s (25 segments)")
    
    total_segments = len(pattern)
    expected_duration = total_segments * duration_per_clip
    logger.info(f"Creating {total_segments} segments: {pattern.count(0)} videos + {pattern.count(1)} images")
    logger.info(f"Target duration: {expected_duration:.1f}s = {total_segments} segments x {duration_per_clip:.1f}s each")
    
    segments = []
    output_dir = Path("videos")
    output_dir.mkdir(exist_ok=True)
    
    # Strategy: 4 videos, 1 image pattern (80/20 ratio)
    # This gives optimal engagement with product visibility for longer reviews
    
    video_idx = 0
    image_idx = 0
    
    # Loop through pattern: 0=video, 1=image
    # Vary segment duration slightly for more natural feel (2.0-3.0s range)
    for position, segment_type in enumerate(pattern):
        # Add slight variation to avoid robotic feeling (±0.3s)
        import random
        segment_duration = duration_per_clip + random.uniform(-0.3, 0.3)
        segment_duration = max(2.0, min(3.0, segment_duration))  # Keep within safe range
        
        if segment_type == 0:  # Video segment
            if video_idx < len(stock_videos):
                video_path = stock_videos[video_idx]
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = output_dir / f"segment_stock_{timestamp}_{position}.mp4"
                    
                    # Trim and resize to reels format with nice transition
                    trim_cmd = [
                        "ffmpeg", "-i", video_path,
                        "-t", str(segment_duration),
                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fade=t=in:st=0:d=0.2,fade=t=out:st=" + str(segment_duration-0.2) + ":d=0.2",
                        "-c:v", "libx264", "-preset", "fast",
                        "-crf", "23",  # Good quality
                        "-c:a", "aac",
                        "-y", str(output_path)
                    ]
                    
                    subprocess.run(trim_cmd, capture_output=True, check=True)
                    segments.append(str(output_path))
                    logger.info(f"Video trimmed to {segment_duration:.1f}s: {output_path}")
                    logger.info(f"Added stock video segment {video_idx+1}/{pattern.count(0)}")
                    video_idx += 1
                except Exception as e:
                    logger.error(f"Failed to process video {video_path}: {str(e)}")
                    video_idx += 1
        
        elif segment_type == 1:  # Image segment
            if image_idx < len(images):
                image_path = images[image_idx]
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = output_dir / f"segment_image_{timestamp}_{position}.mp4"
                    
                    create_video_from_image(image_path, str(output_path), segment_duration)
                    segments.append(str(output_path))
                    logger.info(f"Video created from image: {output_path}")
                    logger.info(f"Added image segment {image_idx+1}/{pattern.count(1)}")
                    image_idx += 1
                except Exception as e:
                    logger.error(f"Failed to create video from image {image_path}: {str(e)}")
                    image_idx += 1
    
    logger.info(f"Generated {len(segments)} video segments ({video_idx} videos, {image_idx} images)")
    return segments


def create_video_from_image(image_path: str, output_path: str,
                           duration: float = 3.0,
                           resolution: str = "1080x1920") -> str:
    """
    Create video clip from static image with zoom effect.
    
    Args:
        image_path: Path to image
        output_path: Output video path
        duration: Video duration in seconds
        resolution: Output resolution
    
    Returns:
        Path to created video
    """
    logger.info(f"Creating video from image: {image_path}")
    
    try:
        # Ken Burns effect with aggressive zoom (no static feel)
        # Limit duration to 2.5s max to prevent long still frames
        actual_duration = min(duration, 2.5)
        cmd = [
            "ffmpeg",
            "-loop", "1",
            "-i", image_path,
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2,zoompan=z='min(1+0.015*on,1.5)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(actual_duration * 30)}:s=1080x1920:fps=30,fade=t=in:st=0:d=0.2,fade=t=out:st={actual_duration-0.2}:d=0.2",
            "-t", str(actual_duration),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-y",
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        logger.info(f"Video created from image: {output_path}")
        return output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create video from image: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Video creation failed: {str(e)}")
        raise


def trim_video_segment(input_path: str, output_path: str,
                      duration: float = 3.0) -> str:
    """
    Trim video to specific duration.
    
    Args:
        input_path: Input video path
        output_path: Output video path
        duration: Target duration in seconds
    
    Returns:
        Path to trimmed video
    """
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Video trimmed to {duration}s: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Trimming failed: {str(e)}")
        # If copy fails, re-encode
        try:
            cmd = [
                "ffmpeg",
                "-i", input_path,
                "-t", str(duration),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",
                output_path
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            return output_path
        except:
            raise


def add_transition(video1: str, video2: str, output_path: str,
                  transition_type: str = "fade") -> str:
    """
    Add transition between two videos.
    
    Args:
        video1: First video path
        video2: Second video path
        output_path: Output video path
        transition_type: Type of transition (fade, wipe, dissolve)
    
    Returns:
        Path to video with transition
    """
    logger.info(f"Adding {transition_type} transition between videos")
    
    try:
        if transition_type == "fade":
            filter_complex = (
                "[0:v]fade=t=out:st=2:d=1[v0];"
                "[1:v]fade=t=in:st=0:d=1[v1];"
                "[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[outv][outa]"
            )
        else:
            # Default concatenation
            filter_complex = "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]"
        
        cmd = [
            "ffmpeg",
            "-i", video1,
            "-i", video2,
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "[outa]",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Transition added: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Transition failed: {str(e)}")
        raise


def apply_color_grading(input_path: str, output_path: str,
                       style: str = "vibrant") -> str:
    """
    Apply color grading to video.
    
    Args:
        input_path: Input video path
        output_path: Output video path
        style: Color grading style (vibrant, cinematic, vintage)
    
    Returns:
        Path to graded video
    """
    logger.info(f"Applying {style} color grading")
    
    # Color grading filters
    styles = {
        "vibrant": "eq=contrast=1.2:brightness=0.05:saturation=1.3",
        "cinematic": "curves=preset=color_negative",
        "vintage": "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3",
        "warm": "colorbalance=rs=0.2:gs=0.1:bs=-0.1",
        "cool": "colorbalance=rs=-0.1:gs=-0.05:bs=0.15"
    }
    
    filter_str = styles.get(style, styles["vibrant"])
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", filter_str,
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Color grading applied: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Color grading failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Single video generation module ready")
    print("Available functions:")
    print("- generate_single_video()")
    print("- create_video_from_image()")
    print("- trim_video_segment()")
    print("- add_transition()")
    print("- apply_color_grading()")
