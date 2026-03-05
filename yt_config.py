"""
YouTube Downloader Configuration with Deno
"""

import subprocess
from pathlib import Path

class YouTubeConfig:
    def __init__(self):
        self.deno_path = self.find_deno()
        self.cookies_file = Path("cookies.txt")
        
    def find_deno(self):
        """Find Deno executable"""
        try:
            result = subprocess.run(["deno", "--version"], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                return "deno"
        except:
            return None
    
    def get_ytdlp_options(self, url: str) -> list:
        """Get yt-dlp command options with Deno"""
        base_options = [
            "yt-dlp",
            "--js-runtime", "deno",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--no-playlist",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "--add-header", "Accept-Language:en-US,en;q=0.9",
        ]
        
        # Add cookies if available
        if self.cookies_file.exists():
            base_options.extend(["--cookies", str(self.cookies_file)])
        
        # Add output template
        base_options.extend(["-o", "audio_uploads/%(title)s.%(ext)s"])
        
        # Add URL
        base_options.append(url)
        
        return base_options
    
    def test_connection(self, url: str) -> bool:
        """Test if we can access the video"""
        try:
            cmd = ["yt-dlp", "--js-runtime", "deno", "--simulate", url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

# Usage in your main code
config = YouTubeConfig()
if config.deno_path:
    print("✅ Deno is ready!")
else:
    print("❌ Deno not found")