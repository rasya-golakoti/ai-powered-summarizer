"""
Chapter Generator with Intelligent Naming
"""

from typing import List, Dict
from config import MAX_CHAPTERS
import re

def generate_chapters(topics: List[Dict]) -> List[Dict]:
    """
    Generate chapters from topics with intelligent naming
    """
    if not topics:
        return []
    
    chapters = []
    
    for i, topic in enumerate(topics[:MAX_CHAPTERS]):
        # Format time as MM:SS
        start_mins = int(topic['time_start'] // 60)
        start_secs = int(topic['time_start'] % 60)
        end_mins = int(topic['time_end'] // 60)
        end_secs = int(topic['time_end'] % 60)
        
        start_time = f"{start_mins:02d}:{start_secs:02d}"
        end_time = f"{end_mins:02d}:{end_secs:02d}"
        
        # Generate intelligent chapter title
        chapter_name = generate_chapter_name(topic, i + 1)
        
        # Generate better topic title (clean, not cut mid-sentence)
        topic_title = generate_topic_title(topic['text'])
        
        # Generate meaningful description
        description = generate_chapter_description(topic['text'])
        
        chapters.append({
            "chapter": i + 1,
            "title": f"Chapter {i+1}: {chapter_name}",
            "topic_title": topic_title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "duration": f"{topic['duration']:.1f}s",
            "time_start": topic['time_start'],
            "time_end": topic['time_end'],
            "word_count": topic.get('word_count', 0)
        })
    
    return chapters


def generate_chapter_name(topic: Dict, chapter_num: int) -> str:
    """
    Generate intelligent chapter name based on content
    """
    text = topic.get('text', '')
    
    # Try to extract key phrase (first meaningful sentence)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if sentences:
        first_sentence = sentences[0].strip()
        
        # Clean up the sentence
        first_sentence = re.sub(r'^(How|What|Why|When|Where|Who|Do|Does|Is|Are)\s+', '', first_sentence)
        first_sentence = re.sub(r'[.!?]$', '', first_sentence)
        
        # Limit length
        words = first_sentence.split()
        if len(words) > 6:
            first_sentence = ' '.join(words[:6]) + '...'
        
        if first_sentence and len(first_sentence) > 5:
            return first_sentence.capitalize()
    
    # Fallback to topic-based name
    topic_keywords = extract_topic_keywords(text)
    if topic_keywords:
        return topic_keywords
    
    return f"Topic {chapter_num}"


def generate_topic_title(text: str) -> str:
    """
    Generate a clean topic title (first 6-8 words, complete words only)
    """
    # Remove speaker labels
    text = re.sub(r'\b\w+:\s*', '', text)
    
    # Take first 8 words
    words = text.split()[:8]
    
    if not words:
        return "Topic"
    
    title = ' '.join(words)
    
    # Add ellipsis if we cut off
    if len(text.split()) > 8:
        title += '...'
    
    return title


def generate_chapter_description(text: str) -> str:
    """
    Generate a meaningful chapter description
    """
    # Take first 2-3 sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) >= 2:
        description = ' '.join(sentences[:2])
    elif sentences:
        description = sentences[0]
    else:
        description = text
    
    # Limit length
    if len(description) > 150:
        description = description[:147] + '...'
    
    return description.strip()


def extract_topic_keywords(text: str) -> str:
    """
    Extract key topic keywords for chapter naming
    """
    # Common topic keywords mapping
    keywords_map = {
        'family': ['family', 'mother', 'father', 'brother', 'sister', 'parents'],
        'work': ['work', 'job', 'office', 'company', 'career', 'business'],
        'health': ['health', 'doctor', 'hospital', 'medicine', 'sick', 'pain'],
        'food': ['food', 'restaurant', 'eat', 'meal', 'cook', 'dinner'],
        'travel': ['travel', 'trip', 'flight', 'hotel', 'vacation', 'beach'],
        'school': ['school', 'college', 'study', 'learn', 'teacher', 'student'],
        'shopping': ['shop', 'store', 'buy', 'price', 'money', 'cost'],
        'weather': ['weather', 'rain', 'sun', 'hot', 'cold', 'temperature']
    }
    
    text_lower = text.lower()
    
    for topic, keywords in keywords_map.items():
        for keyword in keywords:
            if keyword in text_lower:
                return topic.capitalize()
    
    return None


def format_chapter_markdown(chapters: List[Dict]) -> str:
    """
    Format chapters in markdown format
    """
    if not chapters:
        return ""
    
    markdown = "## 📖 Chapters\n\n"
    
    for chapter in chapters:
        markdown += f"### {chapter['title']}\n"
        markdown += f"- **Time**: {chapter['start_time']} - {chapter['end_time']}\n"
        markdown += f"- **Duration**: {chapter['duration']}\n"
        markdown += f"- **Summary**: {chapter['description']}\n\n"
    
    return markdown


def generate_chapter_timeline(chapters: List[Dict]) -> List[Dict]:
    """
    Generate simplified timeline for visualization
    """
    timeline = []
    
    for chapter in chapters:
        timeline.append({
            "chapter": chapter["chapter"],
            "title": chapter["title"],
            "start": chapter["time_start"],
            "end": chapter["time_end"],
            "duration": chapter["time_end"] - chapter["time_start"]
        })
    
    return timeline


def generate_chapters_from_topics(topics: List[Dict]) -> List[Dict]:
    """
    Alias for generate_chapters (for main.py compatibility)
    """
    return generate_chapters(topics)