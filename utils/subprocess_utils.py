# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\utils\subprocess_utils.py
"""
Subprocess utilities for audio processing
"""

import os
import sys
import subprocess
from pathlib import Path
from config import FFMPEG_PATH

def check_ffmpeg():
    """Check if FFmpeg is available"""
    if FFMPEG_PATH:
        try:
            result = subprocess.run([FFMPEG_PATH, "-version"], 
                                  capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False
    
    # Try to find ffmpeg in PATH
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=2)
        return result.returncode == 0
    except:
        return False

def setup_ffmpeg():
    """Setup FFmpeg for audio processing"""
    print("🔧 Checking FFmpeg...")
    
    if check_ffmpeg():
        print("   ✅ FFmpeg is available")
        return True
    else:
        print("   ⚠️ FFmpeg not found. Some audio features may not work.")
        print("\n💡 To install FFmpeg:")
        print("   1. Download from: https://ffmpeg.org/download.html")
        print("   2. Extract to C:\\ffmpeg")
        print("   3. Add C:\\ffmpeg\\bin to your PATH")
        print("\n   For now, YouTube downloads may still work.")
        return False

def safe_run_subprocess(cmd, description="", capture_output=True):
    """
    Run a command with error handling
    
    Args:
        cmd: Command to run (list or string)
        description: Description of what's being done
        capture_output: Whether to capture output
        
    Returns:
        Tuple of (success, output) or (success, None)
    """
    if description:
        print(f"   {description}...")
    
    try:
        if isinstance(cmd, str):
            # Use shell for string commands on Windows
            shell = sys.platform == "win32"
        else:
            shell = False
        
        result = subprocess.run(
            cmd, 
            capture_output=capture_output, 
            text=True, 
            shell=shell,
            timeout=30
        )
        
        if result.returncode != 0:
            if capture_output:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                print(f"   ❌ Command failed: {error_msg}")
            else:
                print(f"   ❌ Command failed with code {result.returncode}")
            return False, result.stderr if capture_output else None
        
        return True, result.stdout if capture_output else None
        
    except subprocess.TimeoutExpired:
        print("   ❌ Command timed out after 30 seconds")
        return False, None
    except Exception as e:
        print(f"   ❌ Command error: {e}")
        return False, None

def run_command(cmd, description=""):
    """Alias for safe_run_subprocess (backward compatibility)"""
    success, _ = safe_run_subprocess(cmd, description, capture_output=False)
    return success

def convert_audio(input_path, output_path, output_format="wav", sample_rate=16000):
    """
    Convert audio file using FFmpeg
    
    Args:
        input_path: Input audio file
        output_path: Output audio file
        output_format: Output format (wav, mp3, etc.)
        sample_rate: Target sample rate
        
    Returns:
        True if successful, False otherwise
    """
    if not check_ffmpeg():
        print("   ❌ FFmpeg not available for audio conversion")
        return False
    
    cmd = [
        FFMPEG_PATH or "ffmpeg",
        "-i", str(input_path),
        "-ar", str(sample_rate),
        "-ac", "1",  # Mono
        "-y",  # Overwrite output
        str(output_path)
    ]
    
    success, _ = safe_run_subprocess(cmd, f"Converting {input_path.name} to {output_format}")
    return success

def get_audio_duration(file_path):
    """
    Get audio duration using FFmpeg
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Duration in seconds or 0 if failed
    """
    if not check_ffmpeg():
        return 0
    
    cmd = [
        FFMPEG_PATH or "ffmpeg",
        "-i", str(file_path),
        "-f", "null", "-"
    ]
    
    success, output = safe_run_subprocess(cmd, capture_output=True)
    
    if success and output:
        # Parse duration from FFmpeg output
        import re
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d{2})", output)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2))
            seconds = float(duration_match.group(3))
            return hours * 3600 + minutes * 60 + seconds
    
    return 0

def extract_audio_from_video(video_path, audio_path):
    """
    Extract audio from video file
    
    Args:
        video_path: Path to video file
        audio_path: Path to save audio file
        
    Returns:
        True if successful, False otherwise
    """
    if not check_ffmpeg():
        print("   ❌ FFmpeg not available for audio extraction")
        return False
    
    cmd = [
        FFMPEG_PATH or "ffmpeg",
        "-i", str(video_path),
        "-q:a", "0",
        "-map", "a",
        "-y",
        str(audio_path)
    ]
    
    success, _ = safe_run_subprocess(cmd, f"Extracting audio from {video_path.name}")
    return success