# Product Reviewer Video Updates

## Overview
Updated the video generation system to create **longer, authentic product review videos (60-90 seconds)** with AI-generated keywords and reviewer-style scripts that align video length with audio narration.

---

## Key Changes

### 1. **Longer Video Duration (60-90 seconds)**
- **Previous**: 30-45 seconds (10 segments)
- **Current**: 60-90 seconds (25 segments)
- **Pattern**: V-V-V-V-I (4 videos + 1 image, repeating 5 times)
- **Total**: 20 stock videos + 5 product images
- **Segment Duration**: 3.5 seconds each (increased from 3.0s)

### 2. **AI-Generated Keywords from Product Data**
New function: `generate_keywords_from_product()` in `generate_content.py`

**Workflow**:
```
Product Data → LLM Analysis → Reviewer Keywords → Script Generation
```

**Generated Keywords Include**:
- Performance aspects (speed, efficiency, responsiveness)
- Design elements (build quality, aesthetics, ergonomics)  
- User experience (comfortable, intuitive, reliable)
- Technical specs (connectivity, battery, materials)
- Value propositions (affordable, premium, worth it)

**Example**:
```python
Input: "Wireless Gaming Mouse"
Base Keywords: ["gaming", "precision"]

Generated Keywords:
→ "wireless", "RGB", "ergonomic", "DPI", "battery life", 
  "build quality", "lightweight", "responsive", "customizable",
  "premium feel", "worth it", "performance", "gaming experience"
```

### 3. **Authentic Product Reviewer Script**
New prompt builder: `_build_reviewer_prompt()` in `main.py`

**Script Structure** (60-90 seconds):
1. **Hook** (5s): "Hey guys, today I'm reviewing the..."
2. **Unboxing/First Impressions** (10s): What's in the box, build quality
3. **Key Features** (20s): Main features and specifications
4. **Real-World Testing** (15s): Actual usage scenarios
5. **Pros & Cons** (10s): Honest strengths and weaknesses
6. **Comparison** (10s): vs alternatives (if available)
7. **Value Assessment** (5s): Is it worth the price?
8. **Final Verdict** (5s): Who should buy this?

**Tone**: Enthusiastic but honest, conversational, uses "I", "you", personal experiences

**Style**: Natural pacing with filler words ("so", "now", "actually", "honestly")

**Target**: 800-1200 words (60-90 second narration)

### 4. **Video Length Auto-Sync with Audio**
Updated: `add_audio_to_video()` in `generate_video_final.py`

**Previous Behavior**:
- Video always stretched to audio if shorter
- No adjustment if video was longer

**New Behavior**:
- **Automatically syncs video duration to match audio**
- If difference > 2 seconds: adjusts video speed (setpts filter)
- If difference ≤ 2 seconds: no adjustment needed
- Ensures reviewer pacing aligns perfectly with narration

**Example**:
```
Audio: 75 seconds (reviewer script)
Video: 87.5 seconds (25 segments × 3.5s)
→ Speed adjustment: 0.86x (slight slowdown)
→ Final: 75 seconds perfectly synced
```

---

## Updated Pipeline Workflow

```
Step 1: Scrape Product Data
   ↓
Step 2: Generate Keywords (LLM) ← NEW
   ├─ Base keywords (user input)
   ├─ Product features (scraped)
   └─ AI-generated reviewer keywords
   ↓
Step 3: Generate Reviewer Script (800-1200 words) ← UPDATED
   ├─ Authentic reviewer tone
   ├─ 8-section structure
   └─ Natural conversational style
   ↓
Step 4: Generate Audio (60-90s narration) ← UPDATED
   ├─ Validates text length (>500 chars)
   └─ Creates voiceover
   ↓
Step 5: Download Assets
   ├─ 20 stock videos (portrait 9:16)
   └─ 5 product images (unique sources)
   ↓
Step 6: Create 25 Video Segments (3.5s each) ← UPDATED
   └─ Pattern: V-V-V-V-I (×5 repeats)
   ↓
Step 7: Concatenate with Transitions
   └─ 0.2s fade transitions
   ↓
Step 8: Sync Video to Audio Duration ← NEW
   ├─ Auto-adjust video speed
   └─ Perfect alignment with reviewer pacing
   ↓
Step 9: Add Engagement Overlays
   ├─ Hook (first 3s)
   ├─ Text overlays
   └─ CTA (last 3s)
   ↓
Final Output: 60-90s Product Review Video
```

---

## Technical Specifications

### Video Format
- **Aspect Ratio**: 9:16 (1080×1920) - YouTube Shorts/Reels
- **Frame Rate**: 30 FPS
- **Codec**: H.264 (libx264)
- **Quality**: CRF 23 (high quality)
- **Audio**: AAC 192k

### Content Specifications
- **Script Length**: 800-1200 words
- **Character Count**: ~5000-7500 characters
- **Audio Duration**: 60-90 seconds
- **Video Segments**: 25 total (20 videos + 5 images)
- **Segment Duration**: 3.5 seconds each
- **Transition**: 0.2s fade

### Keyword Generation
- **Source**: Product features + user keywords + AI analysis
- **Count**: 10-15 reviewer-focused keywords
- **API**: Groq (llama-3.1-8b-instant)
- **Fallback**: Extract from product features

---

## File Changes Summary

### Modified Files

1. **`main.py`**
   - Added keyword generation step (Step 1)
   - Updated to 20 videos + 5 images
   - New `_build_reviewer_prompt()` method
   - Updated logging for longer videos

2. **`generate_content.py`**
   - New `generate_keywords_from_product()` function
   - LLM-based keyword extraction from product data
   - Returns 10-15 reviewer-style keywords

3. **`generate_video_single.py`**
   - Updated pattern: 25 segments (was 10)
   - Segment duration: 3.5s (was 3.0s)
   - Pattern: V-V-V-V-I repeated 5 times

4. **`generate_video_final.py`**
   - Auto-sync video to audio duration
   - Speed adjustment for >2s difference
   - Better logging for sync operations

5. **`generate_audio.py`**
   - Validates text length (warns if <500 chars)
   - Logs character count for 60-90s check

---

## Usage Example

```bash
# Run with product name and optional base keywords
python main.py --product "Wireless Gaming Mouse" --keywords gaming precision

# System will:
# 1. Scrape product data
# 2. Generate 10-15 keywords using LLM
#    → "wireless", "ergonomic", "DPI", "RGB", "battery", "responsive", etc.
# 3. Create 800-1200 word reviewer script
#    → "Hey guys, today I'm reviewing the Wireless Gaming Mouse..."
# 4. Generate 60-90 second audio narration
# 5. Download 20 videos + 5 images
# 6. Create 25 segments (87.5s total)
# 7. Auto-sync to audio duration (60-90s)
# 8. Output: final_videos/final_video_*.mp4
```

---

## Benefits

✅ **Longer Content**: 60-90s matches typical product review length  
✅ **Authentic Tone**: Sounds like real reviewer, not scripted ad  
✅ **Smart Keywords**: LLM extracts relevant terms from product data  
✅ **Perfect Sync**: Video automatically aligns with audio pacing  
✅ **Better Engagement**: Structured review format (hook → features → verdict)  
✅ **Natural Flow**: Conversational style with personal experiences  
✅ **Honest Reviews**: Includes pros & cons, comparisons, value assessment  

---

## Next Steps

To test the new system:

```bash
cd /root/Agent/content
source venv/bin/activate
python main.py --product "Gaming Mechanical Keyboard" --keywords mechanical RGB switches
```

Expected output:
- Script: ~1000 words with reviewer structure
- Keywords: ~12 AI-generated terms
- Audio: 70-80 seconds
- Video: 60-90 seconds (auto-synced)
- Format: 9:16 vertical (1080×1920)

---

**Last Updated**: November 26, 2025  
**Target Platform**: YouTube Shorts, Instagram Reels, TikTok  
**Video Type**: Authentic Product Reviews (60-90s)
