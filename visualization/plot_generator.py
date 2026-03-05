# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\visualization\plot_generator.py
"""
Visualization generator for audio analysis results
FIXED VERSION - Handles all data structures properly
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class PlotGenerator:
    """Generate various plots for audio analysis"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def plot_metrics(self, metrics: Dict[str, float], filename: str = "metrics.png") -> Path:
        """Plot accuracy metrics as bar chart"""
        try:
            # Filter out non-numeric values and ensure we have data
            filtered_metrics = {}
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    filtered_metrics[key] = float(value)
                elif isinstance(value, dict):
                    # Handle nested metrics
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            filtered_metrics[f"{key}_{sub_key}"] = float(sub_value)
            
            if not filtered_metrics:
                print("   ⚠️ No valid metrics data to plot")
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data
            labels = list(filtered_metrics.keys())
            values = list(filtered_metrics.values())
            
            # Clean up label names
            clean_labels = []
            for label in labels:
                # Remove prefixes and clean up
                clean_label = label.replace('rouge_', 'ROUGE-').replace('_', ' ').title()
                clean_label = clean_label.replace('Rouge L', 'ROUGE-L').replace('Bleu', 'BLEU').replace('Bert F1', 'BERT-F1')
                clean_labels.append(clean_label)
            
            colors = sns.color_palette("Blues_d", len(labels))
            
            # Create bars
            bars = ax.bar(clean_labels, values, color=colors, edgecolor='black', linewidth=1)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{value:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Customize plot
            ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
            ax.set_title('Accuracy Metrics', fontsize=14, fontweight='bold', pad=20)
            ax.set_ylim(0, max(values) * 1.2 if values else 100)
            ax.grid(True, alpha=0.3)
            
            # Rotate x-axis labels if long
            if max(len(str(label)) for label in clean_labels) > 10:
                plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            # Save plot
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"   📊 Metrics plot saved: {filename}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Metrics plot failed: {e}")
            import traceback
            traceback.print_exc()
            plt.close('all')
            return None
    
    def plot_emotions(self, emotion_data: Dict, filename: str = "emotions.png") -> Path:
        """Plot emotion scores - handles multiple data structures"""
        try:
            # Extract emotion scores from different possible structures
            emotion_scores = {}
            
            if isinstance(emotion_data, dict):
                if 'emotion_scores' in emotion_data:
                    # Structure: {'emotion_scores': {...}}
                    emotion_scores = emotion_data['emotion_scores']
                elif 'dominant_emotion' in emotion_data:
                    # Structure: {'dominant_emotion': 'joy', 'dominant_score': 0.8}
                    dominant = emotion_data.get('dominant_emotion', 'neutral')
                    score = emotion_data.get('dominant_score', 1.0)
                    emotion_scores = {dominant: score}
                elif all(isinstance(k, str) for k in emotion_data.keys()):
                    # Structure: {'joy': 0.4, 'neutral': 0.3, ...}
                    emotion_scores = emotion_data
            else:
                print(f"   ⚠️ Unexpected emotion data type: {type(emotion_data)}")
                return None
            
            if not emotion_scores:
                # Create default emotion scores
                emotion_scores = {
                    'neutral': 0.5,
                    'joy': 0.3,
                    'sadness': 0.1,
                    'anger': 0.1
                }
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Pie chart
            labels = list(emotion_scores.keys())
            sizes = list(emotion_scores.values())
            colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99', '#FF99FF', '#FFD700', '#87CEEB', '#98FB98']
            
            ax1.pie(sizes, labels=labels, colors=colors[:len(labels)], 
                   autopct='%1.1f%%', startangle=90, shadow=True)
            ax1.set_title('Emotion Distribution', fontsize=12, fontweight='bold')
            ax1.axis('equal')
            
            # Bar chart
            y_pos = np.arange(len(labels))
            bars = ax2.barh(y_pos, sizes, color=colors[:len(labels)], edgecolor='black')
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(labels)
            ax2.set_xlabel('Score', fontsize=11)
            ax2.set_title('Emotion Scores', fontsize=12, fontweight='bold')
            
            # Add value labels
            for bar, value in zip(bars, sizes):
                width = bar.get_width()
                ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2,
                        f'{value:.3f}', va='center', fontsize=9)
            
            plt.tight_layout()
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"   😊 Emotions plot saved: {filename}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Emotions plot failed: {e}")
            import traceback
            traceback.print_exc()
            plt.close('all')
            return None
    
    def plot_keywords(self, keywords_data: Any, filename: str = "keywords.png") -> Path:
        """Plot keywords - handles multiple data structures"""
        try:
            keywords = []
            
            if isinstance(keywords_data, list):
                # Direct list of (keyword, score) tuples
                keywords = keywords_data
            elif isinstance(keywords_data, dict) and 'keywords' in keywords_data:
                # Structure: {'keywords': [...]}
                keywords = keywords_data['keywords']
            elif isinstance(keywords_data, dict):
                # Try to extract from dict values
                for value in keywords_data.values():
                    if isinstance(value, list):
                        keywords = value
                        break
            
            if not keywords:
                print("   ⚠️ No keywords data to plot")
                # Create a simple text plot
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, 'No keywords extracted', 
                       ha='center', va='center', fontsize=12)
                ax.set_title('Keywords', fontsize=14, fontweight='bold')
                ax.axis('off')
                
                output_path = self.output_dir / filename
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
                return output_path
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Extract words and scores, handle different tuple/list structures
            valid_keywords = []
            for item in keywords:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    keyword = str(item[0])
                    try:
                        score = float(item[1])
                        valid_keywords.append((keyword, score))
                    except (ValueError, TypeError):
                        continue
                elif isinstance(item, str):
                    valid_keywords.append((item, 1.0))
            
            if not valid_keywords:
                ax.text(0.5, 0.5, 'No valid keywords data', 
                       ha='center', va='center', fontsize=12)
                ax.set_title('Keywords', fontsize=14, fontweight='bold')
                ax.axis('off')
            else:
                # Take top 15 keywords
                top_keywords = sorted(valid_keywords, key=lambda x: x[1], reverse=True)[:15]
                words = [kw[0] for kw in top_keywords]
                scores = [kw[1] for kw in top_keywords]
                
                # Normalize scores for bubble sizes
                max_score = max(scores) if scores else 1
                sizes = [score * 500 / max_score for score in scores]
                
                # Create scatter plot
                y_pos = np.arange(len(words))
                scatter = ax.scatter(scores, y_pos, s=sizes, alpha=0.6, 
                                    c=scores, cmap='viridis', edgecolors='black', linewidth=0.5)
                
                # Add word labels
                for i, (word, score) in enumerate(zip(words, scores)):
                    ax.text(score, i, f' {word}', va='center', fontsize=10)
                
                # Customize
                ax.set_yticks(y_pos)
                ax.set_yticklabels([])  # Hide y-tick labels since we have word labels
                ax.set_xlabel('Importance Score', fontsize=11)
                ax.set_title('Top Keywords', fontsize=14, fontweight='bold')
                ax.grid(True, alpha=0.3)
                
                # Add colorbar
                plt.colorbar(scatter, ax=ax, label='Importance')
            
            plt.tight_layout()
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"   🔑 Keywords plot saved: {filename}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Keywords plot failed: {e}")
            import traceback
            traceback.print_exc()
            plt.close('all')
            return None
    
    def plot_speakers(self, speaker_data: Any, filename: str = "speakers.png") -> Path:
        """Plot speaker statistics - handles multiple data structures"""
        try:
            speaker_stats = {}
            
            if isinstance(speaker_data, dict):
                if 'segments' in speaker_data:
                    # Structure from speaker_analysis: {'segments': [...]}
                    for seg in speaker_data['segments']:
                        speaker = seg.get('speaker', 'UNKNOWN')
                        if speaker not in speaker_stats:
                            speaker_stats[speaker] = {'duration': 0, 'words': 0}
                        speaker_stats[speaker]['duration'] += seg.get('end', 0) - seg.get('start', 0)
                        speaker_stats[speaker]['words'] += len(seg.get('text', '').split())
                elif 'statistics' in speaker_data:
                    # Structure with pre-calculated statistics
                    speaker_stats = speaker_data['statistics']
                elif all(isinstance(v, dict) for v in speaker_data.values()):
                    # Direct speaker stats dict
                    speaker_stats = speaker_data
            
            if not speaker_stats:
                print("   ⚠️ No speaker data to plot")
                return None
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
            
            # Speaker duration distribution
            speakers = list(speaker_stats.keys())
            durations = [stats.get('duration', 0) for stats in speaker_stats.values()]
            word_counts = [stats.get('words', 0) for stats in speaker_stats.values()]
            
            # Ensure we have data
            if sum(durations) == 0 and sum(word_counts) == 0:
                print("   ⚠️ Insufficient speaker data")
                return None
            
            # Bar chart for durations
            bars1 = ax1.bar(speakers, durations, color=sns.color_palette("Set2"), edgecolor='black')
            ax1.set_xlabel('Speaker', fontsize=11)
            ax1.set_ylabel('Duration (seconds)', fontsize=11)
            ax1.set_title('Speaking Time by Speaker', fontsize=12, fontweight='bold')
            ax1.tick_params(axis='x', rotation=45)
            
            # Add duration labels
            for bar, duration in zip(bars1, durations):
                height = bar.get_height()
                if height > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{duration:.1f}s', ha='center', va='bottom', fontsize=9)
            
            # Pie chart for word counts
            ax2.pie(word_counts, labels=speakers, autopct='%1.1f%%', 
                   colors=sns.color_palette("Set3"), startangle=90)
            ax2.set_title('Word Distribution by Speaker', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"   👥 Speakers plot saved: {filename}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Speakers plot failed: {e}")
            import traceback
            traceback.print_exc()
            plt.close('all')
            return None
    
    def plot_timeline(self, chapters_data: Any, filename: str = "timeline.png") -> Path:
        """Plot chapter/segment timeline - handles multiple data structures"""
        try:
            chapters = []
            
            if isinstance(chapters_data, list):
                chapters = chapters_data
            elif isinstance(chapters_data, dict) and 'chapters' in chapters_data:
                chapters = chapters_data['chapters']
            
            if not chapters:
                print("   ⚠️ No chapter data to plot")
                return None
            
            fig, ax = plt.subplots(figsize=(12, 4))
            
            colors = sns.color_palette("husl", len(chapters))
            
            for i, chapter in enumerate(chapters):
                # Handle different chapter structures
                start = chapter.get('time_start', chapter.get('start', i * 30))
                end = chapter.get('time_end', chapter.get('end', start + 30))
                duration = end - start
                title = chapter.get('title', chapter.get('summary', f'Chapter {i+1}'))
                
                # Truncate long titles
                if len(title) > 30:
                    title = title[:27] + '...'
                
                # Create horizontal bar for chapter
                ax.barh(i, duration, left=start, height=0.6, 
                       color=colors[i], edgecolor='black', alpha=0.7)
                
                # Add chapter title
                mid_point = start + duration / 2
                ax.text(mid_point, i, title, ha='center', va='center', 
                       fontsize=9, fontweight='bold', color='white')
                
                # Add time labels
                ax.text(start, i + 0.3, f"{start/60:.1f}m", ha='left', va='bottom', fontsize=8)
                ax.text(end, i + 0.3, f"{end/60:.1f}m", ha='right', va='bottom', fontsize=8)
            
            ax.set_xlabel('Time (seconds)', fontsize=11)
            ax.set_ylabel('Chapters', fontsize=11)
            ax.set_title('Chapter Timeline', fontsize=14, fontweight='bold')
            ax.set_yticks(range(len(chapters)))
            ax.set_yticklabels([f'Ch {i+1}' for i in range(len(chapters))])
            ax.grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            
            output_path = self.output_dir / filename
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            print(f"   📅 Timeline plot saved: {filename}")
            return output_path
            
        except Exception as e:
            print(f"   ⚠️ Timeline plot failed: {e}")
            import traceback
            traceback.print_exc()
            plt.close('all')
            return None
    
    def generate_all_plots(self, analysis_results: Dict) -> Dict[str, Path]:
        """Generate all plots from analysis results - FIXED VERSION"""
        plots = {}
        
        try:
            # Get base name from audio file
            audio_file = analysis_results.get('input_info', {}).get('audio_file', 'unknown')
            base_name = Path(audio_file).stem
            
            print(f"   🎨 Generating plots for: {base_name}")
            
            # 1. Metrics plot
            if 'quality_metrics' in analysis_results:
                metrics_file = f"{base_name}_metrics.png"
                plots['metrics'] = self.plot_metrics(
                    analysis_results['quality_metrics'], 
                    metrics_file
                )
            
            # 2. Emotions plot
            if 'emotion_analysis' in analysis_results:
                emotions_file = f"{base_name}_emotions.png"
                plots['emotions'] = self.plot_emotions(
                    analysis_results['emotion_analysis'], 
                    emotions_file
                )
            
            # 3. Keywords plot
            if 'keyword_analysis' in analysis_results:
                keywords_file = f"{base_name}_keywords.png"
                plots['keywords'] = self.plot_keywords(
                    analysis_results['keyword_analysis'], 
                    keywords_file
                )
            
            # 4. Speakers plot
            if 'speaker_analysis' in analysis_results:
                speakers_file = f"{base_name}_speakers.png"
                plots['speakers'] = self.plot_speakers(
                    analysis_results['speaker_analysis'], 
                    speakers_file
                )
            
            # 5. Timeline plot
            if 'chapter_analysis' in analysis_results:
                timeline_file = f"{base_name}_timeline.png"
                plots['timeline'] = self.plot_timeline(
                    analysis_results['chapter_analysis'], 
                    timeline_file
                )
            
            # Count successful plots
            successful_plots = {k: v for k, v in plots.items() if v is not None}
            print(f"   ✅ Successfully generated {len(successful_plots)} plots")
            
            return successful_plots
            
        except Exception as e:
            print(f"   ⚠️ Plot generation failed: {e}")
            import traceback
            traceback.print_exc()
            return {}

# Global instance
plot_generator = None

def init_plot_generator(output_dir: Path):
    """Initialize plot generator"""
    global plot_generator
    plot_generator = PlotGenerator(output_dir)
    return plot_generator

# Test function
def test_plot_generation():
    """Test the plot generator with sample data"""
    from pathlib import Path
    
    # Create test data matching your actual structure
    test_data = {
        "input_info": {
            "audio_file": "test_audio.wav"
        },
        "quality_metrics": {
            "rouge_l": 0.488,
            "bleu": 0.312,
            "bert_f1": 0.645
        },
        "emotion_analysis": {
            "emotion_scores": {
                "joy": 0.4,
                "neutral": 0.3,
                "sadness": 0.2,
                "anger": 0.1
            },
            "dominant_emotion": "joy",
            "dominant_score": 0.4
        },
        "keyword_analysis": {
            "keywords": [
                ("visit restaurants", 0.533),
                ("food restaurants", 0.514),
                ("restaurants like", 0.498),
                ("restaurants", 0.490),
                ("restaurant usually", 0.457)
            ]
        },
        "speaker_analysis": {
            "segments": [
                {"speaker": "SPEAKER_00", "start": 0, "end": 30, "text": "Hello how are you"},
                {"speaker": "SPEAKER_01", "start": 30, "end": 60, "text": "I'm good thanks"},
                {"speaker": "SPEAKER_00", "start": 60, "end": 90, "text": "What do you think"}
            ]
        },
        "chapter_analysis": {
            "chapters": [
                {"title": "Introduction", "time_start": 0, "time_end": 30},
                {"title": "Main Discussion", "time_start": 30, "time_end": 60},
                {"title": "Conclusion", "time_start": 60, "time_end": 90}
            ]
        }
    }
    
    print("🧪 Testing plot generator...")
    plot_gen = PlotGenerator(Path("./test_plots"))
    plots = plot_gen.generate_all_plots(test_data)
    
    if plots:
        print(f"✅ Generated {len(plots)} plots:")
        for plot_name, plot_path in plots.items():
            if plot_path:
                print(f"   ✓ {plot_name}: {plot_path.name}")
    else:
        print("❌ No plots generated")

if __name__ == "__main__":
    test_plot_generation()