# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\summarization\chapter_generator.py
from typing import List, Dict
from config import MAX_CHAPTERS

def generate_chapters(topics: List[Dict]) -> List[Dict]:
    """Generate chapters from topics"""
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
        
        # Create chapter title from topic
        title_words = topic['text'].split()[:5]
        topic_title = ' '.join(title_words) + ('...' if len(title_words) >= 5 else '')
        
        chapters.append({
            "chapter": i + 1,
            "title": f"Chapter {i+1}: {topic['title']}",
            "topic_title": topic_title,
            "description": topic['text'][:100] + "..." if len(topic['text']) > 100 else topic['text'],
            "start_time": start_time,
            "end_time": end_time,
            "duration": f"{topic['duration']:.1f}s",
            "time_start": topic['time_start'],
            "time_end": topic['time_end'],
            "word_count": topic.get('word_count', 0)
        })
    
    return chapters

def format_chapter_markdown(chapters: List[Dict]) -> str:
    """Format chapters in markdown format"""
    if not chapters:
        return ""
    
    markdown = "## Chapters\n\n"
    
    for chapter in chapters:
        markdown += f"### {chapter['title']}\n"
        markdown += f"- **Time**: {chapter['start_time']} - {chapter['end_time']}\n"
        markdown += f"- **Duration**: {chapter['duration']}\n"
        markdown += f"- **Description**: {chapter['description']}\n\n"
    
    return markdown

def generate_chapter_timeline(chapters: List[Dict]) -> List[Dict]:
    """Generate simplified timeline for visualization"""
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
    """Alias for generate_chapters (for main.py compatibility)"""
    return generate_chapters(topics)