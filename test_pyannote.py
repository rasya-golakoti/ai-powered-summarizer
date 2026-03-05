"""
Test Pyannote diarization directly
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from pyannote.audio import Pipeline
import torch

def test_pyannote():
    print("\n" + "="*60)
    print("🎤 TESTING PYANNOTE DIRECTLY")
    print("="*60)
    
    # 1. Load pipeline
    print("\n1️⃣ Loading pipeline...")
    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=True
        )
        print("✅ Pipeline loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return
    
    # 2. Check if CUDA is available
    print(f"\n2️⃣ Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    
    # 3. Test with a sample audio file
    test_file = Path("audio_uploads") / "172b8e344ede41268b839d7484aadb75.mp3"
    if test_file.exists():
        print(f"\n3️⃣ Testing with: {test_file.name}")
        try:
            diarization = pipeline(str(test_file))
            
            # Count speakers
            speakers = set()
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                speakers.add(speaker)
                segments.append({
                    "speaker": speaker,
                    "start": turn.start,
                    "end": turn.end,
                    "duration": turn.end - turn.start
                })
            
            print(f"   Detected {len(speakers)} speakers: {', '.join(speakers)}")
            
            # Show distribution
            if segments:
                print(f"\n   Segment breakdown:")
                speaker_durations = {}
                for seg in segments:
                    speaker_durations[seg['speaker']] = speaker_durations.get(seg['speaker'], 0) + seg['duration']
                
                for speaker, duration in speaker_durations.items():
                    print(f"      {speaker}: {duration:.1f}s")
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print(f"\n3️⃣ No test file found at {test_file}")

if __name__ == "__main__":
    test_pyannote()