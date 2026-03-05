"""
Test the web interface setup
"""

import sys
from pathlib import Path

def test_web_setup():
    """Test if all web files are in place"""
    
    project_dir = Path(__file__).parent
    
    # Check required files
    required = {
        'app.py': 'Flask application',
        'templates/index.html': 'HTML template',
        'static/css/style.css': 'CSS stylesheet',
        'static/js/script.js': 'JavaScript file',
    }
    
    print("🔍 Testing web interface setup...")
    print("="*50)
    
    all_ok = True
    for file_path, description in required.items():
        full_path = project_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {description:25} found ({size} bytes)")
        else:
            print(f"❌ {description:25} MISSING")
            all_ok = False
    
    print("="*50)
    
    if all_ok:
        print("\n✅ Web interface ready!")
        print("\n🚀 To start the web server:")
        print("   python app.py")
        print("   or")
        print("   python run.py --web")
        print("\n🌐 Then open: http://localhost:5000")
    else:
        print("\n❌ Missing files. Please create them first.")
    
    return all_ok

if __name__ == "__main__":
    test_web_setup()