# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\transcription\whisper_transcriber.py
from typing import List, Dict
from models_manager import get_model

def transcribe_audio(audio_path: str, language: str = "en") -> Dict:
    """
    Transcribe audio using Whisper model with confidence filtering
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
        low_confidence_count = 0
        total_segments = len(result.get("segments", []))
        
        for seg in result.get("segments", []):
            text = seg.get("text", "").strip()
            
            # ============================================
            # ADD CONFIDENCE FILTER HERE
            # ============================================
            # Get confidence score (avg_logprob)
            # Higher = more confident (0 = perfect, -1 = very uncertain)
            confidence = seg.get("avg_logprob", -1.0)
            
            # Only keep segments with good confidence (above -0.6)
            # Adjust this threshold as needed:
            # -0.3 = very strict (only very clear speech)
            # -0.6 = balanced (default, filters noisy parts)
            # -1.0 = no filtering (keeps everything)
            if text and confidence > -0.6:  # ← CONFIDENCE FILTER
                segments.append({
                    "start": seg.get("start", 0.0),
                    "end": seg.get("end", 0.0),
                    "text": text
                })
            else:
                low_confidence_count += 1
                if text and confidence <= -0.6:
                    print(f"   ⚠️ Skipping low-confidence: '{text[:40]}...' (conf: {confidence:.2f})")
        
        # Build full text from filtered segments
        full_text = " ".join([s["text"] for s in segments]).strip()
        duration = result.get("duration", 0.0)
        
        print(f"   ✅ Transcribed {len(segments)}/{total_segments} segments, {len(full_text.split())} words")
        if low_confidence_count > 0:
            print(f"   ⚠️ Skipped {low_confidence_count} low-confidence segments")
        
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