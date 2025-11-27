#!/usr/bin/env python3
"""
Image generation module for creating product images, thumbnails, and graphics.
Supports AI image generation via Hugging Face and image manipulation.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Directory for images
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)


def generate_images(prompt: str, product_name: Optional[str] = None, 
                   count: int = 2, size: Tuple[int, int] = (1920, 1080)) -> List[str]:
    """
    Generate images based on text prompt.
    
    Args:
        prompt: Text description for image generation
        product_name: Optional product name
        count: Number of images to generate
        size: Image size (width, height)
    
    Returns:
        List of paths to generated images
    """
    logger.info(f"Generating {count} images for: {product_name or 'content'}")
    
    image_paths = []
    
    for i in range(count):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}_{i+1}.png"
        image_path = ASSETS_DIR / filename
        
        try:
            # Try multiple image generation methods
            img_path = None
            
            # Try Pexels first (fast, reliable, high-quality stock images)
            if os.getenv("PEXELS_API_KEY"):
                try:
                    img_path = generate_with_pexels(prompt, str(image_path))
                except Exception as e:
                    logger.warning(f"Pexels failed: {str(e)[:100]}")
                    img_path = None
            
            # Try Unsplash as backup (free, no API key needed)
            if not img_path:
                try:
                    img_path = generate_with_unsplash(prompt, str(image_path))
                except Exception as e:
                    logger.warning(f"Unsplash failed: {str(e)[:100]}")
                    img_path = None
            
            # Try Hugging Face if stock images failed
            if not img_path and os.getenv("HUGGINGFACE_API_KEY"):
                try:
                    img_path = generate_with_huggingface(prompt, str(image_path))
                except Exception as e:
                    logger.warning(f"Hugging Face failed: {str(e)[:100]}")
                    img_path = None
            
            # If HF failed or not available, try other methods
            if not img_path and os.getenv("STABILITY_API_KEY"):
                try:
                    img_path = generate_with_stability(prompt, str(image_path), size)
                except Exception as e:
                    logger.warning(f"Stability AI failed: {str(e)[:100]}")
                    img_path = None
            
            if not img_path and os.getenv("OPENAI_API_KEY"):
                try:
                    img_path = generate_with_dalle(prompt, str(image_path))
                except Exception as e:
                    logger.warning(f"DALL-E failed: {str(e)[:100]}")
                    img_path = None
            
            # Final fallback to placeholder
            if not img_path:
                logger.info("Using placeholder image generation")
                img_path = generate_placeholder(prompt, str(image_path), size)
            
            image_paths.append(img_path)
            logger.info(f"Generated image {i+1}/{count}: {img_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate image {i+1}: {str(e)}")
            # Even if everything fails, create a basic placeholder
            try:
                img_path = generate_placeholder(f"Image {i+1}", str(image_path), size)
                image_paths.append(img_path)
            except:
                continue
    
    logger.info(f"Successfully generated {len(image_paths)} images")
    return image_paths


def generate_with_pexels(prompt: str, output_path: str) -> str:
    """
    Generate image using Pexels API (high-quality stock photos).
    """
    try:
        import requests
        
        api_key = os.getenv("PEXELS_API_KEY")
        if not api_key:
            raise ValueError("PEXELS_API_KEY not set")
        
        # Extract keywords from prompt
        keywords = prompt.lower().split()[:5]  # First 5 words
        query = " ".join(keywords)
        
        logger.info(f"Searching Pexels for: {query}")
        
        # Search Pexels API
        headers = {"Authorization": api_key}
        search_url = f"https://api.pexels.com/v1/search?query={query}&per_page=1&orientation=landscape"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if not data.get('photos'):
            raise Exception("No photos found")
        
        # Download the image (use large size for quality)
        photo = data['photos'][0]
        image_url = photo['src']['large2x']  # High quality
        
        img_response = requests.get(image_url, timeout=15)
        img_response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
        
        logger.info(f"Downloaded from Pexels: {output_path} ({len(img_response.content) / 1024:.1f} KB)")
        return output_path
        
    except Exception as e:
        logger.error(f"Pexels generation failed: {str(e)}")
        raise


def generate_with_unsplash(prompt: str, output_path: str) -> str:
    """
    Generate image using Unsplash API (free, high-quality stock photos).
    """
    try:
        import requests
        
        # Extract keywords from prompt
        keywords = prompt.lower().split()[:3]  # First 3 words
        query = " ".join(keywords)
        
        # Use free direct link (no API key needed, unlimited)
        # Source.unsplash.com provides random images based on keywords
        image_url = f"https://source.unsplash.com/1920x1080/?{query.replace(' ', ',')},technology"
        
        logger.info(f"Downloading from Unsplash: {query}")
        
        # Download image
        img_response = requests.get(image_url, timeout=15)
        img_response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
        
        logger.info(f"Generated image from Unsplash: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Unsplash generation failed: {str(e)}")
        raise


def generate_with_huggingface(prompt: str, output_path: str) -> str:
    """
    Generate image using Hugging Face Inference API.
    """
    try:
        import requests
        import time
        
        api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY not set")
        
        # Use Stable Diffusion model on Hugging Face with new endpoint
        API_URL = "https://router.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        logger.info(f"Generating image with Hugging Face: {prompt[:50]}...")
        
        payload = {"inputs": prompt}
        
        # Retry logic for model loading
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 503:
                logger.info(f"Model loading, attempt {attempt + 1}/{max_retries}...")
                time.sleep(20)  # Wait for model to load
                continue
            
            if response.status_code != 200:
                raise Exception(f"API returned status code {response.status_code}: {response.text}")
            
            break
        
        # Save image
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Generated image with Hugging Face: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Hugging Face image generation failed: {str(e)}")
        raise


def generate_with_gemini_old(prompt: str, output_path: str, 
                        size: Tuple[int, int]) -> str:
    """Generate image using Google Gemini API."""
    try:
        import google.generativeai as genai
        from PIL import Image
        import io
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        # Use Gemini's imagen model for image generation
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Enhanced prompt for better image quality
        enhanced_prompt = f"High quality professional product photography: {prompt}. Photorealistic, 4K, studio lighting, detailed."
        
        logger.info(f"Generating image with Gemini: {enhanced_prompt[:100]}...")
        
        # Generate image using Gemini
        response = model.generate_content(enhanced_prompt)
        
        # For now, create placeholder as Gemini's native image gen may need different approach
        # This will be updated when Gemini Imagen API is fully available
        logger.info("Creating high-quality placeholder with Gemini context")
        return generate_placeholder(prompt, output_path, size)
        
    except Exception as e:
        logger.error(f"Gemini image generation failed: {str(e)}, using placeholder")
        return generate_placeholder(prompt, output_path, size)





def generate_placeholder(text: str, output_path: str, 
                        size: Tuple[int, int]) -> str:
    """Generate placeholder image with text."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create image with gradient background
        image = Image.new('RGB', size, color=(30, 30, 50))
        draw = ImageDraw.Draw(image)
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        words = text.split()[:10]
        wrapped_text = '\n'.join(words)
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        # Draw text
        draw.text(position, wrapped_text, fill=(255, 255, 255), font=font)
        
        # Save image
        image.save(output_path)
        
        logger.info(f"Generated placeholder image: {output_path}")
        return output_path
        
    except ImportError:
        logger.error("PIL not installed. Install with: pip install Pillow")
        raise
    except Exception as e:
        logger.error(f"Placeholder generation failed: {str(e)}")
        raise


def create_thumbnail(image_path: str, size: Tuple[int, int] = (1280, 720)) -> str:
    """
    Create video thumbnail from image.
    
    Args:
        image_path: Source image path
        size: Thumbnail size
    
    Returns:
        Path to thumbnail
    """
    try:
        from PIL import Image
        
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        thumbnail_path = str(Path(image_path).with_stem(Path(image_path).stem + "_thumb"))
        img.save(thumbnail_path)
        
        logger.info(f"Created thumbnail: {thumbnail_path}")
        return thumbnail_path
        
    except Exception as e:
        logger.error(f"Failed to create thumbnail: {str(e)}")
        raise


def add_text_overlay(image_path: str, text: str, output_path: str = None) -> str:
    """
    Add text overlay to image.
    
    Args:
        image_path: Source image path
        text: Text to overlay
        output_path: Output path
    
    Returns:
        Path to image with overlay
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Load font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Position text at bottom
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((img.width - text_width) // 2, img.height - text_height - 50)
        
        # Draw semi-transparent background
        padding = 20
        draw.rectangle(
            [position[0] - padding, position[1] - padding,
             position[0] + text_width + padding, position[1] + text_height + padding],
            fill=(0, 0, 0, 180)
        )
        
        # Draw text
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        if output_path is None:
            output_path = str(Path(image_path).with_stem(Path(image_path).stem + "_overlay"))
        
        img.save(output_path)
        
        logger.info(f"Added text overlay: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to add text overlay: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    
    try:
        images = generate_images(
            "Professional product photography of a mechanical keyboard",
            product_name="Keyboard",
            count=3
        )
        print(f"Generated images: {images}")
        
    except Exception as e:
        print(f"Error: {e}")
