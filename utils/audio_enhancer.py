# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\utils\audio_enhancer.py
"""
Audio enhancement utilities including noise reduction
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Optional, Tuple, Dict, List
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

try:
    import noisereduce as nr
    NOISEREDUCE_AVAILABLE = True
except ImportError:
    NOISEREDUCE_AVAILABLE = False
    print("⚠️ noisereduce not installed. Install with: pip install noisereduce")

class AudioEnhancer:
    """Audio enhancement and noise reduction"""
    def adaptive_preemphasis(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        Apply adaptive pre-emphasis based on voice characteristics
        """
        # Estimate average pitch to detect child vs adult voices
        try:
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = pitches[pitches > 0]
            avg_pitch = np.mean(pitch_values) if len(pitch_values) > 0 else 200
        
            # Children typically have higher pitch (>300 Hz)
            if avg_pitch > 300:
                preemphasis_coeff = 0.95  # Less boost for children's voices
                print(f"   👧 Child-like voice detected (pitch: {avg_pitch:.0f}Hz), using coeff={preemphasis_coeff}")
            else:
                preemphasis_coeff = 0.97  # Standard boost for adults
        except:
            preemphasis_coeff = 0.97
    
        return librosa.effects.preemphasis(y, coef=preemphasis_coeff)


    def remove_low_frequency_rumble(self, y: np.ndarray, sr: int, cutoff_hz: int = 80) -> np.ndarray:
        """
        Remove low-frequency noise (rumble, AC hum, etc.)
        """
        from scipy import signal
    
        if sr < cutoff_hz * 2:
            return y  # Can't filter if sample rate is too low
    
        # Design high-pass filter
        nyquist = sr / 2
        normal_cutoff = cutoff_hz / nyquist
        b, a = signal.butter(4, normal_cutoff, btype='high')
    
        # Apply filter
        y_filtered = signal.filtfilt(b, a, y)
    
        print(f"   🔇 Removed frequencies below {cutoff_hz}Hz")
        return y_filtered

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
    
    def enhance_audio(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Enhance audio quality with noise reduction and normalization
        
        Args:
            input_path: Path to input audio file
            output_path: Optional output path (default: same as input with _enhanced suffix)
            
        Returns:
            Path to enhanced audio file
        """
        print("   🔊 Enhancing audio quality...")
        
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input audio file not found: {input_path}")
        
        if output_path is None:
            output_path = str(input_path.parent / f"{input_path.stem}_enhanced.wav")
        
        try:
            # Load audio
            y, sr = librosa.load(str(input_path), sr=self.sample_rate)

            y = self.remove_low_frequency_rumble(y, sr)

            # Apply noise reduction if available
            if NOISEREDUCE_AVAILABLE and len(y) > 10000:
                print("   🔇 Applying noise reduction...")
                y = nr.reduce_noise(y=y, sr=sr, stationary=True)
        
            # Normalize audio
            print("   🔊 Normalizing audio...")
            y = librosa.util.normalize(y)
        
            # Apply adaptive pre-emphasis
            y = self.adaptive_preemphasis(y, sr)
        
            # Save enhanced audio
            sf.write(output_path, y, sr)
        
            print(f"   ✅ Enhanced audio saved: {Path(output_path).name}")
            return output_path
        
        except Exception as e:
            print(f"   ⚠️ Audio enhancement failed: {e}")
            return str(input_path)
    
    def get_audio_info(self, audio_path: str) -> dict:
        """Get detailed audio information"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Calculate RMS (loudness)
            rms = np.sqrt(np.mean(y**2))
            
            # Calculate zero-crossing rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(y))
            
            # Calculate spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_mean = np.mean(spectral_centroids)
            
            return {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[0],
                "rms": float(rms),
                "zero_crossing_rate": float(zcr),
                "spectral_centroid": float(spectral_mean),
                "samples": len(y)
            }
        except Exception as e:
            print(f"   ⚠️ Audio info failed: {e}")
            return {"error": str(e)}
    
    def detect_silence(self, audio_path: str, threshold: float = 0.01) -> list:
        """Detect silence segments in audio"""
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Split into frames
            frame_length = int(0.1 * sr)  # 100ms frames
            hop_length = frame_length // 2
            
            # Calculate RMS energy for each frame
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Find silent frames
            silent_frames = np.where(rms < threshold)[0]
            
            # Convert frames to time segments
            silence_segments = []
            if len(silent_frames) > 0:
                # Group consecutive silent frames
                groups = np.split(silent_frames, np.where(np.diff(silent_frames) != 1)[0] + 1)
                
                for group in groups:
                    if len(group) > 2:  # Minimum 3 frames (300ms) of silence
                        start_time = (group[0] * hop_length) / sr
                        end_time = (group[-1] * hop_length + frame_length) / sr
                        duration = end_time - start_time
                        
                        if duration > 0.5:  # Only report silence > 500ms
                            silence_segments.append({
                                "start": start_time,
                                "end": end_time,
                                "duration": duration
                            })
            
            return silence_segments
            
        except Exception as e:
            print(f"   ⚠️ Silence detection failed: {e}")
            return []

# Global instance
audio_enhancer = AudioEnhancer()