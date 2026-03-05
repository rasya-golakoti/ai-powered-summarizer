# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\run.py
"""
AI Audio Summarizer - Command Line & Web Interface Runner
Usage:
  CLI Mode: python run.py [input] [options]
  Web Mode: python run.py --web [options]
"""

import os
import sys
import argparse
import signal
import webbrowser
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n⚠️  Interrupted by user. Cleaning up...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     🎙️  AI AUDIO SUMMARIZER - Complete Pipeline         ║
    ║                                                          ║
    ║     📁 CLI: Analyze audio/video files                    ║
    ║     🌐 Web: Interactive browser interface                ║
    ║     ⚡ Quick: Fast processing with essential features    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        from main import AudioSummarizer
        return True, "✅ Backend modules loaded successfully"
    except ImportError as e:
        return False, f"❌ Backend import error: {e}"
    except Exception as e:
        return False, f"❌ Error: {e}"

def run_cli_mode(args):
    """Run in CLI (command line) mode"""
    try:
        from main import AudioSummarizer
        from config import OUTPUT_CONFIG, VISUALIZATION_CONFIG, PROGRESS_CONFIG
        
        print("\n" + "="*60)
        print("🚀 Starting CLI Processing")
        print("="*60)
        
        # Apply command line overrides
        if args.no_enhance:
            OUTPUT_CONFIG["enhance_audio"] = False
            print("   ⚙️ Audio enhancement: DISABLED")
        
        if args.no_plots:
            VISUALIZATION_CONFIG["enabled"] = False
            print("   ⚙️ Visualizations: DISABLED")
        
        if args.no_progress:
            PROGRESS_CONFIG["enabled"] = False
            print("   ⚙️ Progress indicators: DISABLED")
        
        if args.quick:
            print("   ⚙️ Quick mode: ENABLED (skipping some analysis)")
        
        # Create output name if not provided
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if args.input.startswith(('http://', 'https://')):
                args.output = f"youtube_{timestamp}"
            else:
                file_stem = Path(args.input).stem
                args.output = f"{file_stem}_{timestamp}"
        
        print(f"\n📥 Input: {args.input}")
        print(f"📁 Output: {args.output}")
        print("-" * 40)
        
        # Start processing
        summarizer = AudioSummarizer()
        results = summarizer.process(args.input, args.output)
        
        if results:
            print("\n" + "="*60)
            print("✅ PROCESSING COMPLETE!")
            print("="*60)
            
            # Show output locations
            audio_file = Path(results['input_info']['audio_file']).stem
            print(f"\n📂 OUTPUT FILES:")
            print(f"   📄 Transcript: transcripts/{audio_file}.txt")
            print(f"   📄 Summary: summaries/{audio_file}.txt")
            print(f"   📊 Report: reports/{audio_file}.md")
            
            if VISUALIZATION_CONFIG["enabled"]:
                plot_count = results.get("visualization", {}).get("plots_generated", 0)
                if plot_count > 0:
                    print(f"   🎨 Visualizations: plots/ ({plot_count} files)")
            
            # Show statistics
            stats = results.get('processing_info', {})
            print(f"\n⏱️  Processing Time: {stats.get('total_time', 0):.1f} seconds")
            
            # Auto-open report if requested
            if args.auto_open:
                try:
                    report_path = Path(__file__).parent / "reports" / f"{audio_file}.md"
                    if report_path.exists():
                        webbrowser.open(f"file://{report_path}")
                        print(f"\n📖 Opened report in browser")
                except:
                    print(f"\n⚠️  Could not open report automatically")
            
            return 0  # Success
        else:
            print("\n❌ Processing failed")
            return 1  # Failure
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

def run_web_mode(args):
    """Run in web interface mode"""
    try:
        # Import and run Flask app
        try:
            from app import app
        except ImportError:
            print("\n❌ Web interface not found!")
            print("Please make sure app.py exists in the current directory.")
            print("Or install web dependencies:")
            print("  pip install Flask Flask-CORS")
            return 1
        
        print("\n" + "="*60)
        print("🌐 Starting Web Interface")
        print("="*60)
        
        # Check backend availability
        backend_ok, backend_msg = check_dependencies()
        print(f"Backend: {backend_msg}")
        
        # Create necessary directories
        directories = ['uploads', 'web_results', 'static/css', 'static/js', 'templates']
        for dir_name in directories:
            dir_path = Path(dir_name)
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📂 Web directories ready")
        print(f"🔌 Port: {args.port}")
        print(f"🌍 Host: {args.host}")
        print(f"\n👉 Open: http://{args.host}:{args.port}")
        print("="*60)
        
        # Auto-open browser if requested
        if args.auto_open:
            try:
                webbrowser.open(f"http://{args.host}:{args.port}")
                print("\n📖 Opening browser...")
            except:
                pass
        
        # Run Flask app
        app.run(
            debug=args.debug,
            host=args.host,
            port=args.port,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Web server stopped by user")
        return 130
    except Exception as e:
        print(f"\n❌ Web server error: {e}")
        return 1

def run_interactive_mode():
    """Run in interactive mode"""
    print_banner()
    
    while True:
        print("\n" + "="*50)
        print("SELECT MODE:")
        print("="*50)
        print("1. 🚀 CLI Mode - Process audio/video file or URL")
        print("2. 🌐 Web Mode - Start browser interface")
        print("3. ⚡ Quick Test - Test with sample YouTube video")
        print("4. 🔧 Check Dependencies")
        print("5. 📋 View Recent Results")
        print("6. 🚪 Exit")
        print("="*50)
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            # CLI mode
            input_path = input("\nEnter file path or YouTube URL: ").strip()
            if not input_path:
                print("❌ No input provided")
                continue
            
            output_name = input("Output name (optional, press Enter for auto): ").strip()
            quick_mode = input("Quick mode? (y/N): ").strip().lower() == 'y'
            no_plots = input("Disable plots? (y/N): ").strip().lower() == 'y'
            
            # Build arguments
            class Args:
                pass
            
            args = Args()
            args.input = input_path
            args.output = output_name if output_name else None
            args.quick = quick_mode
            args.no_plots = no_plots
            args.no_enhance = False
            args.no_progress = False
            args.auto_open = False
            
            run_cli_mode(args)
            
        elif choice == "2":
            # Web mode
            port = input("\nEnter port (default: 5000): ").strip()
            port = int(port) if port.isdigit() else 5000
            
            class Args:
                pass
            
            args = Args()
            args.port = port
            args.host = "0.0.0.0"
            args.debug = True
            args.auto_open = True
            
            run_web_mode(args)
            break  # Exit after web server stops
            
        elif choice == "3":
            # Quick test
            print("\n" + "="*50)
            print("⚡ QUICK TEST MODE")
            print("="*50)
            
            test_url = "https://www.youtube.com/watch?v=DWYP8vJ0PjU"  # Short test video
            print(f"Using test video: {test_url}")
            print("This is a 1-minute video for quick testing.")
            
            confirm = input("\nStart test? (Y/n): ").strip().lower()
            if confirm and confirm != 'y':
                continue
            
            class Args:
                pass
            
            args = Args()
            args.input = test_url
            args.output = "quick_test"
            args.quick = True
            args.no_plots = True
            args.no_enhance = True
            args.no_progress = False
            args.auto_open = False
            
            run_cli_mode(args)
            
        elif choice == "4":
            # Check dependencies
            print("\n" + "="*50)
            print("🔧 DEPENDENCY CHECK")
            print("="*50)
            
            backend_ok, backend_msg = check_dependencies()
            print(f"\nBackend: {backend_msg}")
            
            # Check for common packages
            packages = [
                ('Flask', 'flask', 'Web interface'),
                ('Whisper', 'whisper', 'Speech recognition'),
                ('Transformers', 'transformers', 'NLP models'),
                ('PyTorch', 'torch', 'Deep learning'),
                ('FFmpeg', 'ffmpeg', 'Audio processing'),
            ]
            
            print("\nPackage Status:")
            for display_name, import_name, purpose in packages:
                try:
                    if import_name == 'ffmpeg':
                        # Check ffmpeg system command
                        import subprocess
                        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
                        if result.returncode == 0:
                            version = result.stdout.split('\n')[0].split(' ')[2]
                            print(f"  ✓ {display_name:15} v{version} - {purpose}")
                        else:
                            print(f"  ✗ {display_name:15} NOT FOUND - {purpose}")
                    else:
                        module = __import__(import_name)
                        version = getattr(module, '__version__', 'unknown')
                        print(f"  ✓ {display_name:15} v{version} - {purpose}")
                except ImportError:
                    print(f"  ✗ {display_name:15} NOT INSTALLED - {purpose}")
                except Exception:
                    print(f"  ? {display_name:15} UNKNOWN - {purpose}")
            
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            # View recent results
            print("\n" + "="*50)
            print("📋 RECENT RESULTS")
            print("="*50)
            
            result_dirs = ['transcripts', 'summaries', 'reports', 'plots']
            has_results = False
            
            for dir_name in result_dirs:
                dir_path = Path(dir_name)
                if dir_path.exists():
                    files = list(dir_path.glob("*.*"))
                    if files:
                        has_results = True
                        print(f"\n📁 {dir_name.upper()}:")
                        for file in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                            size_mb = file.stat().st_size / (1024 * 1024)
                            mtime = datetime.fromtimestamp(file.stat().st_mtime)
                            print(f"  • {file.name} ({size_mb:.1f} MB, {mtime:%Y-%m-%d %H:%M})")
            
            if not has_results:
                print("\nNo results found. Run an analysis first!")
            
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-6.")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AI Audio Summarizer - CLI and Web Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process YouTube video
  python run.py https://youtu.be/UMdig0gbdUE --output my_video
  
  # Process local file
  python run.py audio.mp3 --quick --no-plots
  
  # Start web interface
  python run.py --web --port 8080
  
  # Interactive mode
  python run.py
        """
    )
    
    # Input arguments (for CLI mode)
    parser.add_argument("input", nargs="?", help="Audio file or YouTube URL")
    parser.add_argument("--output", "-o", help="Output base name")
    
    # Mode selection
    parser.add_argument("--web", "-w", action="store_true", 
                       help="Start web interface")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="Start interactive mode")
    
    # Processing options
    parser.add_argument("--quick", "-q", action="store_true", 
                       help="Quick mode (skip some analysis)")
    parser.add_argument("--no-enhance", action="store_true",
                       help="Disable audio enhancement")
    parser.add_argument("--no-plots", action="store_true",
                       help="Disable visualizations")
    parser.add_argument("--no-progress", action="store_true",
                       help="Disable progress indicators")
    parser.add_argument("--auto-open", action="store_true",
                       help="Auto-open report in browser")
    
    # Web interface options
    parser.add_argument("--port", "-p", type=int, default=5000,
                       help="Port for web interface (default: 5000)")
    parser.add_argument("--host", default="0.0.0.0",
                       help="Host for web interface (default: 0.0.0.0)")
    parser.add_argument("--debug", "-d", action="store_true",
                       help="Enable debug mode for web interface")
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check dependencies
    backend_ok, backend_msg = check_dependencies()
    print(f"Status: {backend_msg}")
    
    # Determine mode
    if args.interactive:
        # Interactive mode
        run_interactive_mode()
    elif args.web:
        # Web interface mode
        run_web_mode(args)
    elif args.input:
        # CLI mode with input
        return run_cli_mode(args)
    else:
        # No arguments, show help
        parser.print_help()
        print("\n" + "="*60)
        print("💡 TIP: Run without arguments for interactive mode")
        print("       Or use --help for all options")
        print("="*60)
        
        # Ask if user wants interactive mode
        choice = input("\nStart interactive mode? (Y/n): ").strip().lower()
        if not choice or choice == 'y':
            run_interactive_mode()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())