# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\reporting\report_generator.py

"""
Report Generator for AI Audio Summarizer with Enhanced Features
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from config import SUMMARIES_DIR, TRANSCRIPTS_DIR, REPORTS_DIR, PLOTS_DIR
from utils.file_utils import save_text_file, save_json_file

class ReportGenerator:
    """Generate comprehensive reports from analysis results"""
    
    def __init__(self, base_name: str = "report"):
        """
        Initialize report generator
        
        Args:
            base_name: Base name for output files
        """
        self.base_name = base_name
        self.report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_comprehensive_report(self, analysis_results: Dict) -> Path:
        """
        Generate comprehensive report from analysis results
        
        Args:
            analysis_results: Dictionary with all analysis results
            
        Returns:
            Path to generated report file
        """
        print(f"   📊 Generating comprehensive report: {self.base_name}")
        
        # Create markdown report
        markdown_content = self._generate_markdown_report(analysis_results)
        
        # Save markdown report
        report_path = REPORTS_DIR / f"{self.base_name}.md"
        save_text_file(markdown_content, report_path)
        
        # Save JSON metadata
        json_path = REPORTS_DIR / f"{self.base_name}_metadata.json"
        save_json_file(analysis_results, json_path)
        
        # Copy plots to reports directory for easy access
        self._copy_plots_to_reports(analysis_results)
        
        print(f"   ✅ Report saved to: {report_path.name}")
        return report_path
    
    def _generate_markdown_report(self, results: Dict) -> str:
        """Generate enhanced markdown report with plots"""
        
        # Get base info
        input_info = results.get('input_info', {})
        audio_file = input_info.get('audio_file', 'Unknown')
        duration = input_info.get('duration', 0)
        
        # Get plot files
        plot_files = results.get('visualization', {}).get('plot_files', [])
        
        markdown = f"""# 🎙️ Audio Analysis Report

**Generated:** {self.report_date}
**Audio File:** {audio_file}
**Duration:** {duration:.1f} seconds
**Processing Time:** {results.get('processing_info', {}).get('total_time', 0):.1f}s
**Audio Enhanced:** {'✅ Yes' if input_info.get('enhanced', False) else '❌ No'}

## 📊 Executive Summary

### 🔑 Key Insights
- **Duration:** {duration:.1f}s
- **Word Count:** {results.get('transcription', {}).get('word_count', 0):,}
- **Speakers:** {results.get('speaker_analysis', {}).get('speaker_count', 0)}
- **Topics:** {results.get('topic_analysis', {}).get('topic_count', 0)}
- **Chapters:** {results.get('chapter_analysis', {}).get('chapter_count', 0)}

### 📋 Abstractive Summary
{results.get('summarization', {}).get('abstractive', 'No summary available')}

### 🎯 Quality Metrics
"""
        
        # Add metrics
        metrics = results.get('quality_metrics', {})
        if metrics:
            markdown += f"- **ROUGE-L**: {metrics.get('rouge_l', 0):.3f}\n"
            markdown += f"- **BLEU**: {metrics.get('bleu', 0):.3f}\n"
            markdown += f"- **BERT-F1**: {metrics.get('bert_f1', 0):.3f}\n"
            if 'compression_ratio' in metrics:
                markdown += f"- **Compression Ratio**: {metrics.get('compression_ratio', 0):.3f}\n"
        
        # Add visualizations if available
        if plot_files:
            markdown += "\n## 📈 Visualizations\n\n"
            
            # Check which plots were generated
            if 'metrics' in plot_files:
                markdown += f"![Metrics Plot]({self.base_name}_metrics.png)\n*Figure 1: Accuracy Metrics*\n\n"
            
            if 'emotions' in plot_files:
                markdown += f"![Emotions Plot]({self.base_name}_emotions.png)\n*Figure 2: Emotion Analysis*\n\n"
            
            if 'keywords' in plot_files:
                markdown += f"![Keywords Plot]({self.base_name}_keywords.png)\n*Figure 3: Keyword Analysis*\n\n"
            
            if 'speakers' in plot_files:
                markdown += f"![Speakers Plot]({self.base_name}_speakers.png)\n*Figure 4: Speaker Analysis*\n\n"
            
            if 'timeline' in plot_files:
                markdown += f"![Timeline Plot]({self.base_name}_timeline.png)\n*Figure 5: Chapter Timeline*\n\n"
        
        # Add detailed sections
        markdown += """
## 🎭 Detailed Analysis

### 👥 Speaker Analysis
"""
        
        speaker_stats = results.get('speaker_analysis', {}).get('statistics', {})
        if speaker_stats:
            for speaker, stats in speaker_stats.items():
                words = stats.get('words', 0)
                duration = stats.get('duration', 0)
                markdown += f"- **{speaker}**: {words:,} words, {duration:.1f}s speaking time\n"
        else:
            # Calculate from segments
            speaker_durations = {}
            speaker_words = {}
            for seg in results.get('speaker_analysis', {}).get('segments', []):
                speaker = seg.get('speaker', 'UNKNOWN')
                duration = seg.get('end', 0) - seg.get('start', 0)
                words = len(seg.get('text', '').split())
                
                speaker_durations[speaker] = speaker_durations.get(speaker, 0) + duration
                speaker_words[speaker] = speaker_words.get(speaker, 0) + words
            
            for speaker in speaker_durations:
                markdown += f"- **{speaker}**: {speaker_words.get(speaker, 0):,} words, {speaker_durations[speaker]:.1f}s speaking time\n"
        
        markdown += "\n### 🔑 Keyword Analysis\n"
        
        keywords = results.get('keyword_analysis', {}).get('keywords', [])
        if keywords:
            top_keywords = keywords[:10]
            for i, (kw, score) in enumerate(top_keywords, 1):
                markdown += f"{i}. **{kw}** ({score:.3f})\n"
        else:
            markdown += "No keywords extracted.\n"
        
        markdown += "\n### 📚 Chapter Overview\n"
        
        chapters = results.get('chapter_analysis', {}).get('chapters', [])
        if chapters:
            for chapter in chapters[:5]:  # Show first 5 chapters
                title = chapter.get('title', 'Untitled')
                start = chapter.get('time_start', 0)
                end = chapter.get('time_end', 0)
                markdown += f"- **{title}**: {start/60:.1f}m - {end/60:.1f}m\n"
        else:
            markdown += "No chapters generated.\n"
        
        markdown += "\n### ✅ Action Items\n"
        
        tasks = results.get('task_analysis', {}).get('tasks', [])
        if tasks:
            for i, task in enumerate(tasks[:5], 1):
                markdown += f"{i}. {task}\n"
        else:
            markdown += "No specific action items identified.\n"
        
        markdown += f"""
## 📁 Generated Files

All analysis files have been saved with base name: **{self.base_name}**

### 📂 Directory Structure
- **Transcripts**: `{TRANSCRIPTS_DIR}/{self.base_name}_*.txt`
- **Summaries**: `{SUMMARIES_DIR}/{self.base_name}_*.txt`
- **Reports**: `{REPORTS_DIR}/{self.base_name}_*.md`
- **Visualizations**: `{PLOTS_DIR}/{self.base_name}_*.png`
- **Metadata**: `{REPORTS_DIR}/{self.base_name}_*.json`

### 📄 File Details
"""
        
        # List generated files
        file_types = [
            ("Full Transcript", f"{self.base_name}.txt"),
            ("Speaker Transcript", f"{self.base_name}_speakers.txt"),
            ("Summary", f"{self.base_name}.txt"),
            ("Report", f"{self.base_name}.md"),
            ("Metadata", f"{self.base_name}_metadata.json"),
        ]
        
        for file_desc, filename in file_types:
            file_path = REPORTS_DIR / filename if 'metadata' in file_desc.lower() else \
                       TRANSCRIPTS_DIR / filename if 'transcript' in file_desc.lower() else \
                       SUMMARIES_DIR / filename if 'summary' in file_desc.lower() else \
                       REPORTS_DIR / filename
            
            if file_path.exists():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                markdown += f"- **{file_desc}**: `{filename}` ({size_mb:.2f} MB)\n"
        
        # List plot files
        if plot_files:
            markdown += "\n### 🎨 Generated Visualizations\n"
            for plot_type in plot_files:
                plot_path = PLOTS_DIR / f"{self.base_name}_{plot_type}.png"
                if plot_path.exists():
                    size_mb = plot_path.stat().st_size / (1024 * 1024)
                    markdown += f"- **{plot_type.title()} Plot**: `{self.base_name}_{plot_type}.png` ({size_mb:.2f} MB)\n"
        
        markdown += """

---

*Report generated by AI Audio Summarizer v2.0 with Enhanced Features*
"""
        
        return markdown
    
    def _copy_plots_to_reports(self, results: Dict):
        """Copy generated plots to reports directory for easy access"""
        plot_files = results.get('visualization', {}).get('plot_files', [])
        
        for plot_type in plot_files:
            src_path = PLOTS_DIR / f"{self.base_name}_{plot_type}.png"
            dst_path = REPORTS_DIR / f"{self.base_name}_{plot_type}.png"
            if src_path.exists():
                import shutil
                shutil.copy2(src_path, dst_path)
    
    def save_transcript(self, full_text: str, speaker_transcript: List[Dict]) -> Dict[str, Path]:
        """
        Save transcript files
        
        Args:
            full_text: Full transcript text
            speaker_transcript: Speaker-segmented transcript
            
        Returns:
            Dictionary of saved file paths
        """
        saved_files = {}
        
        # Save full transcript
        transcript_path = TRANSCRIPTS_DIR / f"{self.base_name}_full.txt"
        if save_text_file(full_text, transcript_path):
            saved_files['full_transcript'] = transcript_path
        
        # Save speaker transcript
        speaker_text = self._format_speaker_transcript(speaker_transcript)
        speaker_path = TRANSCRIPTS_DIR / f"{self.base_name}_speakers.txt"
        if save_text_file(speaker_text, speaker_path):
            saved_files['speaker_transcript'] = speaker_path
        
        return saved_files
    
    def _format_speaker_transcript(self, speaker_transcript: List[Dict]) -> str:
        """Format speaker transcript with timestamps"""
        formatted = f"Speaker Transcript - {self.base_name}\n"
        formatted += "=" * 50 + "\n\n"
        
        for segment in speaker_transcript:
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            speaker = segment.get('speaker', 'UNKNOWN')
            text = segment.get('text', '')
            
            # Format time as MM:SS
            start_min = int(start_time // 60)
            start_sec = int(start_time % 60)
            end_min = int(end_time // 60)
            end_sec = int(end_time % 60)
            
            time_str = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d}"
            formatted += f"[{time_str}] {speaker}:\n{text}\n\n"
        
        return formatted
    
    def generate_json_metadata(self, results: Dict) -> Path:
        """
        Generate JSON metadata file
        
        Args:
            results: Analysis results
            
        Returns:
            Path to JSON file
        """
        # Create simplified metadata
        metadata = {
            "metadata": {
                "report_name": self.base_name,
                "generation_date": self.report_date,
                "audio_file": results.get('input_info', {}).get('audio_file'),
                "duration": results.get('input_info', {}).get('duration'),
                "word_count": results.get('transcription', {}).get('word_count'),
                "audio_enhanced": results.get('input_info', {}).get('enhanced', False)
            },
            "statistics": {
                "speakers": results.get('speaker_analysis', {}).get('speaker_count'),
                "topics": results.get('topic_analysis', {}).get('topic_count'),
                "keywords": results.get('keyword_analysis', {}).get('keyword_count'),
                "chapters": results.get('chapter_analysis', {}).get('chapter_count')
            },
            "summary": results.get('summarization', {}).get('abstractive', ''),
            "visualizations": results.get('visualization', {}).get('plot_files', [])
        }
        
        json_path = REPORTS_DIR / f"{self.base_name}_metadata.json"
        save_json_file(metadata, json_path)
        
        return json_path

# Global function for main.py compatibility
def generate_comprehensive_report(results: Dict, base_name: str = "report") -> Path:
    """
    Generate comprehensive report (global function for main.py)
    
    Args:
        results: Analysis results
        base_name: Base name for output files
        
    Returns:
        Path to generated report file
    """
    generator = ReportGenerator(base_name)
    return generator.generate_comprehensive_report(results)