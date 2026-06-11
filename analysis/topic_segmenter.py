"""
Topic Segmentation with Semantic Change Detection
"""

from typing import List, Dict
import re

def segment_into_topics(text: str, segments: List[Dict]) -> List[Dict]:
    """
    Automatic topic segmentation with semantic change detection
    """
    if not text or not segments:
        return []
    
    # Step 1: Clean and prepare text
    sentences = clean_and_split_sentences(text)
    
    if len(sentences) < 3:
        return create_single_topic(sentences, segments)
    
    # Step 2: Detect topic change points using multiple methods
    change_points = detect_topic_changes_enhanced(sentences, segments)
    
    # Step 3: Create topics based on change points
    topics = create_topics_from_changes(sentences, segments, change_points)
    
    return topics


def clean_and_split_sentences(text: str) -> List[str]:
    """
    Clean text and split into sentences properly
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    # Clean each sentence
    cleaned = []
    for s in sentences:
        s = s.strip()
        if len(s.split()) >= 3:  # Skip very short sentences
            cleaned.append(s)
    
    return cleaned


def detect_topic_changes_enhanced(sentences: List[str], segments: List[Dict]) -> List[int]:
    """
    Detect topic change points using multiple methods
    """
    if len(sentences) < 2:
        return [0]
    
    change_points = [0]  # Start is always a change point
    
    # Method 1: Word overlap analysis
    overlap_changes = detect_overlap_changes(sentences)
    
    # Method 2: Segment timing analysis (pauses indicate topic changes)
    timing_changes = detect_timing_changes(segments)
    
    # Method 3: Keyword shift analysis
    keyword_changes = detect_keyword_changes(sentences)
    
    # Combine all methods (a change is detected if 2 out of 3 methods agree)
    for i in range(1, len(sentences)):
        vote_count = 0
        if i in overlap_changes:
            vote_count += 1
        if i in timing_changes:
            vote_count += 1
        if i in keyword_changes:
            vote_count += 1
        
        if vote_count >= 2:  # At least 2 methods agree
            change_points.append(i)
    
    return change_points


def detect_overlap_changes(sentences: List[str]) -> List[int]:
    """
    Detect topic changes by analyzing word overlap between consecutive sentences
    """
    changes = []
    
    for i in range(1, len(sentences)):
        prev_words = set(sentences[i-1].lower().split())
        curr_words = set(sentences[i].lower().split())
        
        # Calculate overlap ratio
        if len(prev_words) > 0 and len(curr_words) > 0:
            overlap = len(prev_words.intersection(curr_words))
            total_words = min(len(prev_words), len(curr_words))
            overlap_ratio = overlap / total_words if total_words > 0 else 0
            
            # Low overlap indicates potential topic change
            if overlap_ratio < 0.2:  # Less than 20% word overlap
                changes.append(i)
    
    return changes


def detect_timing_changes(segments: List[Dict]) -> List[int]:
    """
    Detect topic changes based on time gaps between segments
    Long pauses often indicate topic changes in conversation
    """
    changes = []
    
    for i in range(1, len(segments)):
        time_gap = segments[i]['start'] - segments[i-1]['end']
        
        # Gap > 1.5 seconds indicates potential topic change
        if time_gap > 1.5:
            changes.append(i)
    
    return changes


def detect_keyword_changes(sentences: List[str]) -> List[int]:
    """
    Detect topic changes by analyzing keyword shifts
    """
    # Common topic-specific keywords
    topic_keywords = {
        'family': ['family', 'mother', 'father', 'brother', 'sister', 'parents', 'children'],
        'work': ['work', 'job', 'office', 'colleague', 'boss', 'career', 'company'],
        'food': ['food', 'restaurant', 'eat', 'meal', 'cook', 'dinner', 'lunch'],
        'travel': ['travel', 'trip', 'flight', 'hotel', 'vacation', 'journey', 'destination'],
        'education': ['school', 'college', 'study', 'learn', 'teacher', 'student', 'class'],
        'health': ['health', 'doctor', 'hospital', 'medicine', 'exercise', 'fitness'],
        'entertainment': ['movie', 'music', 'game', 'watch', 'listen', 'play', 'fun']
    }
    
    changes = []
    
    for i in range(1, len(sentences)):
        prev_sent = sentences[i-1].lower()
        curr_sent = sentences[i].lower()
        
        # Find which topics are present in each sentence
        prev_topics = set()
        curr_topics = set()
        
        for topic, keywords in topic_keywords.items():
            if any(kw in prev_sent for kw in keywords):
                prev_topics.add(topic)
            if any(kw in curr_sent for kw in keywords):
                curr_topics.add(topic)
        
        # If topics don't overlap, it's a change
        if prev_topics and curr_topics and not prev_topics.intersection(curr_topics):
            changes.append(i)
    
    return changes


def create_topics_from_changes(sentences: List[str], segments: List[Dict], change_points: List[int]) -> List[Dict]:
    """
    Create topic objects from detected change points
    """
    topics = []
    
    for idx, start_idx in enumerate(change_points):
        # Determine end index
        if idx + 1 < len(change_points):
            end_idx = change_points[idx + 1]
        else:
            end_idx = len(sentences)
        
        # Get sentences for this topic
        topic_sentences = sentences[start_idx:end_idx]
        if not topic_sentences:
            continue
        
        topic_text = '. '.join(topic_sentences)
        
        # Estimate timestamps from segments
        time_start, time_end = estimate_timestamps(topic_sentences, segments, start_idx, end_idx)
        
        # Generate topic title
        topic_title = generate_topic_title(topic_sentences)
        
        topics.append({
            "topic_id": idx,
            "title": topic_title,
            "text": topic_text,
            "time_start": time_start,
            "time_end": time_end,
            "duration": time_end - time_start,
            "word_count": len(topic_text.split()),
            "sentence_count": len(topic_sentences)
        })
    
    return topics


def estimate_timestamps(topic_sentences: List[str], segments: List[Dict], start_idx: int, end_idx: int) -> tuple:
    """
    Estimate start and end times for a topic based on sentence positions
    """
    # Count words before this topic
    words_before = 0
    for i in range(start_idx):
        words_before += len(topic_sentences[i - start_idx].split()) if i < len(topic_sentences) else 0
    
    # Count words in this topic
    topic_words = sum(len(s.split()) for s in topic_sentences)
    
    # Use segment timestamps if available
    if segments and start_idx < len(segments):
        # Approximate based on segment order
        segment_ratio = start_idx / max(len(segments), 1)
        time_start = segments[0]['start'] + segment_ratio * (segments[-1]['end'] - segments[0]['start'])
        time_end = time_start + (topic_words / 3)  # ~3 words per second
    else:
        # Fallback: estimate from word count
        time_start = (words_before / 3) if words_before > 0 else 0
        time_end = time_start + (topic_words / 3)
    
    return time_start, time_end


def generate_topic_title(sentences: List[str]) -> str:
    """
    Generate a descriptive title for the topic
    """
    if not sentences:
        return "Untitled Topic"
    
    # Take first sentence and extract key words
    first_sentence = sentences[0]
    
    # Remove common question words and filler
    title = re.sub(r'^(How|What|Why|When|Where|Who|Do|Does|Is|Are)\s+', '', first_sentence)
    
    # Limit to 5-8 words
    words = title.split()
    if len(words) > 7:
        title = ' '.join(words[:7]) + '...'
    
    return title.capitalize()


def create_single_topic(sentences: List[str], segments: List[Dict]) -> List[Dict]:
    """
    Create a single topic when text is too short
    """
    if not sentences:
        return []
    
    topic_text = '. '.join(sentences)
    
    time_start = segments[0]['start'] if segments else 0
    time_end = segments[-1]['end'] if segments else (len(topic_text.split()) / 3)
    
    return [{
        "topic_id": 0,
        "title": generate_topic_title(sentences),
        "text": topic_text,
        "time_start": time_start,
        "time_end": time_end,
        "duration": time_end - time_start,
        "word_count": len(topic_text.split()),
        "sentence_count": len(sentences)
    }]


def detect_topic_changes(segments: List[Dict]) -> List[int]:
    """
    Original function kept for compatibility
    """
    change_points = [0]
    
    for i in range(1, len(segments)):
        prev_text = segments[i-1]["text"].lower()
        curr_text = segments[i]["text"].lower()
        
        prev_words = set(prev_text.split()[:15])
        curr_words = set(curr_text.split()[:15])
        overlap = len(prev_words.intersection(curr_words))
        
        time_gap = segments[i]["start"] - segments[i-1]["end"]
        if overlap < 3 and time_gap > 1.5:
            change_points.append(i)
    
    return change_points