# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\batch_processor.py
"""
Batch Processor - Process multiple audio files
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import AudioSummarizer

def main():
    parser = argparse.ArgumentParser(
        description="📦 Batch Audio Processor - Process multiple audio files"
    )
    parser.add_argument("folder", help="Folder containing audio files")
    parser.add_argument("--output", "-o", help="Output directory for results")
    parser.add_argument("--config", "-c", help="Configuration JSON file")
    parser.add_argument("--resume", action="store_true", 
                       help="Resume from previous batch")
    parser.add_argument("--threads", "-t", type=int, default=1,
                       help="Number of parallel threads (default: 1)")
    parser.add_argument("--report", "-r", action="store_true",
                       help="Generate batch report")
    
    args = parser.parse_args()
    
    # Load configuration
    config = {
        "enable_speaker_diarization": True,
        "enable_emotion_analysis": True,
        "enable_topic_segmentation": True,
        "enable_visualizations": True,
        "fast_mode": False,
        "output_formats": ["json", "md"],
        "clean_intermediate": True,
        "verbose": False
    }
    
    if args.config:
        try:
            with open(args.config, 'r') as f:
                user_config = json.load(f)
                config.update(user_config)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            return
    
    # Set output directory
    if args.output:
        from config import set_output_directory
        set_output_directory(args.output)
    
    # Create summarizer
    summarizer = AudioSummarizer(config=config)
    
    print(f"\n📦 BATCH PROCESSING STARTED")
    print(f"   Folder: {args.folder}")
    print(f"   Threads: {args.threads}")
    print(f"   Resume: {args.resume}")
    print("-" * 50)
    
    # Process batch
    results = summarizer.batch_process(args.folder)
    
    # Generate batch report
    if args.report and results:
        generate_batch_report(results, args.folder)

def generate_batch_report(results, folder_path):
    """Generate comprehensive batch report"""
    from config import BASE_DIR
    
    report_data = {
        "batch_info": {
            "folder": folder_path,
            "processing_date": datetime.now().isoformat(),
            "total_files": len(results),
            "successful_files": len([r for r in results if r])
        },
        "statistics_summary": {
            "total_words": sum(r["statistics"]["word_count"] for r in results if r),
            "total_speakers": sum(r["statistics"]["speaker_count"] for r in results if r),
            "total_tasks": sum(r["statistics"]["task_count"] for r in results if r),
            "avg_processing_time": "N/A"
        },
        "file_results": []
    }
    
    for result in results:
        if result:
            report_data["file_results"].append({
                "filename": result["metadata"]["audio_filename"],
                "word_count": result["statistics"]["word_count"],
                "speaker_count": result["statistics"]["speaker_count"],
                "task_count": result["statistics"]["task_count"],
                "processing_time": result["metadata"]["processing_time"]
            })
    
    # Save batch report
    batch_report_path = BASE_DIR / "reports" / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    batch_report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(batch_report_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📊 BATCH REPORT: {batch_report_path}")
    
    # Print summary
    print(f"\n📋 BATCH SUMMARY:")
    print(f"   Total files: {report_data['batch_info']['total_files']}")
    print(f"   Successful: {report_data['batch_info']['successful_files']}")
    print(f"   Total words: {report_data['statistics_summary']['total_words']}")
    print(f"   Total tasks: {report_data['statistics_summary']['total_tasks']}")

if __name__ == "__main__":
    main()