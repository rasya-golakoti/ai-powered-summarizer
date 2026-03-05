# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\analysis\topic_segmenter.py
from typing import List, Dict

def segment_into_topics(text: str, segments: List[Dict]) -> List[Dict]:
    """
    Automatic topic segmentation with timeline
    """
    sentences = [s.strip() for s in text.split('. ') if s.strip()]
    
    topics = []
    current_topic = []
    topic_id = 0
    
    for i, sentence in enumerate(sentences):
        current_topic.append(sentence)
        
        # Segment after 3-5 sentences or on topic change
        if len(current_topic) >= 4 or i == len(sentences) - 1:
            topic_text = '. '.join(current_topic)
            
            # Estimate timestamps based on word positions
            word_count_before = sum(len(s.split()) for s in sentences[:i-len(current_topic)+1])
            word_count_after = word_count_before + sum(len(s.split()) for s in current_topic)
            
            # ~3 words per second assumption
            time_start = (word_count_before / 3) * 60
            time_end = (word_count_after / 3) * 60
            
            topics.append({
                "topic_id": topic_id,
                "title": f"Topic {topic_id+1}",
                "text": topic_text,
                "time_start": time_start,
                "time_end": time_end,
                "duration": time_end - time_start,
                "word_count": len(topic_text.split())
            })
            
            current_topic = []
            topic_id += 1
    
    return topics

def detect_topic_changes(segments: List[Dict]) -> List[int]:
    """
    Detect points where topic likely changes
    """
    change_points = [0]  # Start is always a change
    
    for i in range(1, len(segments)):
        prev_text = segments[i-1]["text"].lower()
        curr_text = segments[i]["text"].lower()
        
        # Calculate word overlap
        prev_words = set(prev_text.split()[:15])
        curr_words = set(curr_text.split()[:15])
        overlap = len(prev_words.intersection(curr_words))
        
        # Topic change if low overlap and time gap
        time_gap = segments[i]["start"] - segments[i-1]["end"]
        if overlap < 3 and time_gap > 1.5:
            change_points.append(i)
    
    return change_points