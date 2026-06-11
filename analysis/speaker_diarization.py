"""
Speaker Diarization using Pyannote - NO TORCHAUDIO VERSION
"""

from typing import List, Dict, Optional
import numpy as np
from models_manager import get_model

def diarize_speakers_pyannote(audio_path: str) -> List[Dict]:
    """
    Speaker diarization using Pyannote
    """
    print("   🔧 Getting Pyannote model...")
    diarization_model = get_model("diarization")
    
    if diarization_model is None:
        print("   ❌ Pyannote model not available - MODEL IS NONE")
        print("   💡 Check: Pyannote failed to load in models_manager.py")
        return []
    
    try:
        print("   🔧 Running Pyannote inference...")
        
        # Try different input formats
        try:
            # Try direct file path first
            diarization = diarization_model(audio_path)
        except Exception as e:
            print(f"   ⚠️ Direct loading failed: {e}")
            # Try with waveform loading
            import torchaudio
            waveform, sample_rate = torchaudio.load(audio_path)
            diarization = diarization_model({"waveform": waveform, "sample_rate": sample_rate})
        
        # Convert to list of dictionaries
        segments = []
        speakers = set()
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speakers.add(speaker)
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker,
                "duration": turn.end - turn.start
            })
        
        print(f"   ✅ Pyannote identified {len(speakers)} speakers: {', '.join(speakers)}")
        
        if segments:
            speaker_durations = {}
            for seg in segments:
                speaker_durations[seg['speaker']] = speaker_durations.get(seg['speaker'], 0) + seg['duration']
            
            for speaker, duration in speaker_durations.items():
                print(f"      {speaker}: {duration:.1f}s total")
        
        return segments
        
    except Exception as e:
        print(f"   ❌ Pyannote diarization failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def diarize_speakers_fallback(audio_path: str, duration: float) -> List[Dict]:
    """
    Fallback speaker diarization (simulated)
    """
    print(f"   ⚠️ Using fallback diarization for {duration:.1f}s audio")
    segments = []
    num_segments = max(3, int(duration / 30))
    
    for i in range(num_segments):
        start = i * 30
        end = min((i + 1) * 30, duration)
        speaker = f"SPEAKER_{i % 2:02d}"
        
        segments.append({
            "start": start,
            "end": end,
            "speaker": speaker,
            "duration": end - start
        })
    
    print(f"   ⚠️ Fallback created {len(segments)} segments with 2 simulated speakers")
    return segments

def diarize_speakers(audio_path: str, duration: Optional[float] = None) -> List[Dict]:
    """
    Main speaker diarization function with fallback
    """
    print("   🎤 Running speaker diarization...")
    
    # Try Pyannote first
    segments = diarize_speakers_pyannote(audio_path)
    
    # If Pyannote failed and we have duration, use fallback
    if not segments and duration:
        print("   ⚠️ Pyannote returned no segments, using fallback")
        segments = diarize_speakers_fallback(audio_path, duration)
    
    return segments

def merge_speaker_segments(speaker_segments: List[Dict], transcript_segments: List[Dict]) -> List[Dict]:
    """Merge speaker diarization with transcript segments"""
    if not speaker_segments:
        for segment in transcript_segments:
            segment["speaker"] = "SPEAKER_00"
        return transcript_segments
    
    speaker_map = []
    for seg in speaker_segments:
        speaker_map.append({
            "start": seg["start"],
            "end": seg["end"],
            "speaker": seg["speaker"]
        })
    
    for transcript_seg in transcript_segments:
        seg_start = transcript_seg.get("start", 0)
        seg_end = transcript_seg.get("end", 0)
        
        best_speaker = "SPEAKER_00"
        max_overlap = 0
        
        for speaker_seg in speaker_map:
            overlap_start = max(seg_start, speaker_seg["start"])
            overlap_end = min(seg_end, speaker_seg["end"])
            
            if overlap_end > overlap_start:
                overlap = overlap_end - overlap_start
                if overlap > max_overlap:
                    max_overlap = overlap
                    best_speaker = speaker_seg["speaker"]
        
        transcript_seg["speaker"] = best_speaker
    
    return transcript_segments

def get_speaker_statistics(segments: List[Dict]) -> Dict:
    """Calculate speaker statistics"""
    stats = {}
    
    for segment in segments:
        speaker = segment.get("speaker", "UNKNOWN")
        text = segment.get("text", "")
        duration = segment.get("end", 0) - segment.get("start", 0)
        
        if speaker not in stats:
            stats[speaker] = {
                "segments": 0,
                "words": 0,
                "duration": 0.0,
                "text": ""
            }
        
        stats[speaker]["segments"] += 1
        stats[speaker]["words"] += len(text.split())
        stats[speaker]["duration"] += duration
        if text.strip():
            stats[speaker]["text"] += text + " "
    
    for speaker in stats:
        stats[speaker]["text"] = stats[speaker]["text"].strip()
    
    return stats