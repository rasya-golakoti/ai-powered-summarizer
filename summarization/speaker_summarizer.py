"""
Speaker Summarizer - Fixed version to properly merge speaker segments
"""

from typing import Dict, List
from summarization.dual_summarizer import abstractive_summary

def generate_speaker_summaries(speaker_transcript: List[Dict]) -> Dict:
    """Generate individual summaries for each speaker with proper merging"""
    
    if not speaker_transcript:
        return {}
    
    # First, merge consecutive segments from the same speaker
    merged_segments = merge_consecutive_speaker_segments(speaker_transcript)
    
    # Group text by speaker
    speaker_texts = {}
    for seg in merged_segments:
        speaker = seg["speaker"]
        if speaker not in speaker_texts:
            speaker_texts[speaker] = []
        speaker_texts[speaker].append(seg["text"])
    
    # Generate summaries
    speaker_summaries = {}
    for speaker, texts in speaker_texts.items():
        combined_text = " ".join(texts)
        word_count = len(combined_text.split())
        
        if word_count > 50:
            summary = abstractive_summary(combined_text[:1000])
            if not summary or len(summary.split()) < 5:
                # Fallback: take first few sentences
                sentences = combined_text.split('. ')
                summary = '. '.join(sentences[:3]) + '.'
        else:
            summary = combined_text
        
        # Calculate speaking duration from ORIGINAL segments (for accurate timing)
        speaker_segments = [s for s in speaker_transcript if s["speaker"] == speaker]
        total_duration = sum(s["end"] - s["start"] for s in speaker_segments)
        
        speaker_summaries[speaker] = {
            "summary": summary,
            "full_text": combined_text,  # Store full text too
            "total_words": word_count,
            "total_segments": len(texts),
            "total_duration": total_duration,
            "avg_words_per_segment": word_count / len(texts) if texts else 0
        }
    
    return speaker_summaries

def merge_consecutive_speaker_segments(segments: List[Dict]) -> List[Dict]:
    """
    Merge consecutive segments from the same speaker
    This prevents the display from showing fragmented speaker text
    """
    if not segments:
        return []
    
    merged = []
    current = segments[0].copy()
    
    for i in range(1, len(segments)):
        next_seg = segments[i]
        
        # If same speaker and gap is small, merge them
        if (current["speaker"] == next_seg["speaker"] and 
            next_seg["start"] - current["end"] < 1.0):  # Less than 1 second gap
            
            # Merge text
            current["text"] = current["text"] + " " + next_seg["text"]
            # Update end time
            current["end"] = next_seg["end"]
        else:
            # Different speaker or large gap, add current and start new
            merged.append(current)
            current = next_seg.copy()
    
    # Add the last segment
    merged.append(current)
    
    print(f"   🔄 Merged {len(segments)} segments into {len(merged)} continuous speaker segments")
    return merged

def format_speaker_summaries(speaker_summaries: Dict) -> str:
    """Format speaker summaries for display with proper formatting"""
    if not speaker_summaries:
        return "No speaker summaries available."
    
    formatted = []
    
    for speaker, data in speaker_summaries.items():
        # Format time
        minutes = int(data['total_duration'] // 60)
        seconds = int(data['total_duration'] % 60)
        
        formatted.append(f"{speaker}:")
        formatted.append(f"{data['summary']}")
        formatted.append(f"")
    
    return "\n".join(formatted)

def get_speaker_statistics(speaker_transcript: List[Dict]) -> Dict:
    """Calculate detailed statistics for each speaker"""
    stats = {}
    
    for seg in speaker_transcript:
        speaker = seg["speaker"]
        if speaker not in stats:
            stats[speaker] = {
                "words": 0,
                "segments": 0,
                "duration": 0.0,
                "texts": []
            }
        
        stats[speaker]["words"] += len(seg["text"].split())
        stats[speaker]["segments"] += 1
        stats[speaker]["duration"] += seg["end"] - seg["start"]
        stats[speaker]["texts"].append(seg["text"])
    
    # Calculate percentages
    total_words = sum(s["words"] for s in stats.values())
    total_duration = sum(s["duration"] for s in stats.values())
    
    for speaker in stats:
        if total_words > 0:
            stats[speaker]["word_percentage"] = (stats[speaker]["words"] / total_words) * 100
        if total_duration > 0:
            stats[speaker]["duration_percentage"] = (stats[speaker]["duration"] / total_duration) * 100
    
    return stats

def summarize_speakers(speaker_transcript: List[Dict]) -> Dict:
    """Alias for generate_speaker_summaries"""
    return generate_speaker_summaries(speaker_transcript)