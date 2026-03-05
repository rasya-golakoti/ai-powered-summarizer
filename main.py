# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\main.py
"""
AI Audio Summarizer - Main Pipeline with Enhanced Features
Follows exact architecture from your diagram
"""

import os
import sys
import time
import warnings
from pathlib import Path
from typing import List, Dict, Optional

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "3"
os.environ['TOKENIZERS_PARALLELISM'] = "false"

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import BASE_DIR, AUDIO_UPLOADS, PROCESSED_AUDIO, PLOTS, VISUALIZATION_CONFIG, OUTPUT_CONFIG
from utils.subprocess_utils import setup_ffmpeg
from audio_processing.youtube_downloader import download_youtube_audio
from audio_processing.audio_converter import convert_to_wav, get_audio_info
from models_manager import load_models, clear_models
from transcription.whisper_transcriber import transcribe_audio
from transcription.text_normalizer import normalize_text
from analysis.speaker_diarization import diarize_speakers, merge_speaker_segments
from analysis.emotion_analyzer import analyze_emotions
from analysis.topic_segmenter import segment_into_topics
from analysis.keyword_extractor import extract_keyphrases
from analysis.metrics_calculator import calculate_all_metrics
from summarization.dual_summarizer import abstractive_summary as generate_abstractive_summary, extractive_summary as generate_extractive_summary
from summarization.chapter_generator import generate_chapters_from_topics
from summarization.speaker_summarizer import summarize_speakers
from reporting.report_generator import generate_comprehensive_report

# Import enhanced features
from utils.audio_enhancer import audio_enhancer
from visualization.plot_generator import init_plot_generator
from utils.progress_indicator import progress

class AudioSummarizer:
    """Main class that follows your exact architecture diagram with enhanced features"""
    
    def __init__(self):
        self.results = {}
        self.models = {}
        self.plot_generator = None
        
    def process(self, input_path: str, output_name: Optional[str] = None) -> Dict:
        """
        Complete pipeline as per your architecture diagram with enhanced features
        
        Args:
            input_path: Path to audio file or YouTube URL
            output_name: Optional custom output name
            
        Returns:
            Complete analysis results
        """
        print("=" * 80)
        print("🎙️ AI AUDIO SUMMARIZER - COMPLETE PIPELINE WITH ENHANCED FEATURES")
        print("=" * 80)
        
        start_time = time.time()
        
        try:
            # Step 0: Setup
            progress.step_start(1, 15, "Initial Setup")
            self._setup()
            progress.step_complete(1, "Setup complete")
            
            # Step 1: Input Handling
            progress.step_start(2, 15, "Input Handling")
            audio_path = self._handle_input(input_path, output_name)
            if not audio_path:
                return {}
            progress.step_complete(2, "Input processed")
            
            # Step 1.5: Audio Enhancement (NEW)
            if OUTPUT_CONFIG.get("enhance_audio", True):
                progress.step_start(3, 15, "Audio Enhancement")
                enhanced_path = audio_enhancer.enhance_audio(audio_path)
                if enhanced_path and enhanced_path != audio_path:
                    audio_path = enhanced_path
                    print(f"   🔊 Using enhanced audio: {Path(audio_path).name}")
                progress.step_complete(3, "Audio enhanced")
            
            # Step 2: Transcription (Whisper)
            progress.step_start(4, 15, "Transcription")
            transcript = self._transcribe(audio_path)
            progress.step_complete(4, "Transcription complete")
            
            # Step 3: Normalization
            progress.step_start(5, 15, "Text Normalization")
            normalized_text = normalize_text(transcript["text"])
            progress.step_complete(5, "Text normalized")
            
            # Step 4: Speaker Diarization (Pyannote)
            progress.step_start(6, 15, "Speaker Diarization")
            speaker_segments = self._diarize_speakers(audio_path, transcript["segments"])
            progress.step_complete(6, "Speaker diarization complete")
            
            # Step 5: Summarization (BART + BERT)
            progress.step_start(7, 15, "Summarization")
            summaries = self._summarize(normalized_text)
            progress.step_complete(7, "Summarization complete")
            
            # Step 6: Emotion Detection (Pretrained models)
            progress.step_start(8, 15, "Emotion Analysis")
            emotions = analyze_emotions(normalized_text)
            progress.step_complete(8, "Emotion analysis complete")
            
            # Step 7: Topic Segmentation & Timeline
            progress.step_start(9, 15, "Topic Segmentation")
            topics = segment_into_topics(normalized_text, transcript["segments"])
            progress.step_complete(9, "Topic segmentation complete")
            
            # Step 8: Chapter Generation
            progress.step_start(10, 15, "Chapter Generation")
            chapters = generate_chapters_from_topics(topics)
            progress.step_complete(10, "Chapters generated")
            
            # Step 9: Keyword Extraction (KeyBERT)
            progress.step_start(11, 15, "Keyword Extraction")
            keywords = extract_keyphrases(normalized_text)
            progress.step_complete(11, "Keywords extracted")
            
            # Step 10: Speaker Summaries
            progress.step_start(12, 15, "Speaker Summarization")
            speaker_summaries = summarize_speakers(speaker_segments)
            progress.step_complete(12, "Speaker summaries generated")
            
            # Step 11: Metrics (ROUGE-L, BLEU, BERT-F1)
            progress.step_start(13, 15, "Metrics Calculation")
            metrics = calculate_all_metrics(
                original_text=normalized_text,
                summary_text=summaries["abstractive"],
                reference_summary=summaries.get("extractive", "")
            )
            progress.step_complete(13, "Metrics calculated")
            
            # Step 12: Compile Results FIRST (BEFORE plots)
            self.results = {
                "input_info": {
                    "source": input_path,
                    "audio_file": Path(audio_path).name,
                    "duration": transcript.get("duration", 0),
                    "enhanced": 'enhanced_path' in locals() and enhanced_path != audio_path
                },
                "transcription": {
                    "full_text": transcript["text"],
                    "normalized_text": normalized_text,
                    "segments": transcript["segments"],
                    "word_count": len(normalized_text.split()),
                    "segment_count": len(transcript["segments"])
                },
                "speaker_analysis": {
                    "segments": speaker_segments,
                    "speaker_count": len(set([s.get("speaker", "UNKNOWN") for s in speaker_segments])),
                    "summaries": speaker_summaries
                },
                "summarization": {
                    "abstractive": summaries["abstractive"],
                    "extractive": summaries.get("extractive", ""),
                    "abstractive_words": len(summaries["abstractive"].split()),
                    "extractive_words": len(summaries.get("extractive", "").split())
                },
                "emotion_analysis": emotions,
                "topic_analysis": {
                    "topics": topics,
                    "topic_count": len(topics)
                },
                "chapter_analysis": {
                    "chapters": chapters,
                    "chapter_count": len(chapters)
                },
                "keyword_analysis": {
                    "keywords": keywords,
                    "keyword_count": len(keywords)
                },
                "quality_metrics": metrics,
                "processing_info": {
                    "total_time": time.time() - start_time,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "audio_enhanced": 'enhanced_path' in locals() and enhanced_path != audio_path
                }
            }
            
            # Step 13: Visualizations (AFTER results are compiled)
            plot_files = {}
            if VISUALIZATION_CONFIG["enabled"]:
                progress.step_start(14, 15, "Generating Visualizations")
                
                # Ensure plots directory exists
                PLOTS.mkdir(exist_ok=True, parents=True)
                
                # Initialize plot generator
                self.plot_generator = init_plot_generator(PLOTS)
                
                # Generate plots WITH the compiled results
                plot_files = self.plot_generator.generate_all_plots(self.results)
                
                # Add visualization info to results
                if plot_files:
                    self.results["visualization"] = {
                        "plots_generated": len(plot_files),
                        "plot_files": list(plot_files.keys())
                    }
                    print(f"   ✅ Generated {len(plot_files)} visualizations")
                else:
                    print(f"   ⚠️ No visualizations were generated")
                
                progress.step_complete(14, "Visualizations generated")
            
            # Step 14: Generate Outputs & Dashboard
            progress.step_start(15, 15, "Generating Outputs")
            self._generate_outputs(output_name or Path(audio_path).stem)
            progress.step_complete(15, "Outputs generated")
            
            print("\n" + "=" * 80)
            print("✅ PROCESSING COMPLETE!")
            print("=" * 80)
            
            self._print_summary()
            
            return self.results
            
        except Exception as e:
            progress.step_error(0, f"Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
        finally:
            clear_models()
    
    def _setup(self):
        """Initialize the system with enhanced features"""
        print("\n🔧 STEP 0: SETUP")
        setup_ffmpeg()
        self.models = load_models()
        print("   ✅ Models loaded")
        
        # Ensure directories exist
        for dir_name in ["audio_uploads", "processed_audio", "transcripts", "summaries", "reports", "plots"]:
            (BASE_DIR / dir_name).mkdir(exist_ok=True)
    
    def _handle_input(self, input_path: str, output_name: Optional[str]) -> Optional[str]:
        """Step 1: Input Handling (YouTube/Local) with progress"""
        print("\n🔊 STEP 1: INPUT HANDLING")
        
        # Handle YouTube URLs
        if input_path.startswith(("http://", "https://")):
            with progress.spinner("Downloading from YouTube"):
                print("   📥 Downloading from YouTube...")
                audio_path = download_youtube_audio(input_path, output_name)
                if not audio_path:
                    print("   ❌ Failed to download YouTube audio")
                    return None
        else:
            # Local file
            audio_path = input_path
            if not Path(audio_path).exists():
                print(f"   ❌ File not found: {audio_path}")
                return None
        
        # Convert to WAV if needed
        if not audio_path.endswith('.wav'):
            with progress.spinner("Converting to WAV"):
                print("   🔄 Converting to WAV...")
                wav_path = str(PROCESSED_AUDIO / f"{Path(audio_path).stem}.wav")
                if convert_to_wav(audio_path, wav_path, enhance=OUTPUT_CONFIG.get("enhance_audio", True)):
                    audio_path = wav_path
                else:
                    print("   ❌ Audio conversion failed")
                    return None
        
        # Get audio info
        info = get_audio_info(audio_path)
        duration = info.get("format", {}).get("duration", 0)
        print(f"   ✅ Audio ready: {duration:.1f}s")
        
        return audio_path
    
    def _transcribe(self, audio_path: str) -> Dict:
        """Step 2: Transcription (Whisper) with progress"""
        print("\n📝 STEP 2: TRANSCRIPTION (Whisper)")
        
        with progress.spinner("Transcribing with Whisper"):
            result = transcribe_audio(audio_path)
            
            if not result or "text" not in result:
                print("   ❌ Transcription failed")
                return {"text": "", "segments": [], "duration": 0}
            
            word_count = len(result["text"].split())
            print(f"   ✅ Transcribed: {word_count} words, {len(result['segments'])} segments")
            
            return result
    
    def _diarize_speakers(self, audio_path: str, segments: List[Dict]) -> List[Dict]:
        """Step 4: Speaker Diarization (Pyannote) with progress"""
        print("\n👥 STEP 4: SPEAKER DIARIZATION (Pyannote)")
        
        with progress.spinner("Identifying speakers"):
            try:
                from analysis.speaker_diarization import diarize_speakers, merge_speaker_segments
                
                # Get audio duration for fallback
                import librosa
                duration = librosa.get_duration(filename=audio_path)
                
                # Run diarization
                speaker_segments = diarize_speakers(audio_path, duration)
                
                # Merge with transcript segments
                merged_segments = merge_speaker_segments(speaker_segments, segments)
                
                # Count unique speakers
                unique_speakers = set([s.get("speaker", "UNKNOWN") for s in merged_segments])
                print(f"   ✅ Identified {len(unique_speakers)} speakers: {', '.join(sorted(unique_speakers))}")
                
                return merged_segments
                
            except Exception as e:
                print(f"   ⚠️ Speaker diarization error: {e}")
                # Fallback: assign all to one speaker
                for segment in segments:
                    segment["speaker"] = "SPEAKER_00"
                return segments
    
    def _summarize(self, text: str) -> Dict:
        """Step 5: Summarization (BART + BERT) with progress"""
        print("\n📋 STEP 5: SUMMARIZATION")
        
        with progress.spinner("Generating abstractive summary"):
            print("   🤖 Abstractive (BART)...")
            abstractive = generate_abstractive_summary(text)
        
        with progress.spinner("Generating extractive summary"):
            print("   🔍 Extractive (BERT)...")
            extractive = generate_extractive_summary(text)
        
        print(f"   ✅ Abstractive: {len(abstractive.split())} words")
        print(f"   ✅ Extractive: {len(extractive.split())} words")
        
        return {
            "abstractive": abstractive,
            "extractive": extractive
        }
    
    def _generate_outputs(self, base_name: str):
        """Step 14: Generate Outputs & Dashboard with enhanced reporting"""
        print("\n📊 GENERATING OUTPUTS")
        
        # Save transcript
        transcript_file = BASE_DIR / "transcripts" / f"{base_name}.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(self.results["transcription"]["full_text"])
        print(f"   📄 Transcript: {transcript_file.name}")
        
        # Save summary
        summary_file = BASE_DIR / "summaries" / f"{base_name}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("ABSTRACTIVE SUMMARY:\n")
            f.write(self.results["summarization"]["abstractive"])
            f.write("\n\nEXTRACTIVE SUMMARY:\n")
            f.write(self.results["summarization"]["extractive"])
        print(f"   📄 Summary: {summary_file.name}")
        
        # Generate comprehensive report
        report_file = generate_comprehensive_report(self.results, base_name)
        print(f"   📊 Report: {report_file.name}")
        
        # Print metrics
        metrics = self.results["quality_metrics"]
        print(f"   📈 Metrics - ROUGE-L: {metrics.get('rouge_l', 0):.3f}, "
              f"BLEU: {metrics.get('bleu', 0):.3f}, "
              f"BERT-F1: {metrics.get('bert_f1', 0):.3f}")
        
        # Show visualization info
        if VISUALIZATION_CONFIG["enabled"]:
            plot_count = self.results.get("visualization", {}).get("plots_generated", 0)
            if plot_count > 0:
                print(f"   🎨 Generated {plot_count} visualizations in plots/ directory")
    
    def _print_summary(self):
        """Print final summary with enhanced information"""
        print("\n" + "=" * 80)
        print("📋 FINAL SUMMARY")
        print("=" * 80)
        
        results = self.results
        
        print(f"\n📊 STATISTICS:")
        print(f"   • Duration: {results['input_info'].get('duration', 0):.1f}s")
        print(f"   • Words: {results['transcription']['word_count']}")
        print(f"   • Speakers: {results['speaker_analysis']['speaker_count']}")
        print(f"   • Topics: {results['topic_analysis']['topic_count']}")
        print(f"   • Chapters: {results['chapter_analysis']['chapter_count']}")
        print(f"   • Processing time: {results['processing_info']['total_time']:.1f}s")
        
        if results['input_info'].get('enhanced', False):
            print(f"   • Audio Enhanced: ✅ Yes")
        
        print(f"\n🎯 KEY METRICS:")
        metrics = results["quality_metrics"]
        print(f"   • ROUGE-L: {metrics.get('rouge_l', 0):.3f}")
        print(f"   • BLEU: {metrics.get('bleu', 0):.3f}")
        print(f"   • BERT-F1: {metrics.get('bert_f1', 0):.3f}")
        
        print(f"\n📋 ABSTRACTIVE SUMMARY:")
        summary = results["summarization"]["abstractive"]
        if summary:
            if len(summary) > 200:
                print(f"   {summary[:200]}...")
            else:
                print(f"   {summary}")
        else:
            print("   No abstractive summary generated")
        
        print(f"\n🔑 TOP KEYWORDS:")
        keywords = results["keyword_analysis"]["keywords"][:5]
        if keywords:
            for kw, score in keywords:
                print(f"   • {kw} ({score:.3f})")
        else:
            print("   No keywords extracted")
        
        print(f"\n📁 OUTPUT FILES:")
        audio_file = Path(results['input_info']['audio_file']).stem
        print(f"   • Transcript: transcripts/{audio_file}.txt")
        print(f"   • Summary: summaries/{audio_file}.txt")
        print(f"   • Report: reports/{audio_file}.md")
        
        if VISUALIZATION_CONFIG["enabled"]:
            plot_count = results.get("visualization", {}).get("plots_generated", 0)
            if plot_count > 0:
                print(f"   • Visualizations: {plot_count} plots in plots/ directory")
        
        print("\n" + "=" * 80)


def download_from_youtube(url):
    """Download YouTube audio with Deno support"""
    import subprocess
    from pathlib import Path
    
    print("🎬 Using Deno JavaScript runtime...")
    
    # Ensure Deno is available
    try:
        deno_version = subprocess.run(["deno", "--version"], 
                                     capture_output=True, text=True)
        if deno_version.returncode == 0:
            print(f"   Deno version: {deno_version.stdout.split()[1]}")
    except:
        print("❌ Deno not found. Please install Deno first.")
        return None
    
    # Updated command with Deno
    cmd = [
        "yt-dlp",
        "--js-runtime", "deno",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--no-playlist",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-o", "audio_uploads/%(title)s.%(ext)s",
        url
    ]
    
    print("⬇️ Downloading...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        # Find the downloaded file
        audio_files = list(Path("audio_uploads").glob("*.mp3"))
        if audio_files:
            latest = max(audio_files, key=lambda p: p.stat().st_mtime)
            return str(latest)
    
    return None


def main():
    """Main function with enhanced argument parsing"""
    import argparse
    from config import OUTPUT_CONFIG, VISUALIZATION_CONFIG, PROGRESS_CONFIG
    
    parser = argparse.ArgumentParser(description="AI Audio Summarizer with Enhanced Features")
    parser.add_argument("input", help="Audio file or YouTube URL")
    parser.add_argument("--output", "-o", help="Output base name")
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Quick mode (skip some analysis)")
    parser.add_argument("--no-enhance", action="store_true",
                       help="Disable audio enhancement")
    parser.add_argument("--no-plots", action="store_true",
                       help="Disable visualizations")
    parser.add_argument("--no-progress", action="store_true",
                       help="Disable progress indicators")
    
    args = parser.parse_args()
    
    # Apply command line overrides
    if args.no_enhance:
        OUTPUT_CONFIG["enhance_audio"] = False
    
    if args.no_plots:
        VISUALIZATION_CONFIG["enabled"] = False
    
    if args.no_progress:
        PROGRESS_CONFIG["enabled"] = False
    
    summarizer = AudioSummarizer()
    results = summarizer.process(args.input, args.output)
    
    if results and OUTPUT_CONFIG.get("auto_open_report", False):
        try:
            audio_file = Path(results['input_info']['audio_file']).stem
            report_path = BASE_DIR / "reports" / f"{audio_file}.md"
            if report_path.exists():
                import webbrowser
                webbrowser.open(f"file://{report_path}")
        except:
            pass


if __name__ == "__main__":
    main()

# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer_final_project\audio_uploads\QA-01_1.mp3