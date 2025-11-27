#!/usr/bin/env python3
"""
Video engagement optimization module.
Implements attention-keeping techniques: hooks, pattern interrupts, fast cuts, B-roll.
Based on viral video best practices and YouTube engagement research.
"""

import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import random

logger = logging.getLogger(__name__)


class VideoEngagementOptimizer:
    """
    Optimizes videos for maximum engagement and attention retention.
    """
    
    # Attention retention patterns (based on research)
    OPTIMAL_SEGMENT_LENGTH = 2.5  # seconds - optimal for attention
    HOOK_DURATION = 3.0  # First 3 seconds are critical
    PATTERN_INTERRUPT_INTERVAL = 8.0  # Change something every 8 seconds
    
    def __init__(self):
        self.output_dir = Path("videos")
        self.output_dir.mkdir(exist_ok=True)
    
    def create_hook_segment(self, product_name: str, output_path: str) -> str:
        """
        Create attention-grabbing hook for first 3 seconds.
        Uses text overlay, zoom, bright colors.
        """
        logger.info("Creating hook segment")
        
        hook_text = self.generate_hook_text(product_name)
        # Clean text for FFmpeg - escape single quotes and special chars
        hook_text_clean = hook_text.replace("'", "").replace("!", "")
        
        try:
            # Simple hook with text - no complex animations that can break
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c=0xFF6B35:s=1080x1920:d={self.HOOK_DURATION}",
                "-vf",
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{hook_text_clean}':"
                f"fontsize=100:"
                f"fontcolor=white:"
                f"x=(w-text_w)/2:"
                f"y=(h-text_h)/2",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                "-t", str(self.HOOK_DURATION),
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Hook segment created: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create hook: {str(e)}")
            logger.error(f"FFmpeg stderr: {e.stderr}")
            # Fallback: simple colored frame
            return self._create_simple_hook(hook_text_clean, output_path)
    
    def _create_simple_hook(self, text: str, output_path: str) -> str:
        """Simple hook fallback"""
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1080, 1920), color=(255, 107, 53))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((1080 - text_width) // 2, (1920 - text_height) // 2)
        
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        temp_img = output_path.replace('.mp4', '_temp.png')
        img.save(temp_img)
        
        # Convert to video
        cmd = [
            "ffmpeg", "-loop", "1", "-i", temp_img,
            "-c:v", "libx264", "-t", str(self.HOOK_DURATION),
            "-pix_fmt", "yuv420p", "-y", output_path
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        
        os.remove(temp_img)
        return output_path
    
    def generate_hook_text(self, product_name: str) -> str:
        """Generate attention-grabbing hook text"""
        hooks = [
            f"Wait Until You See This!",
            f"You Won't Believe This!",
            f"This Changed Everything!",
            f"Watch This First!",
            f"Don't Skip This!",
            f"Game Changer Alert!",
            f"Shocking Results!"
        ]
        return random.choice(hooks)
    
    def add_fast_cuts(self, video_segments: List[str], output_path: str) -> str:
        """
        Create fast-paced cuts between segments for engagement.
        Adds quick transitions every 2-3 seconds.
        """
        logger.info(f"Adding fast cuts to {len(video_segments)} segments")
        
        try:
            # Create filter complex for fast cuts with crossfade
            filter_parts = []
            for i in range(len(video_segments) - 1):
                filter_parts.append(f"[{i}:v][{i+1}:v]xfade=transition=fade:duration=0.3:offset={self.OPTIMAL_SEGMENT_LENGTH}[v{i}]")
            
            # Build final concatenation
            inputs = " ".join([f"-i {seg}" for seg in video_segments])
            
            cmd = f"""ffmpeg {inputs} -filter_complex "{''.join(filter_parts)}" -c:v libx264 -pix_fmt yuv420p -y {output_path}"""
            
            subprocess.run(cmd, shell=True, capture_output=True, check=True)
            
            logger.info(f"Fast cuts applied: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Fast cuts failed: {str(e)}")
            return video_segments[0] if video_segments else None
    
    def add_zoom_effect(self, video_path: str, output_path: str, zoom_in: bool = True) -> str:
        """
        Add zoom effect to video for visual interest.
        """
        logger.info(f"Adding zoom effect to {video_path}")
        
        try:
            zoom_filter = "zoompan=z='min(zoom+0.001,1.1)':d=125" if zoom_in else "zoompan=z='max(zoom-0.001,1)':d=125"
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", zoom_filter,
                "-c:v", "libx264",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"Zoom effect added: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Zoom effect failed: {str(e)}")
            return video_path
    
    def add_text_overlay_intervals(self, video_path: str, text_points: List[Dict], output_path: str) -> str:
        """
        Add text overlays at specific intervals (pattern interrupts).
        text_points = [{"text": "Amazing Feature!", "start": 5.0, "duration": 2.0}]
        """
        logger.info(f"Adding {len(text_points)} text overlays")
        
        try:
            # Build drawtext filters for each text point
            drawtext_filters = []
            for i, point in enumerate(text_points):
                # Clean text - remove problematic characters
                text = point['text'].replace("'", "").replace("!", "").replace(":", "")
                start = point['start']
                end = start + point['duration']
                
                filter_str = (
                    f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                    f"text='{text}':"
                    f"fontsize=60:"
                    f"fontcolor=white:"
                    f"box=1:"
                    f"boxcolor=black@0.7:"
                    f"boxborderw=10:"
                    f"x=(w-text_w)/2:"
                    f"y=h-150:"
                    f"enable='between(t,{start},{end})'"
                )
                drawtext_filters.append(filter_str)
            
            vf = ",".join(drawtext_filters)
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", vf,
                "-c:v", "libx264",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Text overlays added: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Text overlays failed: {str(e)}")
            logger.error(f"FFmpeg stderr: {e.stderr}")
            return video_path
    
    def create_comparison_split_screen(self, video1: str, video2: str, 
                                       labels: tuple, output_path: str) -> str:
        """
        Create side-by-side comparison for product alternatives.
        """
        logger.info("Creating split-screen comparison")
        
        try:
            label1, label2 = labels
            
            cmd = [
                "ffmpeg",
                "-i", video1,
                "-i", video2,
                "-filter_complex",
                (
                    "[0:v]scale=960:1080,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                    f"text='{label1}':fontsize=40:fontcolor=white:x=50:y=50[left];"
                    "[1:v]scale=960:1080,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                    f"text='{label2}':fontsize=40:fontcolor=white:x=50:y=50[right];"
                    "[left][right]hstack=inputs=2[v]"
                ),
                "-map", "[v]",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", "3",
                "-y",
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            logger.info(f"Split-screen comparison created: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Split-screen creation failed: {str(e)}")
            return video1
    
    def add_call_to_action(self, video_path: str, cta_text: str, output_path: str) -> str:
        """
        Add call-to-action at the end of video.
        """
        logger.info("Adding call-to-action")
        
        try:
            # Clean CTA text for FFmpeg
            cta_clean = cta_text.replace("'", "").replace("!", "").replace(":", "")
            video_duration = self.get_video_duration(video_path)
            
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf",
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{cta_clean}':"
                f"fontsize=70:"
                f"fontcolor=yellow:"
                f"box=1:"
                f"boxcolor=black@0.8:"
                f"boxborderw=15:"
                f"x=(w-text_w)/2:"
                f"y=h-200:"
                f"enable='gt(t,{video_duration - 5})'",
                "-c:v", "libx264",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"CTA added: {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            logger.error(f"CTA addition failed: {str(e)}")
            logger.error(f"FFmpeg stderr: {e.stderr}")
            return video_path
    
    def get_video_duration(self, video_path: str) -> float:
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
            return 30.0  # default
    
    def optimize_pacing(self, segments: List[str]) -> List[str]:
        """
        Optimize segment pacing for attention retention.
        Trim segments to optimal length (2-3 seconds each).
        """
        logger.info("Optimizing video pacing")
        
        optimized = []
        for i, segment in enumerate(segments):
            output = segment.replace('.mp4', '_paced.mp4')
            
            try:
                cmd = [
                    "ffmpeg",
                    "-i", segment,
                    "-t", str(self.OPTIMAL_SEGMENT_LENGTH),
                    "-c:v", "libx264",
                    "-c:a", "aac",
                    "-y",
                    output
                ]
                subprocess.run(cmd, capture_output=True, check=True)
                optimized.append(output)
            except:
                optimized.append(segment)
        
        return optimized
    
    def generate_engagement_points(self, video_duration: float, content: str) -> List[Dict]:
        """
        Generate strategic text overlay points based on content.
        Returns list of {"text": "...", "start": 5.0, "duration": 2.0}
        """
        points = []
        
        # Extract key phrases from content
        sentences = content.split('.')[:5]
        key_phrases = [s.strip()[:50] for s in sentences if s.strip()]
        
        # Space them throughout video
        interval = video_duration / (len(key_phrases) + 1)
        
        for i, phrase in enumerate(key_phrases):
            points.append({
                "text": phrase,
                "start": interval * (i + 1),
                "duration": 2.0
            })
        
        return points


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    optimizer = VideoEngagementOptimizer()
    print("Video Engagement Optimizer ready")
    print("Features: hooks, fast cuts, text overlays, comparisons, CTAs")
