"""
Emotion Detection using pretrained sentiment models - Enhanced Version
"""

from typing import Dict, List
from models_manager import get_model

def analyze_emotions(text: str) -> Dict:
    """
    Analyze emotions in text with enhanced processing
    """
    emotion_classifier = get_model("emotion_classifier")
    
    if emotion_classifier is None:
        return get_fallback_emotions(text)
    
    try:
        # Clean text before emotion analysis
        text = clean_text_for_emotion(text)
        
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
        
        # NEW: Add confidence level indicator
        confidence_level = get_confidence_level(dominant[1])
        
        # NEW: Add emotion intensity
        emotion_intensity = get_emotion_intensity(emotion_scores)
        
        return {
            "emotion_scores": emotion_scores,
            "dominant_emotion": dominant[0],
            "dominant_score": dominant[1],
            "confidence_level": confidence_level,
            "emotion_intensity": emotion_intensity,
            "emotion_count": len(emotion_scores)
        }
        
    except Exception as e:
        print(f"Emotion analysis failed: {e}")
        return get_fallback_emotions(text)


def clean_text_for_emotion(text: str) -> str:
    """
    Clean text specifically for emotion analysis
    """
    import re
    
    # Remove speaker labels (e.g., "Emily:")
    text = re.sub(r'\b\w+:\s*', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    
    # Remove very short sentences (less than 3 words)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    cleaned_sentences = [s for s in sentences if len(s.split()) >= 3]
    text = ' '.join(cleaned_sentences)
    
    return text.strip()


def get_confidence_level(dominant_score: float) -> str:
    """
    Determine confidence level based on dominant emotion score
    """
    if dominant_score > 0.7:
        return "High"
    elif dominant_score > 0.5:
        return "Medium"
    else:
        return "Low (mixed emotions)"


def get_emotion_intensity(scores: Dict[str, float]) -> str:
    """
    Determine overall emotional intensity
    """
    # Calculate how spread out the emotions are
    # High intensity = one dominant emotion (>60%)
    # Low intensity = emotions are spread out
    
    max_score = max(scores.values()) if scores else 0
    
    if max_score > 0.6:
        return "High - Strong single emotion detected"
    elif max_score > 0.4:
        return "Moderate - Clear emotional tone"
    else:
        return "Low - Mixed or neutral emotional state"


def get_fallback_emotions(text: str) -> Dict:
    """Fallback emotion analysis using TextBlob"""
    try:
        from textblob import TextBlob
        
        blob = TextBlob(text)
        sentiment = blob.sentiment
        
        # Map polarity to emotions with more granularity
        polarity = sentiment.polarity
        
        if polarity > 0.5:
            emotion = "joy"
            score = polarity
        elif polarity > 0.2:
            emotion = "slightly positive"
            score = polarity
        elif polarity > 0.1:
            emotion = "surprise"
            score = polarity
        elif polarity < -0.5:
            emotion = "anger"
            score = abs(polarity)
        elif polarity < -0.2:
            emotion = "sadness"
            score = abs(polarity)
        elif polarity < -0.1:
            emotion = "fear"
            score = abs(polarity)
        else:
            emotion = "neutral"
            score = 0.7
        
        # Also detect subjectivity as secondary emotion
        subjectivity = sentiment.subjectivity
        secondary_emotion = "neutral"
        secondary_score = 0.3
        
        if subjectivity > 0.6 and emotion != "joy":
            secondary_emotion = "joy"
            secondary_score = subjectivity * 0.5
        
        return {
            "emotion_scores": {
                emotion: score,
                secondary_emotion: secondary_score,
                "neutral": 0.1
            },
            "dominant_emotion": emotion,
            "dominant_score": score,
            "confidence_level": "Low (fallback mode)",
            "emotion_intensity": "Moderate",
            "emotion_count": 3
        }
        
    except:
        return {
            "emotion_scores": {"neutral": 1.0},
            "dominant_emotion": "neutral",
            "dominant_score": 1.0,
            "confidence_level": "Low",
            "emotion_intensity": "Low",
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


# NEW: Function to format emotion for display
def format_emotion_for_display(emotion_data: Dict) -> str:
    """
    Format emotion results for better display
    """
    if not emotion_data:
        return "Emotion not detected"
    
    dominant = emotion_data.get('dominant_emotion', 'unknown')
    dominant_score = emotion_data.get('dominant_score', 0)
    scores = emotion_data.get('emotion_scores', {})
    
    # Create visual representation
    lines = []
    lines.append(f"🎭 **Dominant Emotion:** {dominant.upper()} ({dominant_score*100:.1f}%)")
    lines.append(f"📊 **Confidence:** {emotion_data.get('confidence_level', 'Unknown')}")
    lines.append("")
    lines.append("**Emotion Distribution:**")
    
    # Sort scores by value descending
    for emotion, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        if emotion != dominant:
            lines.append(f"  • {emotion}: {score*100:.1f}%")
    
    lines.append("")
    lines.append(f"💭 **Intensity:** {emotion_data.get('emotion_intensity', 'Unknown')}")
    
    return "\n".join(lines)