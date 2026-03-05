# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\quick_summarize.py
"""
Quick Summary Tool - Get summary without detailed analysis
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import AudioSummarizer

def main():
    parser = argparse.ArgumentParser(
        description="⚡ Quick Audio Summary - Fast summary without detailed analysis"
    )
    parser.add_argument("input", help="Audio file path or YouTube URL")
    parser.add_argument("--output", "-o", help="Save summary to file")
    parser.add_argument("--model", "-m", choices=["fast", "accurate"], 
                       default="fast", help="Model speed (default: fast)")
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    print(f"⚡ Processing: {args.input}")
    
    config = {
        "enable_speaker_diarization": False,
        "enable_emotion_analysis": False,
        "enable_topic_segmentation": False,
        "enable_visualizations": False,
        "fast_mode": args.model == "fast",
        "output_formats": [],
        "clean_intermediate": True,
        "verbose": False
    }
    
    summarizer = AudioSummarizer(config=config)
    summary = summarizer.quick_summary(args.input)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"✅ Summary saved to: {args.output}")
    else:
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        print(summary)

if __name__ == "__main__":
    main()