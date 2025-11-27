#!/usr/bin/env python3
"""
Content generation module using AI/NLP for creating video scripts and narratives.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Configure APIs
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def load_keywords(keywords_file: str = "keywords.txt") -> List[str]:
    """Load keywords from file."""
    if not os.path.exists(keywords_file):
        logger.warning(f"Keywords file not found: {keywords_file}")
        return []
    
    with open(keywords_file, 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    
    logger.info(f"Loaded {len(keywords)} keywords")
    return keywords


def generate_content(product_name: Optional[str] = None, keywords: Optional[List[str]] = None, custom_prompt: Optional[str] = None) -> str:
    """
    Generate content for video narration.
    
    Args:
        product_name: Name of the product
        keywords: List of keywords to include
        custom_prompt: Custom prompt to override default generation
    
    Returns:
        Generated content text
    """
    logger.info(f"Generating content for product: {product_name}")
    
    # Load keywords if not provided
    if keywords is None:
        keywords = load_keywords()
    
    # Try using Groq API first (fastest and most reliable)
    if GROQ_API_KEY:
        try:
            return generate_content_with_groq(product_name, keywords, custom_prompt)
        except Exception as e:
            logger.warning(f"Groq content generation failed: {e}, trying alternatives")
    
    # Try using Gemini API as backup
    if GEMINI_API_KEY:
        try:
            return generate_content_with_gemini(product_name, keywords)
        except Exception as e:
            logger.warning(f"Gemini content generation failed: {e}, using template")
    
    # Template-based content generation
    content_parts = []
    
    # Introduction
    if product_name:
        content_parts.append(
            f"Welcome to our comprehensive review of the {product_name}. "
            f"In this video, we'll explore the key features, benefits, and "
            f"real-world performance of this innovative product."
        )
    else:
        content_parts.append(
            "Welcome to our product showcase. Today we're exploring "
            "cutting-edge technology that's transforming the way we work and play."
        )
    
    # Main content based on keywords
    if "features" in keywords or "technology" in keywords:
        content_parts.append(
            f"The {product_name or 'product'} stands out with its advanced features. "
            "Designed with innovation in mind, it combines cutting-edge technology "
            "with user-friendly functionality."
        )
    
    if "performance" in keywords or "productivity" in keywords:
        content_parts.append(
            "Performance is where this truly shines. Whether you're working on "
            "demanding tasks or everyday activities, you'll experience smooth, "
            "responsive operation that enhances your productivity."
        )
    
    if "design" in keywords or "lifestyle" in keywords:
        content_parts.append(
            "The design philosophy emphasizes both form and function. "
            "Every detail has been carefully crafted to complement your lifestyle "
            "while delivering exceptional performance."
        )
    
    # Conclusion
    content_parts.append(
        f"In conclusion, the {product_name or 'product'} represents excellent value "
        "for anyone looking to upgrade their setup. Thanks for watching, and don't "
        "forget to like and subscribe for more reviews!"
    )
    
    content = " ".join(content_parts)
    
    # Save to file
    with open("content.txt", 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Content generated: {len(content)} characters")
    return content


def generate_keywords_from_product(product_name: str, product_data: dict, base_keywords: List[str]) -> List[str]:
    """
    Generate reviewer-style keywords from product data using LLM.
    
    Args:
        product_name: Name of the product
        product_data: Product data from scraping (features, specs, etc.)
        base_keywords: User-provided keywords
    
    Returns:
        List of generated keywords
    """
    logger.info("Generating keywords from product data using LLM")
    
    try:
        import requests
        
        # Extract product features from data
        features = []
        if product_data:
            features.extend(product_data.get('features', []))
            if 'specs' in product_data:
                features.extend([f"{k}: {v}" for k, v in product_data.get('specs', {}).items()])
        
        # Build prompt for keyword generation
        prompt = f"""You are a product reviewer analyzing "{product_name}".

Product Features:
{chr(10).join(features[:10]) if features else 'Standard features'}

Base Keywords: {', '.join(base_keywords) if base_keywords else 'None'}

Generate 10-15 review-focused keywords that a tech reviewer would use, including:
- Performance aspects (speed, efficiency, responsiveness)
- Design elements (build quality, aesthetics, ergonomics)
- User experience terms (comfortable, intuitive, reliable)
- Technical specs (connectivity, battery, materials)
- Value propositions (affordable, premium, worth it)

Return ONLY the keywords as a comma-separated list, no explanations."""

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 150
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        keywords_text = data['choices'][0]['message']['content'].strip()
        
        # Parse keywords from response
        keywords = [k.strip() for k in keywords_text.split(',')]
        keywords = [k for k in keywords if k and len(k) < 30]  # Filter valid keywords
        
        logger.info(f"Generated {len(keywords)} keywords: {keywords}")
        return keywords[:15]
        
    except Exception as e:
        logger.warning(f"Keyword generation failed: {e}, using fallback")
        # Fallback: Extract from product features
        fallback_keywords = []
        if product_data:
            for feature in product_data.get('features', [])[:5]:
                words = feature.lower().split()
                fallback_keywords.extend([w for w in words if len(w) > 4])
        return fallback_keywords[:10]


def generate_content_with_groq(product_name: Optional[str], keywords: List[str], custom_prompt: Optional[str] = None) -> str:
    """Generate content using Groq API (Fast & Free)."""
    try:
        import requests
        
        logger.info("Using Groq API for content generation")
        
        # Use custom prompt if provided, otherwise build default
        if custom_prompt:
            prompt = custom_prompt
        else:
            # Build default prompt
            keywords_str = ", ".join(keywords) if keywords else "features, performance, design"
            
            prompt = f"""Create a 30-45 second video script for a product review video about "{product_name or 'an innovative product'}".

Include these elements:
- Engaging introduction (5-7 seconds)
- Key features and benefits focusing on: {keywords_str}
- Performance highlights
- Design and user experience
- Strong conclusion with call-to-action

Keep it conversational, enthusiastic, and suitable for voice-over narration.
Length: approximately 100-150 words.
Do not include timestamps or scene directions."""

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        content = data['choices'][0]['message']['content'].strip()
        
        # Save to file
        with open("content.txt", 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Groq generated {len(content)} characters")
        return content
        
    except Exception as e:
        logger.error(f"Groq API failed: {str(e)}")
        raise


def generate_content_with_gemini(product_name: Optional[str], keywords: List[str]) -> str:
    """Generate content using Gemini API."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash (free tier, working)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create prompt
        keywords_str = ", ".join(keywords) if keywords else "features, performance, design"
        prompt = f"""
        Write a compelling 60-second video script for a product review video about {product_name or 'this product'}.
        
        Include these topics: {keywords_str}
        
        The script should:
        - Be engaging and conversational
        - Be exactly 150-200 words (about 60 seconds when spoken)
        - Include: introduction, key features, benefits, and conclusion
        - Have a call-to-action at the end (like and subscribe)
        - Be suitable for voiceover narration
        
        Write only the script text, no extra formatting or labels.
        """
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Save to file
        with open("content.txt", 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Content generated with Gemini: {len(content)} characters")
        return content
        
    except Exception as e:
        logger.error(f"Gemini content generation failed: {str(e)}")
        raise


def generate_script_segments(content: str, segment_count: int = 5) -> List[str]:
    """
    Split content into segments for video creation.
    
    Args:
        content: Full content text
        segment_count: Number of segments to create
    
    Returns:
        List of content segments
    """
    sentences = content.split('. ')
    segment_size = max(1, len(sentences) // segment_count)
    
    segments = []
    for i in range(0, len(sentences), segment_size):
        segment = '. '.join(sentences[i:i + segment_size])
        if segment and not segment.endswith('.'):
            segment += '.'
        segments.append(segment)
    
    logger.info(f"Created {len(segments)} content segments")
    return segments


if __name__ == "__main__":
    # Test the module
    logging.basicConfig(level=logging.INFO)
    content = generate_content("Mechanical Keyboard", ["features", "productivity"])
    print(content)
    segments = generate_script_segments(content)
    for i, seg in enumerate(segments, 1):
        print(f"\nSegment {i}:\n{seg}")
