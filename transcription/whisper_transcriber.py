# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\transcription\whisper_transcriber.py
from typing import List, Dict
from models_manager import get_model

def transcribe_audio(audio_path: str, language: str = "en") -> Dict:
    """
    Transcribe audio using Whisper model
    """
    whisper_model = get_model("whisper")
    
    if not whisper_model:
        print("❌ Whisper model not loaded")
        return {"text": "", "segments": [], "duration": 0.0}
    
    print(f"🎧 Transcribing with Whisper...")
    
    try:
        # Optimized transcription settings
        result = whisper_model.transcribe(
            audio_path,
            language=language,
            task="transcribe",
            fp16=False,
            verbose=False,
            temperature=0.0,
            best_of=1,
            beam_size=3
        )
        
        segments = []
        for seg in result.get("segments", []):
            if seg.get("text", "").strip():
                segments.append({
                    "start": seg.get("start", 0.0),
                    "end": seg.get("end", 0.0),
                    "text": seg.get("text", "").strip()
                })
        full_text = result.get("text", "").strip()
        duration = result.get("duration", 0.0)
        print(f"   ✅ Transcribed {len(segments)} segments, {len(full_text.split())} words")
        return {
            "text": full_text,
            "segments": segments,
            "duration": duration
        }
        
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return {"text": "", "segments": [], "duration": 0.0}

def format_segments_with_timestamps(segments: List[Dict]) -> str:
    """
    Format segments with readable timestamps
    """
    formatted = []
    for seg in segments:
        start_mins = int(seg["start"] // 60)
        start_secs = int(seg["start"] % 60)
        formatted.append(f"[{start_mins:02d}:{start_secs:02d}] {seg['text']}")
    
    return "\n".join(formatted)

def get_full_transcript_text(segments: List[Dict]) -> str:
    """
    Extract just the text from segments
    """
    return " ".join(s["text"] for s in segments).strip()