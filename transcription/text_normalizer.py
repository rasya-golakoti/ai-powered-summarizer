# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\transcription\text_normalizer.py
import re
from typing import List

def normalize_text(text: str) -> str:
    """
    Clean and normalize transcript text with advanced cleaning
    """
    if not text:
        return ""
    
    # Step 1: Remove filler words
    text = remove_fillers(text)
    
    # Step 2: Merge short sentences (fixes fragmentation)
    text = merge_short_sentences(text, min_words=5)
    
    # Step 3: Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', text)
    
    # Step 4: Fix common punctuation issues
    normalized = re.sub(r'(\w)\.(\w)', r'\1. \2', normalized)
    normalized = re.sub(r'\s+([.,!?])', r'\1', normalized)
    
    # Step 5: Remove speaker labels if they appear as text (e.g., "Emily:")
    normalized = re.sub(r'\b(\w+):\s*', '', normalized)
    
    # Step 6: Capitalize sentences
    sentences = [s.strip() for s in normalized.split('. ') if s.strip()]
    normalized = '. '.join([s[0].upper() + s[1:] if s else s for s in sentences])
    
    # Step 7: Add final period if missing
    if normalized and not normalized.endswith('.'):
        normalized += '.'
    
    return normalized


def merge_short_sentences(text: str, min_words: int = 5) -> str:
    """
    Merge sentences shorter than min_words with the next sentence
    This fixes fragmented transcripts from overlapping or choppy speech
    """
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if len(sentences) <= 1:
        return text
    
    merged = []
    buffer = ""
    
    for i, sentence in enumerate(sentences):
        sentence = sentence.strip()
        if not sentence:
            continue
            
        buffer += " " + sentence if buffer else sentence
        word_count = len(buffer.split())
        
        # If buffer has enough words or it's the last sentence, keep it
        if word_count >= min_words or i == len(sentences) - 1:
            merged.append(buffer.strip())
            buffer = ""
    
    return ". ".join(merged)


def remove_fillers(text: str) -> str:
    """
    Remove common filler words and speech disfluencies
    """
    # Common filler words in English speech
    fillers = [
        "um", "uh", "ah", "er", "mm", "hmm",
        "like", "you know", "actually", "basically",
        "sort of", "kind of", "I mean", "well",
        "so", "okay", "right", "yeah"
    ]
    
    # Pattern for whole word matching with word boundaries
    for filler in fillers:
        pattern = r'\b' + re.escape(filler) + r'\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove multiple spaces created by filler removal
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


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


def clean_speaker_labels(text: str) -> str:
    """
    Remove speaker labels like "Emily:" or "Teacher:" from text
    """
    # Pattern matches words followed by colon at start of sentence or after punctuation
    pattern = r'(^|\s)(\w+):\s*'
    cleaned = re.sub(pattern, r'\1', text)
    return cleaned


def normalize_conversation(text: str) -> str:
    """
    Special normalization for conversational audio
    Combines multiple cleaning steps for dialogue
    """
    # Remove filler words first
    text = remove_fillers(text)
    
    # Merge short utterances (common in conversation)
    text = merge_short_sentences(text, min_words=4)
    
    # Clean speaker labels
    text = clean_speaker_labels(text)
    
    # Fix punctuation
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    
    # Capitalize properly
    sentences = [s.strip() for s in text.split('. ') if s.strip()]
    text = '. '.join([s[0].upper() + s[1:] if s else s for s in sentences])
    
    return text