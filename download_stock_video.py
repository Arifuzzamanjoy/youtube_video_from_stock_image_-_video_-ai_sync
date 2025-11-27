#!/usr/bin/env python3
"""
Stock video download module for fetching royalty-free videos from various sources.
Supports Pexels, Pixabay, and other stock video platforms.
"""

import os
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from time import sleep

logger = logging.getLogger(__name__)

# Directory for videos
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)


def download_stock_videos(keywords: List[str], count: int = 10, 
                          source: str = "pexels") -> List[str]:
    """
    Download stock videos based on keywords.
    
    Args:
        keywords: List of search keywords
        count: Number of videos to download
        source: Video source ('pexels', 'pixabay')
    
    Returns:
        List of downloaded video file paths
    """
    logger.info(f"Downloading {count} stock videos from {source} for keywords: {keywords}")
    
    video_paths = []
    
    try:
        if source == "pexels":
            video_paths = download_from_pexels(keywords, count)
        elif source == "pixabay":
            video_paths = download_from_pixabay(keywords, count)
        else:
            logger.warning(f"Unknown source {source}, using pexels")
            video_paths = download_from_pexels(keywords, count)
        
        logger.info(f"Successfully downloaded {len(video_paths)} videos")
        return video_paths
        
    except Exception as e:
        logger.error(f"Failed to download stock videos: {str(e)}")
        return []


def download_from_pexels(keywords: List[str], count: int) -> List[str]:
    """Download videos from Pexels."""
    api_key = os.getenv("PEXELS_API_KEY")
    
    if not api_key:
        logger.warning("PEXELS_API_KEY not set, skipping download")
        return []
    
    base_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    
    video_paths = []
    
    # First, try searching with combined keywords for better context
    combined_query = " ".join(keywords[:3])  # Use top 3 keywords together
    logger.info(f"Searching Pexels with combined query: {combined_query}")
    
    params = {
        "query": combined_query,
        "per_page": min(count, 15),  # Get more results to filter
        "orientation": "portrait"  # Vertical videos for reels
    }
    
    try:
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        videos = data.get("videos", [])
        
        for video in videos:
            if len(video_paths) >= count:
                break
            
            video_files = video.get("video_files", [])
            if not video_files:
                continue
            
            # Prefer vertical HD videos (1080x1920 for reels)
            hd_video = next((vf for vf in video_files if vf.get("width") == 1080 and vf.get("height") == 1920), None)
            if not hd_video:
                # Fallback to portrait videos or highest quality
                portrait_videos = [vf for vf in video_files if vf.get("height", 0) > vf.get("width", 0)]
                if portrait_videos:
                    portrait_videos.sort(key=lambda x: x.get("height", 0), reverse=True)
                    hd_video = portrait_videos[0]
                else:
                    video_files.sort(key=lambda x: x.get("width", 0), reverse=True)
                    hd_video = video_files[0]
            
            video_url = hd_video.get("link")
            if not video_url:
                continue
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            keyword_safe = combined_query.replace(" ", "_")[:20]
            filename = f"stock_{keyword_safe}_{timestamp}_{len(video_paths)}.mp4"
            file_path = VIDEOS_DIR / filename
            
            logger.info(f"Downloading video {len(video_paths)+1}/{count}: {video_url}")
            if download_file(video_url, str(file_path)):
                video_paths.append(str(file_path))
            sleep(0.5)
    except Exception as e:
        logger.error(f"Combined query failed: {str(e)}, falling back to individual keywords")
    
    # If still need more videos, search by individual keywords
    for keyword in keywords:
        if len(video_paths) >= count:
            break
        
        logger.info(f"Searching Pexels for: {keyword}")
        
        params = {
            "query": keyword,
            "per_page": min(5, count - len(video_paths)),
            "orientation": "portrait"  # Vertical videos for reels
        }
        
        try:
            response = requests.get(base_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            videos = data.get("videos", [])
            
            for video in videos:
                if len(video_paths) >= count:
                    break
                
                # Get the highest quality video file
                video_files = video.get("video_files", [])
                if not video_files:
                    continue
                
                # Sort by quality (width)
                video_files.sort(key=lambda x: x.get("width", 0), reverse=True)
                best_video = video_files[0]
                
                video_url = best_video.get("link")
                if not video_url:
                    continue
                
                # Download video
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stock_{keyword.replace(' ', '_')}_{timestamp}_{len(video_paths)}.mp4"
                file_path = VIDEOS_DIR / filename
                
                logger.info(f"Downloading: {video_url}")
                download_file(video_url, str(file_path))
                
                video_paths.append(str(file_path))
                sleep(0.5)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Failed to download from Pexels for keyword '{keyword}': {str(e)}")
            continue
    
    return video_paths


def download_from_pixabay(keywords: List[str], count: int) -> List[str]:
    """Download videos from Pixabay."""
    api_key = os.getenv("PIXABAY_API_KEY")
    
    if not api_key:
        logger.warning("PIXABAY_API_KEY not set, skipping download")
        return []
    
    base_url = "https://pixabay.com/api/videos/"
    
    video_paths = []
    
    for keyword in keywords:
        if len(video_paths) >= count:
            break
        
        logger.info(f"Searching Pixabay for: {keyword}")
        
        params = {
            "key": api_key,
            "q": keyword,
            "per_page": min(5, count - len(video_paths)),
            "video_type": "all"
        }
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            videos = data.get("hits", [])
            
            for video in videos:
                if len(video_paths) >= count:
                    break
                
                # Get video URL (medium quality)
                video_data = video.get("videos", {})
                medium_video = video_data.get("medium", {})
                video_url = medium_video.get("url")
                
                if not video_url:
                    continue
                
                # Download video
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stock_{keyword.replace(' ', '_')}_{timestamp}_{len(video_paths)}.mp4"
                file_path = VIDEOS_DIR / filename
                
                logger.info(f"Downloading: {video_url}")
                download_file(video_url, str(file_path))
                
                video_paths.append(str(file_path))
                sleep(0.5)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Failed to download from Pixabay for keyword '{keyword}': {str(e)}")
            continue
    
    return video_paths


def download_file(url: str, output_path: str, chunk_size: int = 8192) -> bool:
    """
    Download file from URL.
    
    Args:
        url: File URL
        output_path: Output file path
        chunk_size: Download chunk size
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(output_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        if downloaded % (chunk_size * 100) == 0:  # Log every ~800KB
                            logger.debug(f"Download progress: {progress:.1f}%")
        
        logger.info(f"Downloaded: {output_path} ({total_size / 1024 / 1024:.2f} MB)")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download {url}: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def get_video_info(video_path: str) -> dict:
    """
    Get video information using ffprobe.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Dictionary with video metadata
    """
    try:
        import subprocess
        import json
        
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        video_stream = next(
            (s for s in data.get('streams', []) if s.get('codec_type') == 'video'),
            {}
        )
        
        info = {
            'duration': float(data.get('format', {}).get('duration', 0)),
            'width': video_stream.get('width', 0),
            'height': video_stream.get('height', 0),
            'fps': eval(video_stream.get('r_frame_rate', '0/1')),
            'codec': video_stream.get('codec_name', 'unknown')
        }
        
        logger.info(f"Video info: {info}")
        return info
        
    except Exception as e:
        logger.error(f"Failed to get video info: {str(e)}")
        return {}


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    test_keywords = ["technology", "workspace"]
    
    try:
        videos = download_stock_videos(test_keywords, count=2)
        print(f"Downloaded videos: {videos}")
        
        if videos:
            info = get_video_info(videos[0])
            print(f"Video info: {info}")
            
    except Exception as e:
        print(f"Error: {e}")
