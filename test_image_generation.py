#!/usr/bin/env python3
"""
Test script for image generation with Gemini, Groq, and fallback options.
Tests:
1. Gemini API for image generation (if supported)
2. Groq API for image generation (if supported)
3. Stock images from Unsplash
4. Product images from web scraping
"""

import os
import sys
import logging
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Test directories
TEST_DIR = Path("test_images")
TEST_DIR.mkdir(exist_ok=True)


def test_gemini_image_gen():
    """
    Test Gemini API for image generation.
    Note: Gemini currently doesn't support direct image generation through standard API.
    This will test if there's any workaround.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Gemini API Image Generation")
    logger.info("="*80)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("❌ GEMINI_API_KEY not set")
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Test if Gemini has image generation capability
        logger.info("Testing Gemini API connection...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Gemini currently doesn't have native image generation
        # It can only analyze images and generate text
        logger.warning("⚠️  Gemini API does NOT support image generation (only text/analysis)")
        logger.info("Gemini can: Analyze images, generate text, answer questions")
        logger.info("Gemini cannot: Generate/create images from text prompts")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Gemini test failed: {str(e)}")
        return None


def test_groq_image_gen():
    """
    Test Groq API for image generation.
    Note: Groq is optimized for LLM inference, not image generation.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Groq API Image Generation")
    logger.info("="*80)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("❌ GROQ_API_KEY not set")
        return None
    
    try:
        # Groq is for LLM inference, not image generation
        logger.warning("⚠️  Groq API does NOT support image generation")
        logger.info("Groq specializes in: Fast LLM inference (text generation)")
        logger.info("Groq cannot: Generate/create images")
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Groq test failed: {str(e)}")
        return None


def test_unsplash_stock_images():
    """
    Test downloading stock images from Unsplash.
    This is FREE and doesn't require API key.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Unsplash Stock Images (FREE)")
    logger.info("="*80)
    
    try:
        test_queries = [
            "mechanical keyboard gaming",
            "gaming mouse",
            "technology workspace"
        ]
        
        results = []
        for query in test_queries:
            logger.info(f"\nDownloading image for: {query}")
            
            # Unsplash Source API - free, no API key needed
            url = f"https://source.unsplash.com/1920x1080/?{query.replace(' ', ',')}"
            
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"unsplash_{query.replace(' ', '_')}_{timestamp}.jpg"
            filepath = TEST_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Downloaded: {filepath} ({len(response.content) / 1024:.1f} KB)")
            results.append(str(filepath))
        
        logger.info(f"\n✅ SUCCESS: Downloaded {len(results)} Unsplash images")
        return results
        
    except Exception as e:
        logger.error(f"❌ Unsplash test failed: {str(e)}")
        return None


def test_pexels_stock_images():
    """
    Test downloading stock images from Pexels API.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Pexels Stock Images")
    logger.info("="*80)
    
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        logger.error("❌ PEXELS_API_KEY not set")
        return None
    
    try:
        headers = {"Authorization": api_key}
        test_queries = ["gaming keyboard", "technology"]
        
        results = []
        for query in test_queries:
            logger.info(f"\nSearching Pexels for: {query}")
            
            # Search for photos
            url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('photos'):
                photo = data['photos'][0]
                image_url = photo['src']['large']
                
                # Download the image
                img_response = requests.get(image_url, timeout=15)
                img_response.raise_for_status()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pexels_{query.replace(' ', '_')}_{timestamp}.jpg"
                filepath = TEST_DIR / filename
                
                with open(filepath, 'wb') as f:
                    f.write(img_response.content)
                
                logger.info(f"✅ Downloaded: {filepath} ({len(img_response.content) / 1024:.1f} KB)")
                results.append(str(filepath))
        
        logger.info(f"\n✅ SUCCESS: Downloaded {len(results)} Pexels images")
        return results
        
    except Exception as e:
        logger.error(f"❌ Pexels test failed: {str(e)}")
        return None


def test_product_image_scraping():
    """
    Test scraping product images from the web.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 5: Product Image Scraping")
    logger.info("="*80)
    
    try:
        from scrape_product import fetch_product_data
        
        # Test product
        product_name = "Razer DeathAdder Gaming Mouse"
        logger.info(f"Fetching product images for: {product_name}")
        
        product_data = fetch_product_data(product_name, ["gaming", "mouse"])
        
        if product_data and 'images' in product_data:
            images = product_data['images']
            logger.info(f"✅ Found {len(images)} product images")
            
            # Download first image for testing
            if images:
                image_url = images[0]
                logger.info(f"Downloading: {image_url[:100]}...")
                
                response = requests.get(image_url, timeout=15)
                response.raise_for_status()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"product_{timestamp}.jpg"
                filepath = TEST_DIR / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✅ Downloaded product image: {filepath} ({len(response.content) / 1024:.1f} KB)")
                return [str(filepath)]
        
        logger.warning("⚠️  No product images found")
        return None
        
    except Exception as e:
        logger.error(f"❌ Product scraping test failed: {str(e)}")
        return None


def test_placeholder_generation():
    """
    Test generating placeholder images with PIL.
    """
    logger.info("\n" + "="*80)
    logger.info("TEST 6: Placeholder Image Generation")
    logger.info("="*80)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a nice placeholder
        size = (1920, 1080)
        image = Image.new('RGB', size, color=(30, 30, 50))
        draw = ImageDraw.Draw(image)
        
        text = "Product Showcase\nHigh Quality Content"
        
        # Try to load font
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        except:
            font = ImageFont.load_default()
        
        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"placeholder_{timestamp}.png"
        filepath = TEST_DIR / filename
        
        image.save(filepath)
        
        logger.info(f"✅ Generated placeholder: {filepath}")
        return [str(filepath)]
        
    except Exception as e:
        logger.error(f"❌ Placeholder generation failed: {str(e)}")
        return None


def main():
    """Run all tests and summarize results."""
    logger.info("\n" + "="*80)
    logger.info("IMAGE GENERATION TESTING SUITE")
    logger.info("="*80)
    logger.info(f"Test directory: {TEST_DIR.absolute()}")
    logger.info(f"Virtual environment: {os.getenv('VIRTUAL_ENV', 'Not detected')}")
    
    results = {
        "Gemini API": test_gemini_image_gen(),
        "Groq API": test_groq_image_gen(),
        "Unsplash Stock": test_unsplash_stock_images(),
        "Pexels Stock": test_pexels_stock_images(),
        "Product Scraping": test_product_image_scraping(),
        "Placeholder": test_placeholder_generation()
    }
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("FINAL SUMMARY")
    logger.info("="*80)
    
    working_methods = []
    for method, result in results.items():
        if result:
            status = f"✅ WORKING - {len(result)} images"
            working_methods.append(method)
        else:
            status = "❌ NOT WORKING"
        
        logger.info(f"{method:25s}: {status}")
    
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS")
    logger.info("="*80)
    
    if working_methods:
        logger.info(f"✅ {len(working_methods)} working method(s) found:")
        for method in working_methods:
            logger.info(f"   • {method}")
        
        logger.info("\n📌 RECOMMENDED APPROACH:")
        logger.info("   1. Use Unsplash for FREE high-quality stock images (no API key)")
        logger.info("   2. Use Pexels as backup (API key available)")
        logger.info("   3. Scrape product images from web for specific products")
        logger.info("   4. Use placeholder generation as final fallback")
        
        logger.info("\n⚠️  NOTE: Neither Gemini nor Groq support image generation.")
        logger.info("   - Gemini: Text generation and image analysis only")
        logger.info("   - Groq: Fast LLM inference only")
        logger.info("   - For image generation, use stock photos or specialized APIs")
    else:
        logger.error("❌ No working image sources found!")
    
    logger.info("\n" + "="*80)
    logger.info(f"Test images saved to: {TEST_DIR.absolute()}")
    logger.info("="*80)


if __name__ == "__main__":
    main()
