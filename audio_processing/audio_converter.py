# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\audio_processing\audio_converter.py
"""
Audio conversion utilities with audio enhancement
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from utils.subprocess_utils import safe_run_subprocess, convert_audio, get_audio_duration
from utils.audio_enhancer import audio_enhancer

def convert_to_wav(input_path: str, output_path: str, enhance: bool = True) -> bool:
    """
    Convert any audio file to WAV format with optional enhancement
    
    Args:
        input_path: Path to input audio file
        output_path: Path to output WAV file
        enhance: Whether to enhance audio quality
        
    Returns:
        True if successful, False otherwise
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"   ❌ Input file not found: {input_path}")
        return False
    
    # If file is already WAV, enhance if requested
    if input_file.suffix.lower() == '.wav' and enhance:
        print(f"   🔊 Enhancing existing WAV file...")
        enhanced_path = audio_enhancer.enhance_audio(str(input_file), str(output_file))
        return enhanced_path == str(output_file)
    
    print(f"   Converting {input_file.name} to WAV...")
    
    # First convert to WAV
    success = convert_audio(
        input_path=input_file,
        output_path=output_file,
        output_format="wav",
        sample_rate=16000
    )
    
    if success and output_file.exists():
        # Enhance audio if requested
        if enhance:
            enhanced_path = audio_enhancer.enhance_audio(str(output_file))
            if enhanced_path != str(output_file):
                # Replace with enhanced version
                output_file.unlink(missing_ok=True)
                Path(enhanced_path).rename(output_file)
        
        file_size = output_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   ✅ Converted: {output_file.name} ({file_size:.1f} MB)")
        return True
    else:
        print(f"   ❌ Conversion failed")
        return False

def get_audio_info(file_path: str) -> Dict:
    """
    Get audio file information
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with audio information
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {"error": "File not found"}
    
    info = {
        "filename": file_path.name,
        "path": str(file_path),
        "size_bytes": file_path.stat().st_size,
        "size_mb": file_path.stat().st_size / (1024 * 1024),
        "extension": file_path.suffix.lower(),
        "exists": True
    }
    
    # Get duration using audio enhancer
    try:
        audio_info = audio_enhancer.get_audio_info(str(file_path))
        if "duration" in audio_info:
            info["duration"] = audio_info["duration"]
            info["duration_formatted"] = format_duration(audio_info["duration"])
            info.update({k: v for k, v in audio_info.items() if k != "duration"})
    except:
        # Fallback to ffmpeg
        duration = get_audio_duration(file_path)
        if duration > 0:
            info["duration"] = duration
            info["duration_formatted"] = format_duration(duration)
    
    # Try to get more info with FFprobe if available
    ffprobe_info = get_audio_info_ffprobe(file_path)
    if ffprobe_info:
        info.update(ffprobe_info)
    
    return info

def get_audio_info_ffprobe(file_path: Path) -> Optional[Dict]:
    """
    Get detailed audio info using FFprobe
    
    Args:
        file_path: Path to audio file
        
    Returns:
        Dictionary with audio info or None
    """
    try:
        # Try to run ffprobe
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        
        success, output = safe_run_subprocess(cmd, capture_output=True)
        
        if success and output:
            data = json.loads(output)
            
            # Extract relevant audio info
            result = {"format": {}, "streams": []}
            
            if "format" in data:
                format_info = data["format"]
                result["format"] = {
                    "format_name": format_info.get("format_name", ""),
                    "duration": float(format_info.get("duration", 0)),
                    "size": int(format_info.get("size", 0)),
                    "bit_rate": int(format_info.get("bit_rate", 0))
                }
            
            if "streams" in data:
                for stream in data["streams"]:
                    if stream.get("codec_type") == "audio":
                        audio_stream = {
                            "codec": stream.get("codec_name", ""),
                            "sample_rate": stream.get("sample_rate", ""),
                            "channels": stream.get("channels", 1),
                            "channel_layout": stream.get("channel_layout", ""),
                            "bit_rate": stream.get("bit_rate", 0)
                        }
                        result["streams"].append(audio_stream)
            
            return result
    except:
        pass
    
    return None

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to HH:MM:SS
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:05.2f}"
    else:
        return f"{minutes:02d}:{secs:05.2f}"

def normalize_audio(input_path: str, output_path: str, target_level: float = -20.0) -> bool:
    """
    Normalize audio volume
    
    Args:
        input_path: Input audio file
        output_path: Output audio file
        target_level: Target loudness in LUFS
        
    Returns:
        True if successful, False otherwise
    """
    print(f"   Normalizing audio volume...")
    
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-af", f"loudnorm=I={target_level}:TP=-1.5:LRA=11",
        "-ar", "16000",
        "-ac", "1",
        "-y",
        str(output_path)
    ]
    
    success, _ = safe_run_subprocess(cmd, capture_output=False)
    return success

def split_audio_by_silence(input_path: str, output_dir: str, min_silence_len: int = 500) -> list:
    """
    Split audio file by silence detection
    
    Args:
        input_path: Input audio file
        output_dir: Output directory for segments
        min_silence_len: Minimum silence length in milliseconds
        
    Returns:
        List of output file paths
    """
    print(f"   Splitting audio by silence...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    output_pattern = str(output_dir / "segment_%03d.wav")
    
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-f", "segment",
        "-segment_times", "",  # Will be set by silence detection
        "-c", "copy",
        "-y",
        output_pattern
    ]
    
    # This is a simplified version. Full silence detection would need pydub
    print("   ⚠️ Basic splitting implemented")
    
    # For now, just return the original file
    return [input_path]

def get_supported_formats() -> list:
    """
    Get list of supported audio formats
    
    Returns:
        List of supported file extensions
    """
    return ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac', '.wma', '.mp4', '.mkv', '.avi', '.mov']