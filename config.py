# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\config.py
"""
Configuration settings for AI Audio Summarizer
"""

import os
import sys
from pathlib import Path

# ============================================
# SUMMARIZATION SETTINGS
# ============================================

MAX_CHAPTERS = 10  # Maximum number of chapters to generate
MIN_CHAPTER_DURATION = 30  # Minimum chapter duration in seconds

# Add these other summarization constants if needed
ABSTRACTIVE_MAX_LENGTH = 150
ABSTRACTIVE_MIN_LENGTH = 30
EXTRACTIVE_SENTENCES = 4


# ============================================
# BASE DIRECTORY SETUP
# ============================================

# Base directory
BASE_DIR = Path(__file__).parent

# Create necessary directories
def create_directories():
    """Create all necessary directories"""
    directories = [
        "audio_uploads",
        "video_uploads",
        "processed_audio", 
        "transcripts",
        "summaries",
        "reports",
        "plots",
        "cache",
        "models",
        "visualization",
        "config"
    ]
    
    for dir_name in directories:
        dir_path = BASE_DIR / dir_name
        dir_path.mkdir(exist_ok=True)
    
    return BASE_DIR

# Create directories
create_directories()

# ============================================
# DIRECTORY PATHS (ALL REQUIRED)
# ============================================

AUDIO_UPLOADS = BASE_DIR / "audio_uploads"
VIDEO_UPLOADS = BASE_DIR / "video_uploads"
PROCESSED_AUDIO = BASE_DIR / "processed_audio"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
SUMMARIES_DIR = BASE_DIR / "summaries"
REPORTS_DIR = BASE_DIR / "reports"
PLOTS_DIR = BASE_DIR / "plots"
CACHE_DIR = BASE_DIR / "cache"
MODELS_DIR = BASE_DIR / "models"
VISUALIZATION_DIR = BASE_DIR / "visualization"
CONFIG_DIR = BASE_DIR / "config"


# ============================================
# DIRECTORY ALIASES (For backward compatibility)
# ============================================

# Aliases for modules that expect the old names
SUMMARIES = SUMMARIES_DIR
TRANSCRIPTS = TRANSCRIPTS_DIR
REPORTS = REPORTS_DIR
PLOTS = PLOTS_DIR
AUDIO_UPLOADS = AUDIO_UPLOADS  # Already exists
VIDEO_UPLOADS = VIDEO_UPLOADS  # Already exists

# ============================================
# FFMPEG SETTINGS
# ============================================

FFMPEG_PATH = None  # Will be auto-detected

# Try to find ffmpeg in common locations
common_paths = [
    "ffmpeg",  # If it's in PATH
    "ffmpeg.exe",
    "C:\\ffmpeg\\bin\\ffmpeg.exe",
    "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
    "C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe",
    str(BASE_DIR / "ffmpeg" / "bin" / "ffmpeg.exe"),
]

def find_ffmpeg():
    """Try to find FFmpeg executable"""
    import subprocess
    
    for path in common_paths:
        try:
            result = subprocess.run([path, "-version"], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return path
        except:
            continue
    
    # Try which/where command
    try:
        if sys.platform == "win32":
            result = subprocess.run(["where", "ffmpeg"], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(["which", "ffmpeg"], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

FFMPEG_PATH = find_ffmpeg()

# ============================================
# MODEL CONFIGURATIONS
# ============================================

MODEL_CONFIG = {
    "whisper": {
        "model_size": "base",  # tiny, base, small, medium, large
        "device": "cuda" if os.environ.get('CUDA_VISIBLE_DEVICES') else "cpu",
        "compute_type": "float16" if os.environ.get('CUDA_VISIBLE_DEVICES') else "float32"
    },
    "summarizer": {
        "model_name": "facebook/bart-large-cnn",
        "max_length": 150,
        "min_length": 30,
        "do_sample": False
    },
    "emotion": {
        "model_name": "j-hartmann/emotion-english-distilroberta-base",
        "batch_size": 32
    },
    "sentence_transformer": {
        "model_name": "all-MiniLM-L6-v2"
    },
    "diarization": {
        "model_name": "pyannote/speaker-diarization-3.1",
        "use_auth_token": False
    }
}

# ============================================
# PROCESSING CONFIGURATIONS
# ============================================

PROCESSING_CONFIG = {
    "chunk_size": 1000,  # Characters per chunk for processing
    "overlap": 100,      # Overlap between chunks
    "max_duration": 3600,  # Maximum audio duration in seconds
    "min_duration": 10,    # Minimum audio duration in seconds
    "sample_rate": 16000,  # Audio sample rate
    "channels": 1,         # Audio channels
    "language": "en"       # Default language
}

# ============================================
# VISUALIZATION CONFIGURATIONS
# ============================================

VISUALIZATION_CONFIG = {
    "enabled": True,
    "plot_format": "png",  # png, pdf, svg, jpg
    "dpi": 300,
    "generate_all": True,
    "plots_to_generate": [
        "metrics",
        "emotions", 
        "keywords",
        "speakers",
        "timeline"
    ],
    "colors": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "success": "#3CBBB1",
        "warning": "#F18F01",
        "danger": "#C73E1D"
    },
    "style": "seaborn-v0_8-whitegrid",
    "font_family": "sans-serif"
}

# ============================================
# OUTPUT CONFIGURATIONS
# ============================================

OUTPUT_CONFIG = {
    "transcript_format": "txt",  # txt, json, srt
    "summary_format": "md",      # md, txt, html
    "include_timestamps": True,
    "include_speakers": True,
    "include_chapters": True,
    "generate_plots": True,
    "plot_format": "png",        # png, jpg, svg, pdf
    "plot_dpi": 300,
    "save_all_formats": True,
    "enhance_audio": True,       # Enable audio enhancement
    "show_progress": True,       # Show progress indicators
    "auto_open_report": False    # Auto-open generated report
}

# ============================================
# AUDIO ENHANCEMENT CONFIG
# ============================================

AUDIO_ENHANCEMENT_CONFIG = {
    "enabled": True,
    "noise_reduction": True,
    "normalization": True,
    "pre_emphasis": True,
    "target_sample_rate": 16000,
    "silence_threshold": 0.01,  # RMS threshold for silence detection
    "min_silence_duration": 0.5  # Minimum silence duration in seconds
}

# ============================================
# CACHE SETTINGS
# ============================================

CACHE_CONFIG = {
    "enabled": True,
    "max_size_mb": 1024,  # Maximum cache size in MB
    "ttl_days": 7         # Time to live in days
}

# ============================================
# YOUTUBE DOWNLOAD SETTINGS
# ============================================

YOUTUBE_CONFIG = {
    "format": "bestaudio/best",
    "extract_audio": True,
    "audio_format": "mp3",
    "audio_quality": "192",
    "output_template": str(VIDEO_UPLOADS / "%(title)s.%(ext)s"),
    "max_duration": 3600,  # 1 hour max
    "retries": 3
}

# ============================================
# PROGRESS INDICATOR CONFIG
# ============================================

PROGRESS_CONFIG = {
    "enabled": True,
    "show_steps": True,
    "show_percentage": True,
    "show_spinner": True,
    "step_colors": {
        "start": "cyan",
        "complete": "green",
        "warning": "yellow",
        "error": "red"
    }
}

# ============================================
# UTILITY FUNCTIONS
# ============================================

def set_output_directory(path: str):
    """Dynamically set output directory"""
    global BASE_DIR, AUDIO_UPLOADS, VIDEO_UPLOADS, PROCESSED_AUDIO
    global TRANSCRIPTS_DIR, SUMMARIES_DIR, REPORTS_DIR, PLOTS_DIR, CACHE_DIR
    
    new_base = Path(path).absolute()
    new_base.mkdir(parents=True, exist_ok=True)
    
    BASE_DIR = new_base
    AUDIO_UPLOADS = BASE_DIR / "audio_uploads"
    VIDEO_UPLOADS = BASE_DIR / "video_uploads"
    PROCESSED_AUDIO = BASE_DIR / "processed_audio"
    TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
    SUMMARIES_DIR = BASE_DIR / "summaries"
    REPORTS_DIR = BASE_DIR / "reports"
    PLOTS_DIR = BASE_DIR / "plots"
    CACHE_DIR = BASE_DIR / "cache"
    
    # Recreate directories
    create_directories()
    
    return BASE_DIR

def get_config_summary() -> dict:
    """Get a summary of all configurations"""
    return {
        "base_directory": str(BASE_DIR),
        "directories": {
            "audio_uploads": str(AUDIO_UPLOADS),
            "video_uploads": str(VIDEO_UPLOADS),
            "processed_audio": str(PROCESSED_AUDIO),
            "transcripts": str(TRANSCRIPTS_DIR),
            "summaries": str(SUMMARIES_DIR),
            "reports": str(REPORTS_DIR),
            "plots": str(PLOTS_DIR),
            "cache": str(CACHE_DIR),
            "models": str(MODELS_DIR),
            "visualization": str(VISUALIZATION_DIR),
            "config": str(CONFIG_DIR)
        },
        "ffmpeg_path": FFMPEG_PATH,
        "model_config": MODEL_CONFIG,
        "processing_config": PROCESSING_CONFIG,
        "visualization_config": VISUALIZATION_CONFIG,
        "output_config": OUTPUT_CONFIG,
        "audio_enhancement_config": AUDIO_ENHANCEMENT_CONFIG,
        "progress_config": PROGRESS_CONFIG,
        "cache_config": CACHE_CONFIG,
        "youtube_config": YOUTUBE_CONFIG
    }

def print_config_summary():
    """Print configuration summary"""
    summary = get_config_summary()
    
    print("="*60)
    print("⚙️  CONFIGURATION SUMMARY")
    print("="*60)
    
    print(f"\n📁 Base Directory: {summary['base_directory']}")
    
    print("\n📂 Directories:")
    for name, path in summary['directories'].items():
        exists = "✅" if Path(path).exists() else "❌"
        print(f"  {exists} {name}: {Path(path).name}")
    
    print(f"\n🔧 FFmpeg: {summary['ffmpeg_path'] or 'Not found'}")
    
    print("\n🤖 Models:")
    for model, config in summary['model_config'].items():
        print(f"  • {model}: {config.get('model_name', 'N/A')}")
    
    print("\n🎨 Visualizations: Enabled" if summary['visualization_config']['enabled'] else "Visualizations: Disabled")
    print("🔊 Audio Enhancement: Enabled" if summary['audio_enhancement_config']['enabled'] else "Audio Enhancement: Disabled")
    print("📊 Progress Indicators: Enabled" if summary['progress_config']['enabled'] else "Progress Indicators: Disabled")
    
    print("\n" + "="*60)

# Print config on import (optional)
if __name__ != "__main__":
    print_config_summary()