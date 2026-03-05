"""
Flask Web Application for AI Audio Summarizer
"""

import os
import sys
import uuid
import json
import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, url_for

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main import AudioSummarizer
from config import REPORTS_DIR, TRANSCRIPTS_DIR, SUMMARIES_DIR, PLOTS_DIR, AUDIO_UPLOADS
from utils.subprocess_utils import check_ffmpeg

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['SECRET_KEY'] = os.urandom(24).hex()

# Global summarizer instance (loaded once)
summarizer = None
current_results = {}

def get_summarizer():
    """Lazy load summarizer"""
    global summarizer
    if summarizer is None:
        print("🔄 Loading AudioSummarizer...")
        summarizer = AudioSummarizer()
    return summarizer

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        # Get form data
        url = request.form.get('url', '').strip()
        input_language = request.form.get('input_language', '').strip()
        target_language = request.form.get('target_language', 'en').strip()
        summarization_type = request.form.get('summarization_type', 'abstractive')
        enable_diarization = request.form.get('enable_diarization') == 'true'
        
        file = request.files.get('file')
        
        # Validate input
        if not url and not file:
            return jsonify({'error': 'Please provide a file or URL'}), 400
        
        # Handle file upload
        input_path = url
        if file:
            # Generate unique filename to avoid conflicts
            ext = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = app.config['UPLOAD_FOLDER'] / unique_filename
            file.save(file_path)
            input_path = str(file_path)
            print(f"📁 File uploaded: {file.filename} -> {unique_filename}")
        
        # Get summarizer
        summarizer = get_summarizer()
        
        # Configure processing based on options
        # Note: You may need to modify your summarizer to accept these options
        print(f"🎯 Processing: {input_path[:50]}...")
        print(f"   Language: {input_language or 'auto'}")
        print(f"   Summary type: {summarization_type}")
        print(f"   Speaker diarization: {enable_diarization}")
        
        # Process the audio/video
        results = summarizer.process(input_path)
        
        if not results:
            return jsonify({'error': 'Processing failed'}), 500
        
        # Store results for export
        result_id = uuid.uuid4().hex
        current_results[result_id] = results
        
        # Format response for frontend
        response = format_results_for_frontend(results, result_id)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def format_results_for_frontend(results, result_id):
    """Format results for frontend display"""
    
    # Get transcript
    transcript = results.get('transcription', {}).get('full_text', 'No transcript generated')
    
    # Get summary (prefer abstractive)
    summary = results.get('summarization', {}).get('abstractive', 'No summary generated')
    if not summary:
        summary = results.get('summarization', {}).get('extractive', 'No summary generated')
    
    # Get emotion
    emotion_data = results.get('emotion_analysis', {})
    emotion_text = "Emotion not detected"
    if emotion_data:
        if 'emotion_scores' in emotion_data:
            emotion_text = "\n".join([
                f"{k}: {v*100:.1f}%" 
                for k, v in emotion_data['emotion_scores'].items()
            ])
        if 'dominant_emotion' in emotion_data:
            emotion_text = f"Dominant: {emotion_data['dominant_emotion']}\n\n{emotion_text}"
    
    # Get keywords
    keywords = results.get('keyword_analysis', {}).get('keywords', [])
    keywords_text = "\n".join([f"• {kw[0]}" for kw in keywords[:10]]) if keywords else "No keywords extracted"
    
    # Get highlights (from topics)
    topics = results.get('topic_analysis', {}).get('topics', [])
    highlights_text = "\n".join([
        f"• {t.get('title', 'Topic')}: {t.get('text', '')[:100]}..." 
        for t in topics[:5]
    ]) if topics else "No highlights detected"
    
    # Get tasks
    tasks = results.get('task_analysis', {}).get('tasks', [])
    tasks_text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(tasks[:5])]) if tasks else "No tasks identified"
    
    # Get chapters
    chapters = results.get('chapter_analysis', {}).get('chapters', [])
    chapters_text = "\n".join([
        f"• {c.get('title', 'Chapter')} ({c.get('start_time', '00:00')} - {c.get('end_time', '00:00')})"
        for c in chapters[:5]
    ]) if chapters else "No chapters generated"
    
    # # Get speaker summary
    # speaker_data = results.get('speaker_analysis', {})
    # speaker_text = ""
    # if 'summaries' in speaker_data:
    #     for speaker, data in speaker_data['summaries'].items():
    #         speaker_text += f"{speaker}:\n{data.get('summary', '')}\n\n"
    # elif 'segments' in speaker_data:
    #     speakers = set(s.get('speaker', 'Unknown') for s in speaker_data['segments'])
    #     speaker_text = f"Detected {len(speakers)} speakers: {', '.join(speakers)}"
    # else:
    #     speaker_text = "No speaker analysis available"

    # In format_results_for_frontend function, replace the speaker section:

    # Get speaker summary
    speaker_data = results.get('speaker_analysis', {})
    speaker_text = ""

    if 'summaries' in speaker_data:
        # Use the new formatted speaker summaries
        for speaker, data in speaker_data['summaries'].items():
            if isinstance(data, dict):
                # New format with summary field
                speaker_text += f"{speaker}:\n{data.get('summary', '')}\n\n"
            else:
                # Old format (direct string)
                speaker_text += f"{speaker}:\n{data}\n\n"
    elif 'segments' in speaker_data:
        # If no summaries, group by speaker and show first few lines
        speaker_groups = {}
        for seg in speaker_data['segments']:
            spk = seg.get('speaker', 'Unknown')
            if spk not in speaker_groups:
                speaker_groups[spk] = []
            speaker_groups[spk].append(seg.get('text', ''))
    
        for spk, texts in speaker_groups.items():
            # Join texts and truncate
            full_text = ' '.join(texts)
            if len(full_text) > 300:
                full_text = full_text[:300] + '...'
            speaker_text += f"{spk}:\n{full_text}\n\n"
    else:
        speaker_text = "No speaker analysis available"
    
    # Get timeline
    timeline_text = ""
    if topics:
        for t in topics[:5]:
            start = t.get('time_start', 0)
            end = t.get('time_end', 0)
            try:
                # Convert to integers for formatting
                start_int = int(start)
                end_int = int(end)
                timeline_text += f"[{start_int//60:02d}:{start_int%60:02d} - {end_int//60:02d}:{end_int%60:02d}] {t.get('title', 'Topic')}\n"
            except (ValueError, TypeError):
                # Fallback if conversion fails
                timeline_text += f"[{start:.1f}s - {end:.1f}s] {t.get('title', 'Topic')}\n"
    else:
        timeline_text = "No timeline generated"
    
    # Get metrics
    metrics = results.get('quality_metrics', {})
    
    return {
        'success': True,
        'result_id': result_id,
        'results': {
            'transcript': transcript[:500] + '...' if len(transcript) > 500 else transcript,
            'summary': summary,
            'emotion': emotion_text,
            'keywords': keywords_text,
            'highlights': highlights_text,
            'tasks': tasks_text,
            'chapters': chapters_text,
            'speaker_summary': speaker_text,
            'timeline': timeline_text,
            'metrics': {
                'ROUGE-L': metrics.get('rouge_l', 0),
                'BLEU': metrics.get('bleu', 0),
                'BERT-F1': metrics.get('bert_f1', 0),
                'Compression': metrics.get('compression_ratio', 0)
            }
        },
        'stats': {
            'duration': results.get('input_info', {}).get('duration', 0),
            'words': results.get('transcription', {}).get('word_count', 0),
            'speakers': results.get('speaker_analysis', {}).get('speaker_count', 0),
            'topics': results.get('topic_analysis', {}).get('topic_count', 0),
            'processing_time': results.get('processing_info', {}).get('total_time', 0)
        }
    }

@app.route('/export/<result_id>/<format>')
def export_results(result_id, format):
    """Export results in various formats"""
    if result_id not in current_results:
        return jsonify({'error': 'Results not found'}), 404
    
    results = current_results[result_id]
    audio_file = results.get('input_info', {}).get('audio_file', 'unknown')
    base_name = Path(audio_file).stem
    
    if format == 'txt':
        # Generate text export
        content = generate_text_export(results)
        
        # Save to temp file
        temp_file = app.config['UPLOAD_FOLDER'] / f"export_{result_id}.txt"
        temp_file.write_text(content, encoding='utf-8')
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f"{base_name}_analysis.txt",
            mimetype='text/plain'
        )
    
    elif format == 'pdf':
        # PDF export (you'll need to implement this)
        return jsonify({'error': 'PDF export coming soon'}), 501
    
    elif format == 'csv' and 'speaker_analysis' in results:
        # Generate CSV for speaker diarization
        import csv
        temp_file = app.config['UPLOAD_FOLDER'] / f"speakers_{result_id}.csv"
        
        with open(temp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Speaker', 'Start', 'End', 'Text'])
            
            for seg in results['speaker_analysis'].get('segments', []):
                writer.writerow([
                    seg.get('speaker', 'Unknown'),
                    seg.get('start', 0),
                    seg.get('end', 0),
                    seg.get('text', '')
                ])
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f"{base_name}_speakers.csv",
            mimetype='text/csv'
        )
    
    return jsonify({'error': 'Invalid format'}), 400

def generate_text_export(results):
    """Generate comprehensive text export"""
    lines = []
    lines.append("="*60)
    lines.append("AI AUDIO SUMMARIZER - ANALYSIS RESULTS")
    lines.append("="*60)
    lines.append("")
    
    # Input info
    info = results.get('input_info', {})
    lines.append(f"Audio File: {info.get('audio_file', 'Unknown')}")
    lines.append(f"Duration: {info.get('duration', 0):.1f} seconds")
    lines.append(f"Processed: {results.get('processing_info', {}).get('timestamp', 'Unknown')}")
    lines.append("")
    
    # Statistics
    stats = results.get('transcription', {})
    lines.append("STATISTICS:")
    lines.append(f"  Words: {stats.get('word_count', 0)}")
    lines.append(f"  Speakers: {results.get('speaker_analysis', {}).get('speaker_count', 0)}")
    lines.append(f"  Topics: {results.get('topic_analysis', {}).get('topic_count', 0)}")
    lines.append("")
    
    # Summary
    lines.append("SUMMARY:")
    lines.append(results.get('summarization', {}).get('abstractive', 'No summary'))
    lines.append("")
    
    # Metrics
    metrics = results.get('quality_metrics', {})
    lines.append("METRICS:")
    lines.append(f"  ROUGE-L: {metrics.get('rouge_l', 0):.3f}")
    lines.append(f"  BLEU: {metrics.get('bleu', 0):.3f}")
    lines.append(f"  BERT-F1: {metrics.get('bert_f1', 0):.3f}")
    lines.append("")
    
    # Keywords
    keywords = results.get('keyword_analysis', {}).get('keywords', [])
    if keywords:
        lines.append("TOP KEYWORDS:")
        for kw, score in keywords[:10]:
            lines.append(f"  • {kw} ({score:.3f})")
        lines.append("")
    
    return "\n".join(lines)

@app.route('/status')
def status():
    """Check system status"""
    ffmpeg_ok = check_ffmpeg()
    
    return jsonify({
        'status': 'running',
        'ffmpeg': 'available' if ffmpeg_ok else 'not found',
        'models_loaded': summarizer is not None,
        'directories': {
            'uploads': str(app.config['UPLOAD_FOLDER']),
            'audio_uploads': str(AUDIO_UPLOADS)
        }
    })

@app.route('/clear/<result_id>', methods=['POST'])
def clear_results(result_id):
    """Clear cached results"""
    if result_id in current_results:
        del current_results[result_id]
    return jsonify({'success': True})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌐 AI AUDIO SUMMARIZER WEB INTERFACE")
    print("="*60)
    print("\n📁 Directories:")
    print(f"   Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"   Templates: {Path(__file__).parent / 'templates'}")
    print(f"   Static: {Path(__file__).parent / 'static'}")
    print("\n🚀 Starting server...")
    print("   Open: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)