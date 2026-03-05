# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\setup_web.py
"""
Setup script for web interface
"""
import os
import sys
from pathlib import Path

def setup_web_interface():
    """Create necessary directories and files for web interface"""
    
    # Define paths
    current_dir = Path(__file__).parent
    directories = [
        'static/css',
        'static/js',
        'templates',
        'uploads',
        'web_results'
    ]
    
    # Create directories
    print("Creating directory structure...")
    for dir_path in directories:
        full_path = current_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created: {dir_path}")
    
    # Check for required files
    required_files = {
        'templates/index.html': 'HTML template file',
        'static/css/style.css': 'CSS stylesheet',
        'static/js/script.js': 'JavaScript file'
    }
    
    print("\nChecking required files...")
    for file_path, description in required_files.items():
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✓ Found: {file_path}")
        else:
            print(f"  ✗ Missing: {file_path} ({description})")
    
    # Check backend
    print("\nChecking backend...")
    try:
        from main import AudioSummarizer
        print("  ✓ Backend AudioSummarizer available")
    except ImportError as e:
        print(f"  ⚠ Backend not available: {e}")
        print("  Running in demo mode")
    
    print("\n" + "="*50)
    print("Setup complete!")
    print("\nTo start the web interface, run:")
    print("  python app.py")
    print("  or")
    print("  python run.py --web")
    print("\nThen open: http://localhost:5000")
    print("="*50)

if __name__ == "__main__":
    setup_web_interface()