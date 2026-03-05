# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\utils\file_utils.py
"""
File utility functions for AI Audio Summarizer
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

def save_text_file(text: str, filepath: Path, encoding: str = 'utf-8') -> bool:
    """
    Save text to a file
    
    Args:
        text: Text content to save
        filepath: Path to save file
        encoding: File encoding
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding=encoding) as f:
            f.write(text)
        
        print(f"   ✅ Text saved to: {filepath.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to save text file: {e}")
        return False

def save_json_file(data: Dict, filepath: Path, indent: int = 2) -> bool:
    """
    Save data as JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save file
        indent: JSON indentation
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str)
        
        print(f"   ✅ JSON saved to: {filepath.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Failed to save JSON file: {e}")
        return False

def ensure_directory(directory: Path) -> bool:
    """
    Ensure directory exists
    
    Args:
        directory: Directory path
        
    Returns:
        True if directory exists or was created
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"   ❌ Failed to create directory {directory}: {e}")
        return False

def read_text_file(filepath: Path, encoding: str = 'utf-8') -> Optional[str]:
    """
    Read text from file
    
    Args:
        filepath: Path to read file
        encoding: File encoding
        
    Returns:
        Text content or None if failed
    """
    try:
        with open(filepath, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"   ❌ Failed to read file {filepath}: {e}")
        return None

def read_json_file(filepath: Path) -> Optional[Dict]:
    """
    Read JSON from file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dictionary or None if failed
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"   ❌ Failed to read JSON file {filepath}: {e}")
        return None

def get_file_size(filepath: Path, human_readable: bool = True) -> str:
    """
    Get file size
    
    Args:
        filepath: Path to file
        human_readable: Return human-readable format
        
    Returns:
        File size string
    """
    if not filepath.exists():
        return "0 bytes"
    
    size_bytes = filepath.stat().st_size
    
    if not human_readable:
        return str(size_bytes)
    
    # Convert to human readable format
    for unit in ['bytes', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"