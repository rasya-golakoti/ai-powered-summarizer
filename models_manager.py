"""
Models Manager - Fixed version with proper Pyannote loading
"""

import os
import torch
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
import whisper
import warnings

warnings.filterwarnings("ignore")

class ModelsManager:
    """Singleton class to manage all models"""
    
    _instance = None
    _models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelsManager, cls).__new__(cls)
        return cls._instance
    
    def load_all(self):
        """Load all required models"""
        print("\n" + "="*60)
        print("🤖 LOADING AI MODELS")
        print("="*60)
        
        # 1. Whisper for transcription
        print("\n🔹 1. Loading Whisper (OpenAI)...")
        try:
            self._models["whisper"] = whisper.load_model("base")
            print("   ✅ Whisper loaded")
        except Exception as e:
            print(f"   ❌ Whisper failed: {e}")
            self._models["whisper"] = None
        
        # 2. BART for abstractive summarization
        print("\n🔹 2. Loading BART Summarizer...")
        try:
            model_name = "facebook/bart-large-cnn"
            self._models["bart_tokenizer"] = AutoTokenizer.from_pretrained(model_name)
            self._models["bart_model"] = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            print("   ✅ BART loaded")
        except Exception as e:
            print(f"   ⚠️ BART failed (will use extractive only): {e}")
            self._models["bart_model"] = None
            self._models["bart_tokenizer"] = None
        
        # 3. Sentence Transformer for extractive summarization
        print("\n🔹 3. Loading Sentence Transformer...")
        try:
            self._models["sentence_transformer"] = SentenceTransformer('all-MiniLM-L6-v2')
            print("   ✅ Sentence Transformer loaded")
        except Exception as e:
            print(f"   ❌ Sentence Transformer failed: {e}")
            self._models["sentence_transformer"] = None
        
        # 4. Emotion/Sentiment model
        print("\n🔹 4. Loading Emotion Classifier...")
        try:
            self._models["emotion_classifier"] = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )
            print("   ✅ Emotion classifier loaded")
        except Exception as e:
            print(f"   ⚠️ Emotion classifier failed: {e}")
            self._models["emotion_classifier"] = None
        
        # 5. KeyBERT for keyword extraction
        print("\n🔹 5. Loading KeyBERT...")
        try:
            from keybert import KeyBERT
            self._models["keybert"] = KeyBERT()
            print("   ✅ KeyBERT loaded")
        except Exception as e:
            print(f"   ⚠️ KeyBERT failed: {e}")
            self._models["keybert"] = None
        
        # 6. PYANNOTE for Speaker Diarization - FIXED VERSION
        print("\n🔹 6. Loading Pyannote Speaker Diarization...")
        try:
            from pyannote.audio import Pipeline
            import huggingface_hub
            
            # Check if already logged in
            try:
                # Try to load with default settings
                self._models["diarization"] = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=True
                )
                print("   ✅ Pyannote diarization loaded (with auth token)")
            except Exception as e:
                print(f"   ⚠️ First attempt failed: {e}")
                # Try without token as fallback
                self._models["diarization"] = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=False
                )
                print("   ✅ Pyannote diarization loaded (without auth token)")
                
        except Exception as e:
            print(f"   ⚠️ Pyannote failed: {e}")
            self._models["diarization"] = None
        
        print("\n" + "="*60)
        loaded_count = len([v for v in self._models.values() if v is not None])
        print(f"✅ LOADED {loaded_count}/6 MODELS")
        print("="*60)
        
        return self._models
    
    def get_model(self, model_name):
        """Get a specific model"""
        return self._models.get(model_name)
    
    def clear(self):
        """Clear models from memory"""
        self._models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Global functions for easy access
def load_models():
    """Load all models"""
    manager = ModelsManager()
    return manager.load_all()

def get_model(model_name):
    """Get specific model"""
    manager = ModelsManager()
    return manager.get_model(model_name)

def clear_models():
    """Clear models from memory"""
    manager = ModelsManager()
    manager.clear()