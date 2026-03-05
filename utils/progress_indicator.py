# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\utils\progress_indicator.py
"""
Progress indicators for the pipeline
"""

import sys
import time
import threading
from typing import Optional
from tqdm import tqdm

class ProgressIndicator:
    """Show progress for different pipeline stages"""
    
    @staticmethod
    def step_start(step_number: int, total_steps: int, description: str):
        """Start a new step with progress bar"""
        print(f"\n{'='*60}")
        print(f"STEP {step_number}/{total_steps}: {description}")
        print('='*60)
    
    @staticmethod
    def step_complete(step_number: int, message: str = "Completed"):
        """Mark step as complete"""
        print(f"   ✅ STEP {step_number}: {message}")
    
    @staticmethod
    def step_warning(step_number: int, message: str):
        """Show warning for a step"""
        print(f"   ⚠️ STEP {step_number}: {message}")
    
    @staticmethod
    def step_error(step_number: int, message: str):
        """Show error for a step"""
        print(f"   ❌ STEP {step_number}: {message}")
    
    @staticmethod
    def progress_bar(iterable, desc: str = "Processing", unit: str = "it", 
                    total: Optional[int] = None, color: str = "green"):
        """Wrap iterable with progress bar"""
        return tqdm(iterable, desc=f"   {desc}", unit=unit, total=total, 
                   bar_format="{l_bar}{bar:40}{r_bar}", colour=color)
    
    @staticmethod
    def spinner(message: str, delay: float = 0.1):
        """Create a simple spinner animation"""
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        class Spinner:
            def __init__(self, message: str, delay: float):
                self.message = message
                self.delay = delay
                self.running = False
                self.thread = None
            
            def spin(self):
                i = 0
                while self.running:
                    sys.stdout.write(f'\r   {spinner_chars[i]} {self.message}...')
                    sys.stdout.flush()
                    time.sleep(self.delay)
                    i = (i + 1) % len(spinner_chars)
            
            def __enter__(self):
                self.running = True
                self.thread = threading.Thread(target=self.spin)
                self.thread.start()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.running = False
                if self.thread:
                    self.thread.join()
                sys.stdout.write(f'\r   ✅ {self.message} completed!\n')
                sys.stdout.flush()
        
        return Spinner(message, delay)
    
    @staticmethod
    def percentage_progress(current: int, total: int, message: str = "Progress"):
        """Show percentage progress"""
        percent = (current / total) * 100
        bar_length = 40
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        sys.stdout.write(f'\r   {message}: |{bar}| {percent:.1f}% ({current}/{total})')
        sys.stdout.flush()
        
        if current == total:
            print()  # New line when complete

# Global instance
progress = ProgressIndicator()