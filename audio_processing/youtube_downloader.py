"""
YouTube Audio Downloader - Deno Integration
"""

import os
import sys
import subprocess
from pathlib import Path
from config import AUDIO_UPLOADS

def check_deno():
    """Check if Deno is installed and return its path"""
    try:
        result = subprocess.run(["deno", "--version"], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Deno found: {result.stdout.split()[1]}")
            return "deno"
    except:
        pass
    return None

def download_youtube_audio(url: str, output_name: str = None) -> str:
    """
    Download audio using yt-dlp with Deno JavaScript runtime
    """
    print(f"\n🎯 Downloading: {url}")
    
    # Check Deno first
    deno_path = check_deno()
    if not deno_path:
        print("❌ Deno not found. Please install Deno first.")
        return None
    
    # Update yt-dlp to latest version
    print("🔄 Updating yt-dlp...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], 
                  capture_output=True)
    
    # Prepare output path
    output_template = str(AUDIO_UPLOADS / "%(title)s.%(ext)s")
    
    # Build yt-dlp command with Deno
    cmd = [
        "yt-dlp",
        "--js-runtime", "deno",  # Use Deno as JavaScript runtime
        "--extract-audio",        # Extract audio
        "--audio-format", "mp3",  # Convert to MP3
        "--audio-quality", "0",    # Best quality
        "--no-playlist",           # Don't download playlists
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "--add-header", "Accept-Language:en-US,en;q=0.9",
        "-o", output_template,
        url
    ]
    
    print("⬇️ Downloading with Deno runtime...")
    
    try:
        # Run the command
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        
        if process.returncode == 0:
            print("✅ Download completed!")
            
            # Find the downloaded file
            downloaded_files = list(AUDIO_UPLOADS.glob("*.mp3"))
            if downloaded_files:
                # Get the most recent file
                latest_file = max(downloaded_files, key=lambda p: p.stat().st_mtime)
                file_size = latest_file.stat().st_size / (1024 * 1024)
                print(f"   📁 File: {latest_file.name}")
                print(f"   📊 Size: {file_size:.2f} MB")
                return str(latest_file)
            else:
                print("❌ Could not find downloaded file")
                return None
        else:
            print(f"❌ Download failed with error:")
            print(process.stderr)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def download_with_fallback(url: str) -> str:
    """
    Try multiple methods with Deno
    """
    methods = [
        # Method 1: Try with Deno and best audio
        {
            "cmd": ["yt-dlp", "--js-runtime", "deno", "--extract-audio", 
                   "--audio-format", "mp3", "-f", "bestaudio", url],
            "desc": "Best audio with Deno"
        },
        # Method 2: Try with different format
        {
            "cmd": ["yt-dlp", "--js-runtime", "deno", "--extract-audio", 
                   "--audio-format", "mp3", "-f", "worstaudio", url],
            "desc": "Worst audio with Deno (sometimes works better)"
        },
        # Method 3: Try without format specification
        {
            "cmd": ["yt-dlp", "--js-runtime", "deno", "--extract-audio", 
                   "--audio-format", "mp3", url],
            "desc": "Default format with Deno"
        }
    ]
    
    for method in methods:
        print(f"\n📥 Trying: {method['desc']}")
        try:
            result = subprocess.run(method["cmd"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Success!")
                # Find the downloaded file
                mp3_files = list(AUDIO_UPLOADS.glob("*.mp3"))
                if mp3_files:
                    return str(mp3_files[-1])
        except Exception as e:
            print(f"   Failed: {e}")
            continue
    
    return None

# Update your main.py to use this
def get_youtube_audio(url: str) -> str:
    """
    Main function to get YouTube audio
    """
    print("\n" + "="*60)
    print("🎬 YOUTUBE AUDIO DOWNLOADER WITH DENO")
    print("="*60)
    
    # Try primary method
    result = download_youtube_audio(url)
    
    # If primary fails, try fallback methods
    if not result:
        print("\n⚠️ Primary method failed, trying fallbacks...")
        result = download_with_fallback(url)
    
    return result

# For testing
if __name__ == "__main__":
    test_url = "https://youtu.be/HmR4M1ODZYo?si=sRrH1eFUMwcCOYqs"
    result = get_youtube_audio(test_url)
    if result:
        print(f"\n✅ SUCCESS! File saved to: {result}")
    else:
        print("\n❌ All download methods failed")