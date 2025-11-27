#!/usr/bin/env python3
"""
Main orchestrator for automated video content generation.
This script coordinates the entire workflow from content generation to final video output.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Import project modules
from generate_content import generate_content
from generate_description import generate_description
from generate_audio import generate_audio, get_audio_duration
from generate_image import generate_images
from download_stock_video import download_stock_videos
from generate_video_single import generate_single_video
from generate_product_intro_video import generate_product_intro
from generate_video_final import generate_final_video
from convert_video import convert_video_format
from scrape_product import fetch_product_data
from video_engagement import VideoEngagementOptimizer
from generate_subtitles import generate_subtitles_from_text, add_subtitles_to_video
import re
import json

# Setup logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"video_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def extract_content_keywords(content, original_keywords):
    """
    Extract relevant keywords from generated content for better video search.
    Combines original keywords with important terms from content.
    """
    keywords = list(original_keywords) if original_keywords else []
    
    # Extract nouns and adjectives (common product descriptors)
    words = re.findall(r'\b[A-Z][a-z]+\b', content)  # Capitalized words
    important_words = [
        'gaming', 'mouse', 'keyboard', 'precision', 'ergonomic', 'RGB',
        'wireless', 'mechanical', 'optical', 'sensor', 'design', 'technology',
        'performance', 'quality', 'speed', 'accuracy', 'comfort', 'professional',
        'studio', 'headset', 'audio', 'microphone', 'streaming', 'equipment'
    ]
    
    # Find important words in content
    content_lower = content.lower()
    for word in important_words:
        if word in content_lower and word not in [k.lower() for k in keywords]:
            keywords.append(word)
    
    # Limit to top 5-7 most relevant keywords
    return keywords[:7]


class VideoContentPipeline:
    """
    Main pipeline for automated video content creation.
    Orchestrates all steps from content generation to final video output.
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.output_dir = Path("videos")
        self.output_dir.mkdir(exist_ok=True)
    
    def _build_reviewer_prompt(self, product_name, keywords, comparison_data, product_data):
        """
        Build authentic product reviewer prompt for 60-90 second video.
        """
        prompt = f"""You are a tech enthusiast creating an authentic YouTube Shorts product review.

Product: {product_name}

Create a natural, conversational 60-90 second review script that feels like talking to a friend.

Script Flow:
1. Hook (3s): Start with excitement - "So I've been using this {product_name} and..."
2. Quick Unbox (8s): First impressions, what caught your eye immediately
3. Key Features (18s): Talk about {', '.join(keywords[:5])} - use personal experiences
4. Real Testing (15s): Share actual usage scenarios - "When I was...", "I tried..."
5. Honest Take (8s): Quick pros and cons - be genuine, mention small issues too
"""
        
        if comparison_data:
            alternatives = comparison_data.get('alternatives', [])
            if alternatives:
                prompt += f"6. Comparison (10 seconds): Compare with {alternatives[0].get('product', {}).get('title', 'alternatives')}\n"
        
        prompt += f"""6. Value Check (6s): Personal take on pricing - "For the price..." or "If you're looking for..."
7. Final Word (4s): Quick recommendation - who it's perfect for

Tone: Excited friend sharing a cool find - enthusiastic but real, not scripted.
Style: Use contractions (I'm, it's, that's), say "like", "pretty", "honestly", "actually".
Pacing: Talk at normal speed with natural pauses - like explaining to a friend.
Personal Touch: Say "I noticed", "I found", "this really", "for me", "you'll".

IMPORTANT: Write exactly how you'd speak - relaxed, natural, with minor hesitations.
Use: "so", "and", "but yeah", "honestly", "actually", "like", "pretty good".
Target: 800-1000 words for natural 60-90 second pacing."""
        
        return prompt
    
    def _build_enhanced_prompt(self, product_name, keywords, comparison_data):
        """
        Build enhanced prompt with product features and comparisons.
        """
        prompt = f"Create an engaging 30-45 second product review script for {product_name}.\n\n"
        prompt += f"Key features to highlight: {', '.join(keywords[:5])}\n\n"
        
        if comparison_data:
            alternatives = comparison_data.get('alternatives', [])
            if alternatives:
                prompt += "Compare with these alternatives:\n"
                for i, alt in enumerate(alternatives[:2], 1):
                    alt_product = alt.get('product', {})
                    prompt += f"{i}. {alt_product.get('title', 'Alternative')} - ${alt_product.get('price', 'N/A')}\n"
                prompt += "\nHighlight why the main product is the best choice.\n"
        
        prompt += "\nMake it attention-grabbing, fast-paced, and conversion-focused!"
        return prompt
        
    def run_full_pipeline(self, product_name=None, keywords=None):
        """
        Execute the complete video generation pipeline.
        
        Args:
            product_name: Name of the product to feature
            keywords: List of keywords for content generation
        """
        logger.info("=" * 80)
        logger.info("Starting Enhanced Video Content Generation Pipeline")
        logger.info("=" * 80)
        
        # Initialize engagement optimizer
        engagement_optimizer = VideoEngagementOptimizer()
        
        try:
            # Step 0: Fetch real product data and comparisons
            logger.info("Step 0/10: Fetching product data and comparisons...")
            product_data = fetch_product_data(product_name, keywords)
            
            # Extract product features for enhanced content
            product_features = product_data.get("features", [])
            comparison_data = product_data.get("comparison")
            
            logger.info(f"Fetched data for {len(product_data.get('products', []))} products")
            if comparison_data:
                logger.info("Comparison data available for alternatives")
            
            # Step 1: Generate keywords from product data using LLM
            logger.info("Step 1/10: Generating review keywords from product data...")
            
            # Generate reviewer-style keywords using LLM
            from generate_content import generate_keywords_from_product
            base_keywords = keywords if keywords else []
            generated_keywords = generate_keywords_from_product(product_name, product_data, base_keywords)
            
            # Combine all keywords
            enhanced_keywords = list(set(base_keywords + product_features + generated_keywords))[:15]
            logger.info(f"Generated keywords: {enhanced_keywords}")
            
            # Step 2: Generate product reviewer script
            logger.info("Step 2/10: Generating product reviewer script...")
            
            # Generate authentic product reviewer script (60-90 seconds)
            content_prompt = self._build_reviewer_prompt(product_name, enhanced_keywords, comparison_data, product_data)
            content = generate_content(product_name, enhanced_keywords, custom_prompt=content_prompt)
            logger.info(f"Product reviewer script generated: {len(content)} characters (target: 800-1200 words for 60-90s)")
            
            # Step 2: Generate description
            logger.info("Step 2/10: Generating description...")
            description = generate_description(content)
            logger.info(f"Description generated: {description[:100]}...")
            
            # Step 3: Generate audio narration
            logger.info("Step 3/10: Generating audio narration...")
            audio_path = generate_audio(content)
            logger.info(f"Audio saved to: {audio_path}")
            
            # Step 4: Create attention-grabbing hook
            logger.info("Step 4/10: Creating engagement hook...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            hook_path = self.output_dir / f"hook_{timestamp}.mp4"
            hook_video = engagement_optimizer.create_hook_segment(product_name, str(hook_path))
            logger.info(f"Hook created: {hook_video}")
            
            # Step 5: Generate images (get diverse product images)
            logger.info("Step 5/10: Getting product images...")
            # Use real product images - get DIFFERENT images, not duplicates
            product_images = []
            scraped_products = product_data.get("products", [])
            
            # Download unique product images from ALL search results
            for product in scraped_products[:5]:  # Top 5 products for variety
                image_url = product.get("image", "")
                if image_url and image_url not in [img for img in product_images]:
                    from scrape_product import download_product_image
                    image_path = download_product_image(image_url, product_name)
                    if image_path and image_path not in product_images:
                        product_images.append(image_path)
            
            # Add Pexels images for more variety
            if len(product_images) < 5:
                generated_images = generate_images(content, product_name, count=5)
                product_images.extend(generated_images)
            
            # Use 5 images for longer review video (20% of 25 segments)
            image_paths = product_images[:5]  # 5 unique images
            logger.info(f"Using {len(image_paths)} unique product image segments")
            
            # Step 6: Download stock videos (20 for longer product review)
            logger.info("Step 6/10: Downloading contextual stock videos...")
            # Extract action words and visual keywords from script for better correlation
            content_keywords = extract_content_keywords(content, keywords)
            # Add visual action keywords for better video matching
            visual_keywords = [kw for kw in content_keywords if kw.lower() in [
                'using', 'testing', 'hands', 'unboxing', 'setup', 'features',
                'design', 'quality', 'performance', 'speed', 'working', 'trying'
            ]]
            search_keywords = visual_keywords[:5] + content_keywords[:10]
            video_paths = download_stock_videos(search_keywords, count=20)
            logger.info(f"Downloaded {len(video_paths)} contextual stock videos")
            
            # Step 7: Generate product intro video
            logger.info("Step 7/10: Generating product intro video...")
            intro_video = generate_product_intro(product_name)
            logger.info(f"Intro video created: {intro_video}")
            
            # Step 8: Generate single video segments (optimized for speed)
            logger.info("Step 8/10: Generating video segments...")
            segments = generate_single_video(image_paths, video_paths, audio_path)
            
            # Skip pacing optimization to save resources
            logger.info(f"Created {len(segments)} video segments")
            
            # Step 9: Add engagement elements (text overlays, pattern interrupts)
            logger.info("Step 9/10: Adding engagement elements...")
            audio_duration = engagement_optimizer.get_video_duration(audio_path) if os.path.exists(audio_path) else 30.0
            engagement_points = engagement_optimizer.generate_engagement_points(audio_duration, content)
            logger.info(f"Generated {len(engagement_points)} engagement points")
            
            # Step 10: Compile final video with all enhancements
            logger.info("Step 10/10: Compiling final video with engagement optimizations...")
            
            # Compile all segments in correct order: hook, intro, then video segments
            all_segments = [hook_video, intro_video] + segments
            
            # Pass None as intro since we already included it in all_segments
            final_video = generate_final_video(None, all_segments, audio_path)
            
            # Add text overlays for engagement
            final_with_overlays = str(Path(final_video).with_stem(Path(final_video).stem + "_engaged"))
            final_video = engagement_optimizer.add_text_overlay_intervals(
                final_video, engagement_points, final_with_overlays
            )
            
            # Add call-to-action
            final_with_cta = str(Path(final_video).with_stem(Path(final_video).stem + "_cta"))
            final_video = engagement_optimizer.add_call_to_action(
                final_video, "Get Yours Now!", final_with_cta
            )
            
            logger.info(f"Final engaged video created: {final_video}")
            
            # Skip subtitles (disabled by user request)
            logger.info("Skipping subtitles (disabled)")
            
            # Move to final_videos folder
            import shutil
            final_videos_dir = Path("final_videos")
            final_videos_dir.mkdir(exist_ok=True)
            
            final_output = Path(final_video)
            if not str(final_output).startswith("final_videos/"):
                final_dest = final_videos_dir / final_output.name
                shutil.copy2(final_video, final_dest)
                final_output = final_dest
            
            logger.info(f"Final video saved to: {final_output}")
            
            # Cleanup temporary files in videos folder only
            logger.info("Cleaning up temporary files...")
            videos_dir = Path("videos")
            for temp_file in videos_dir.glob("*"):
                if temp_file.is_file():
                    try:
                        temp_file.unlink()
                    except Exception as e:
                        logger.warning(f"Could not delete {temp_file}: {e}")
            logger.info("Cleanup complete")
            
            # Optional: Convert video format
            if self.config.get('convert_format'):
                logger.info("Converting video format...")
                converted = convert_video_format(str(final_output), self.config.get('output_format', 'mp4'))
                logger.info(f"Converted video: {converted}")
            
            logger.info("=" * 80)
            logger.info(f"✅ VIDEO GENERATION COMPLETE!")
            logger.info(f"📹 Final Video: {final_output}")
            logger.info(f"🎯 Enhanced with: Product comparison, Real product photos, 15 stock videos, Subtitles, Engagement hooks, Fast cuts, CTA")
            logger.info("=" * 80)
            
            return str(final_output)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            raise
    
    def run_partial_pipeline(self, start_step, end_step):
        """Run specific steps of the pipeline."""
        logger.info(f"Running partial pipeline: steps {start_step} to {end_step}")
        # Implementation for partial pipeline execution
        pass


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Automated Video Content Generation System"
    )
    parser.add_argument(
        '--product',
        type=str,
        help='Product name to generate video for'
    )
    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        help='Keywords for content generation'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--format',
        type=str,
        default='mp4',
        choices=['mp4', 'avi', 'mov', 'webm'],
        help='Output video format'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Process multiple products from products.txt'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        'output_format': args.format,
        'convert_format': True
    }
    
    # Initialize pipeline
    pipeline = VideoContentPipeline(config)
    
    # Execute
    if args.batch:
        logger.info("Running in batch mode...")
        with open('products.txt', 'r') as f:
            products = [line.strip() for line in f if line.strip()]
        
        for product in products:
            logger.info(f"Processing product: {product}")
            try:
                pipeline.run_full_pipeline(product_name=product, keywords=args.keywords)
            except Exception as e:
                logger.error(f"Failed to process {product}: {str(e)}")
                continue
    else:
        # Single product mode
        product = args.product
        if not product and os.path.exists('products.txt'):
            with open('products.txt', 'r') as f:
                product = f.readline().strip()
        
        pipeline.run_full_pipeline(product_name=product, keywords=args.keywords)


if __name__ == "__main__":
    main()
