#!/usr/bin/env python3
"""
Final video compilation module.
Combines all segments, adds audio, transitions, and produces the final output.
"""

import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


def generate_final_video(intro_video: str, segments: List[str],
                        audio_path: Optional[str] = None,
                        outro_video: Optional[str] = None,
                        output_filename: Optional[str] = None) -> str:
    """
    Compile final video from all components.
    
    Args:
        intro_video: Path to intro video
        segments: List of video segment paths
        audio_path: Optional audio narration path
        outro_video: Optional outro video path
        output_filename: Optional custom output filename
    
    Returns:
        Path to final compiled video
    """
    logger.info("Compiling final video")
    
    output_dir = Path("videos")
    output_dir.mkdir(exist_ok=True)
    
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"final_video_{timestamp}.mp4"
    
    output_path = output_dir / output_filename
    
    # Prepare list of all video segments
    all_segments = []
    
    if intro_video and os.path.exists(intro_video):
        all_segments.append(intro_video)
    
    all_segments.extend(segments)
    
    if outro_video and os.path.exists(outro_video):
        all_segments.append(outro_video)
    
    logger.info(f"Total segments to compile: {len(all_segments)}")
    
    try:
        # Step 1: Concatenate all video segments
        concat_video = str(output_dir / f"temp_concat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        concatenate_videos(all_segments, concat_video)
        
        # Step 2: Add audio if provided
        if audio_path and os.path.exists(audio_path):
            final_path = add_audio_to_video(concat_video, audio_path, str(output_path))
        else:
            # Just use concatenated video
            os.rename(concat_video, str(output_path))
            final_path = str(output_path)
        
        # Clean up temp files
        if os.path.exists(concat_video) and concat_video != final_path:
            os.remove(concat_video)
        
        logger.info(f"Final video created: {final_path}")
        return final_path
        
    except Exception as e:
        logger.error(f"Failed to compile final video: {str(e)}")
        raise


def concatenate_videos(video_paths: List[str], output_path: str,
                      with_transitions: bool = True) -> str:  # Enabled for realistic videos
    """
    Concatenate multiple videos into one.
    
    Args:
        video_paths: List of video file paths
        output_path: Output video path
        with_transitions: Whether to add transitions between clips
    
    Returns:
        Path to concatenated video
    """
    logger.info(f"Concatenating {len(video_paths)} videos with transitions={with_transitions}")
    
    if not video_paths:
        raise ValueError("No videos to concatenate")
    
    if len(video_paths) == 1:
        # Just copy the single video
        import shutil
        shutil.copy(video_paths[0], output_path)
        return output_path
    
    try:
        # Create concat file list
        concat_file = Path(output_path).parent / "concat_list.txt"
        
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{os.path.abspath(video_path)}'\n")
        
        # Use smooth transitions for realistic product review feel
        if with_transitions and len(video_paths) <= 10:
            return concatenate_with_smooth_transitions(video_paths, output_path)
        
        # Fallback to simple concatenation for many clips
        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c:v", "libx264",
            "-preset", "fast",  # Better quality for final video
            "-crf", "23",  # Good quality
            "-c:a", "aac",
            "-b:a", "192k",  # Better audio quality
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        final_path = output_path
        
        # Clean up
        if concat_file.exists():
            concat_file.unlink()
        
        logger.info(f"Videos concatenated: {final_path}")
        return final_path
        
    except Exception as e:
        logger.error(f"Concatenation failed: {str(e)}")
        raise


def concatenate_with_smooth_transitions(video_paths: List[str], output_path: str) -> str:
    """
    Concatenate videos with smooth crossfade transitions for rhythmic flow.
    
    Args:
        video_paths: List of video paths
        output_path: Output path
    
    Returns:
        Path to output video
    """
    logger.info("Concatenating with crossfade transitions for smooth rhythm")
    
    if len(video_paths) == 1:
        import shutil
        shutil.copy(video_paths[0], output_path)
        return output_path
    
    try:
        # Use xfade filter for smooth crossfade transitions
        # This prevents freezing and creates rhythmic flow
        transition_duration = 0.3  # 0.3s crossfade between segments
        
        # Build complex filter with crossfades
        filter_parts = []
        for i in range(len(video_paths)):
            filter_parts.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1[v{i}]")
        
        # Create xfade transitions
        current = "v0"
        for i in range(1, len(video_paths)):
            if i == 1:
                filter_parts.append(f"[{current}][v{i}]xfade=transition=fade:duration={transition_duration}:offset=0[vout{i}]")
            else:
                filter_parts.append(f"[vout{i-1}][v{i}]xfade=transition=fade:duration={transition_duration}:offset=0[vout{i}]")
        
        filter_complex = ";".join(filter_parts)
        final_output = f"vout{len(video_paths)-1}" if len(video_paths) > 1 else "v0"
        
        # Build ffmpeg command
        cmd = ["ffmpeg"]
        for video_path in video_paths:
            cmd.extend(["-i", video_path])
        
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", f"[{final_output}]",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-y",
            output_path
        ])
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Videos concatenated with crossfades: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Crossfade concatenation failed: {str(e)}, using simple concat")
        # Fallback to simple concatenation
        return concatenate_videos_simple(video_paths, output_path)


def concatenate_videos_simple(video_paths: List[str], output_path: str) -> str:
    """Simple concatenation without transitions as fallback."""
    concat_file = Path(output_path).parent / "concat_list_simple.txt"
    with open(concat_file, 'w') as f:
        for video_path in video_paths:
            f.write(f"file '{os.path.abspath(video_path)}'\n")
    
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-r", "30",
        "-c:a", "aac",
        "-y",
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    concat_file.unlink()
    return output_path


def add_audio_to_video(video_path: str, audio_path: str, output_path: str,
                      mix_mode: str = "replace") -> str:
    """
    Add or mix audio with video, stretching video if needed to match audio.
    
    Args:
        video_path: Input video path
        audio_path: Audio file path
        output_path: Output video path
        mix_mode: 'replace' or 'mix' (mix with existing audio)
    
    Returns:
        Path to output video
    """
    logger.info(f"Adding audio to video (mode: {mix_mode})")
    
    try:
        # Get durations
        video_duration = get_video_duration(video_path)
        audio_duration = get_audio_duration(audio_path)
        
        logger.info(f"Video duration: {video_duration}s, Audio duration: {audio_duration}s")
        
        if mix_mode == "replace":
            # Replace video audio with new audio
            # Use fps filter for fast speed adjustment (no heavy interpolation)
            if abs(video_duration - audio_duration) > 2.0:  # If difference > 2 seconds
                speed_factor = video_duration / audio_duration
                logger.info(f"Syncing video to audio ({video_duration:.1f}s -> {audio_duration:.1f}s, speed={speed_factor:.3f})")
                
                # Use simple setpts + fps for fast processing (no interpolation)
                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-i", audio_path,
                    "-filter:v", f"setpts={speed_factor}*PTS,fps=30",
                    "-c:v", "libx264",
                    "-preset", "fast",
                    "-crf", "23",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    "-y",
                    output_path
                ]
            else:
                # Durations close enough
                logger.info("Video and audio durations aligned, no speed adjustment needed")
                cmd = [
                    "ffmpeg",
                    "-i", video_path,
                    "-i", audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-shortest",
                    "-y",
                    output_path
                ]
        else:  # mix
            # Mix video audio with new audio
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", audio_path,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[aout]",
                "-c:v", "copy",
                "-map", "0:v:0",
                "-map", "[aout]",
                "-y",
                output_path
            ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Audio added to video: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to add audio: {str(e)}")
        raise


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds"""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return 0.0


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds"""
    try:
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


def add_background_music(video_path: str, music_path: str, output_path: str,
                        volume: float = 0.3) -> str:
    """
    Add background music to video.
    
    Args:
        video_path: Input video path
        music_path: Background music path
        output_path: Output video path
        volume: Music volume (0.0 to 1.0)
    
    Returns:
        Path to output video
    """
    logger.info("Adding background music")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex",
            f"[1:a]volume={volume}[a1];[0:a][a1]amix=inputs=2:duration=first[aout]",
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "[aout]",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Background music added: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to add background music: {str(e)}")
        raise


def add_subtitles(video_path: str, subtitle_path: str, output_path: str) -> str:
    """
    Add subtitles to video.
    
    Args:
        video_path: Input video path
        subtitle_path: Subtitle file path (.srt)
        output_path: Output video path
    
    Returns:
        Path to output video
    """
    logger.info("Adding subtitles")
    
    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={subtitle_path}",
            "-c:a", "copy",
            "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Subtitles added: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to add subtitles: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    print("Final video generation module ready")
    print("Available functions:")
    print("- generate_final_video()")
    print("- concatenate_videos()")
    print("- add_audio_to_video()")
    print("- add_background_music()")
    print("- add_subtitles()")
