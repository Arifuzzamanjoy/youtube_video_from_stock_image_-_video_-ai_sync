#!/bin/bash
# Enhanced Video Generation Setup Script

echo "🚀 Setting up Enhanced Video Generation System..."

# Install new dependencies
echo "📦 Installing required packages..."
pip install beautifulsoup4 lxml 2>/dev/null

# Check for API keys
echo ""
echo "🔑 Checking API Keys..."

if grep -q "GROQ_API_KEY" .env 2>/dev/null; then
    echo "✅ Groq API Key found"
else
    echo "⚠️  Groq API Key missing - AI content generation may not work"
fi

if grep -q "PEXELS_API_KEY" .env 2>/dev/null; then
    echo "✅ Pexels API Key found"
else
    echo "⚠️  Pexels API Key missing - stock video downloads will be limited"
fi

if grep -q "SERPAPI_KEY" .env 2>/dev/null; then
    echo "✅ SerpAPI Key found - Real product data enabled!"
else
    echo "⚠️  SerpAPI Key missing - Product scraping will use mock data"
    echo "   Sign up at: https://serpapi.com/ (Free 100 searches/month)"
    echo "   Then add to .env: SERPAPI_KEY=your_key"
fi

echo ""
echo "🎬 New Features Available:"
echo "  ✅ Real product data fetching"
echo "  ✅ Product comparison system"
echo "  ✅ Engagement-optimized videos"
echo "  ✅ Attention-keeping hooks"
echo "  ✅ Fast cuts & pattern interrupts"
echo "  ✅ Real product images"
echo "  ✅ Call-to-action overlays"

echo ""
echo "📖 Usage:"
echo "  python main.py --product \"Gaming Mouse\" --keywords precision RGB wireless"

echo ""
echo "📊 Pipeline Steps:"
echo "  Step 0: Fetch real product data from Google Shopping"
echo "  Step 1: Generate AI content with comparisons"
echo "  Step 2-3: Generate description & audio"
echo "  Step 4: Create 3-second engagement hook"
echo "  Step 5-6: Get real images & 10 stock videos"
echo "  Step 7-8: Create intro & optimized segments"
echo "  Step 9: Add text overlays every 8 seconds"
echo "  Step 10: Compile with CTA"

echo ""
echo "✨ Ready to generate attention-keeping product videos!"
echo ""

chmod +x run.sh quick_test.sh 2>/dev/null
