#!/usr/bin/env python3
"""
Description generation module for creating video descriptions, tags, and metadata.
"""

import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def generate_description(content: str, product_name: str = None) -> str:
    """
    Generate YouTube-style video description from content.
    
    Args:
        content: Video script content
        product_name: Optional product name
    
    Returns:
        Formatted video description
    """
    logger.info("Generating video description")
    
    # Extract key points from content
    sentences = content.split('. ')
    key_points = sentences[:3] if len(sentences) >= 3 else sentences
    
    # Build description
    description_parts = []
    
    # Title section
    if product_name:
        description_parts.append(f"🎥 {product_name} - Complete Review & Overview\n")
    else:
        description_parts.append("🎥 Product Review & Overview\n")
    
    # Summary
    description_parts.append("📋 SUMMARY")
    description_parts.append("-" * 40)
    for point in key_points:
        if point.strip():
            description_parts.append(f"• {point.strip()}")
    description_parts.append("")
    
    # Timestamps (placeholder)
    description_parts.append("⏱️ TIMESTAMPS")
    description_parts.append("-" * 40)
    description_parts.append("00:00 - Introduction")
    description_parts.append("00:30 - Key Features")
    description_parts.append("01:30 - Performance Review")
    description_parts.append("02:30 - Final Thoughts")
    description_parts.append("")
    
    # Call to action
    description_parts.append("👍 Don't forget to LIKE, COMMENT, and SUBSCRIBE!")
    description_parts.append("🔔 Turn on notifications to never miss a video!")
    description_parts.append("")
    
    # Hashtags
    description_parts.append("🏷️ TAGS")
    description_parts.append("#ProductReview #Technology #Innovation #Unboxing")
    
    description = "\n".join(description_parts)
    
    logger.info(f"Description generated: {len(description)} characters")
    return description


def generate_tags(content: str, product_name: str = None) -> List[str]:
    """
    Generate relevant tags for the video.
    
    Args:
        content: Video content
        product_name: Optional product name
    
    Returns:
        List of tags
    """
    tags = [
        "product review",
        "technology",
        "unboxing",
        "tutorial",
        "how to",
        "comparison",
        "features",
        "innovation"
    ]
    
    if product_name:
        tags.insert(0, product_name.lower())
        tags.insert(1, f"{product_name.lower()} review")
    
    logger.info(f"Generated {len(tags)} tags")
    return tags


def generate_seo_metadata(content: str, product_name: str = None) -> Dict[str, any]:
    """
    Generate SEO metadata for video.
    
    Args:
        content: Video content
        product_name: Optional product name
    
    Returns:
        Dictionary with metadata
    """
    metadata = {
        'title': f"{product_name} Review - Complete Overview" if product_name else "Product Review",
        'description': generate_description(content, product_name),
        'tags': generate_tags(content, product_name),
        'category': 'Science & Technology',
        'language': 'en',
        'keywords': extract_keywords(content)
    }
    
    return metadata


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract important keywords from text."""
    # Simple keyword extraction (in production, use NLP libraries)
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                   'of', 'with', 'is', 'are', 'was', 'were', 'this', 'that', 'it'}
    
    words = text.lower().split()
    word_freq = {}
    
    for word in words:
        word = word.strip('.,!?;:')
        if len(word) > 3 and word not in common_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:max_keywords]]
    
    return keywords


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    test_content = "This is an amazing product. It has great features. Performance is excellent."
    desc = generate_description(test_content, "Test Product")
    print(desc)
    print("\nTags:", generate_tags(test_content, "Test Product"))
