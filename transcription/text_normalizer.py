# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\transcription\text_normalizer.py
import re
from typing import List

def normalize_text(text: str) -> str:
    """
    Clean and normalize transcript text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', text)
    
    # Fix common issues
    normalized = re.sub(r'(\w)\.(\w)', r'\1. \2', normalized)
    normalized = re.sub(r'\s+([.,!?])', r'\1', normalized)
    
    # Capitalize sentences
    sentences = [s.strip() for s in normalized.split('. ') if s.strip()]
    normalized = '. '.join([s[0].upper() + s[1:] if s else s for s in sentences])
    
    # Add final period if missing
    if normalized and not normalized.endswith('.'):
        normalized += '.'
    
    return normalized

def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    """
    sentences = []
    current = ""
    
    for char in text:
        current += char
        if char in '.!?':
            sentences.append(current.strip())
            current = ""
    
    if current.strip():
        sentences.append(current.strip())
    
    return sentences

def remove_fillers(text: str) -> str:
    """
    Remove common filler words
    """
    fillers = ["um", "uh", "ah", "er", "like", "you know", "actually", "basically"]
    
    for filler in fillers:
        pattern = r'\b' + re.escape(filler) + r'\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text