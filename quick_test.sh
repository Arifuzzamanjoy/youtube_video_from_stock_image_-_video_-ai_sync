#!/bin/bash
# Quick test to verify everything works

cd /root/Agent/content
source venv/bin/activate

echo "Testing with 'Wireless Mouse'..."
python main.py --product "Wireless Mouse" --keywords features productivity ergonomic

echo ""
echo "Check your output:"
echo "Latest video: $(ls -t videos/final_video_*.mp4 | head -1)"
