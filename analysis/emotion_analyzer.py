
# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\analysis\emotion_analyzer.py
"""
Emotion Detection using pretrained sentiment models
"""

from typing import Dict, List
from models_manager import get_model

def analyze_emotions(text: str) -> Dict:
    """
    Analyze emotions in text
    
    Args:
        text: Input text
        
    Returns:
        Dictionary with emotion analysis
    """
    emotion_classifier = get_model("emotion_classifier")
    
    if emotion_classifier is None:
        return get_fallback_emotions(text)
    
    try:
        # Split text into chunks if too long
        chunks = split_text_into_chunks(text, max_length=512)
        
        all_emotions = []
        for chunk in chunks:
            if chunk.strip():
                try:
                    emotions = emotion_classifier(chunk)[0]
                    all_emotions.extend(emotions)
                except:
                    pass
        
        if not all_emotions:
            return get_fallback_emotions(text)
        
        # Aggregate emotions
        emotion_scores = {}
        for emotion in all_emotions:
            label = emotion['label']
            score = emotion['score']
            emotion_scores[label] = emotion_scores.get(label, 0) + score
        
        # Normalize scores
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {k: v/total for k, v in emotion_scores.items()}
        
        # Get dominant emotion
        if emotion_scores:
            dominant = max(emotion_scores.items(), key=lambda x: x[1])
        else:
            dominant = ("neutral", 1.0)
        
        return {
            "emotion_scores": emotion_scores,
            "dominant_emotion": dominant[0],
            "dominant_score": dominant[1],
            "emotion_count": len(emotion_scores)
        }
        
    except Exception as e:
        print(f"Emotion analysis failed: {e}")
        return get_fallback_emotions(text)

def get_fallback_emotions(text: str) -> Dict:
    """Fallback emotion analysis using TextBlob"""
    try:
        from textblob import TextBlob
        
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Map polarity to emotions
        polarity = sentiment.polarity
        
        if polarity > 0.3:
            emotion = "positive"
        elif polarity > 0.1:
            emotion = "slightly positive"
        elif polarity < -0.3:
            emotion = "negative"
        elif polarity < -0.1:
            emotion = "slightly negative"
        else:
            emotion = "neutral"
        
        return {
            "emotion_scores": {emotion: abs(polarity) + 0.1},
            "dominant_emotion": emotion,
            "dominant_score": abs(polarity) + 0.1,
            "emotion_count": 1
        }
        
    except:
        return {
            "emotion_scores": {"neutral": 1.0},
            "dominant_emotion": "neutral",
            "dominant_score": 1.0,
            "emotion_count": 1
        }

def split_text_into_chunks(text: str, max_length: int = 512) -> List[str]:
    """Split text into chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_length:
            current_chunk.append(word)
            current_length += len(word) + 1
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks