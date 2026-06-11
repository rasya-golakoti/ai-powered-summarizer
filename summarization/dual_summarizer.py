"""
Dual Summarizer with Perfect Compression Control
"""

from typing import Dict
from models_manager import get_model
from config import MAX_CHAPTERS

# ============================================
# COMPRESSION PRESETS (Based on your test results)
# ============================================
# Your test showed: 183 words → 35 words (81% compression)
# This is the STANDARD level - OPTIMAL for most cases
# ============================================

COMPRESSION_PRESETS = {
    "brief": {      # 90% compression - Ultra concise
        "max_len": 60,
        "min_len": 15,
        "length_penalty": 3.0,
        "num_sentences": 2,
        "description": "Very short - key points only"
    },
    "standard": {   # 80% compression - YOUR CURRENT (BEST)
        "max_len": 150,
        "min_len": 30,
        "length_penalty": 2.0,
        "num_sentences": 4,
        "description": "Balanced - optimal for most content"
    },
    "detailed": {   # 65% compression - More detail
        "max_len": 250,
        "min_len": 60,
        "length_penalty": 1.0,
        "num_sentences": 6,
        "description": "Detailed - preserves more information"
    }
}

# Set current compression level (change this one value to control everything)
CURRENT_COMPRESSION = "standard"  # Options: "brief", "standard", "detailed"


# ============================================
# TEXT CLEANING FUNCTIONS
# ============================================

def smooth_conversation_text(text: str) -> str:
    """
    Convert choppy conversation into flowing text by combining
    speaker turns that are closely related
    """
    import re
    
    # Remove speaker labels like "Emily:", "William:"
    speaker_pattern = r'(\w+):\s*'
    
    # Split into lines and clean
    lines = text.split('\n')
    smoothed = []
    buffer = ""
    
    for line in lines:
        clean_line = re.sub(speaker_pattern, '', line)
        if len(clean_line.split()) < 10 and buffer:
            buffer += " " + clean_line
        else:
            if buffer:
                smoothed.append(buffer)
            buffer = clean_line
    
    if buffer:
        smoothed.append(buffer)
    
    return ". ".join(smoothed)


def clean_text_for_summarization(text: str) -> str:
    """
    Clean and prepare text for better summarization
    Removes fragments and excessive punctuation
    """
    import re
    
    # Remove excessive punctuation
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    
    # Remove repeated words (common in hesitation)
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
    
    return text.strip()


# ============================================
# SUMMARIZATION FUNCTIONS
# ============================================

def dual_summarization(text: str) -> Dict[str, str]:
    """Perform both abstractive and extractive summarization"""
    if not text or len(text.split()) < 20:
        return {
            "abstractive": text[:200] if text else "",
            "extractive": text[:200] if text else ""
        }
    
    return {
        "abstractive": abstractive_summary(text),
        "extractive": extractive_summary(text)
    }


def abstractive_summary(text: str) -> str:
    """Generate abstractive summary using BART with perfect compression control"""
    
    # Step 1: Clean the text
    text = smooth_conversation_text(text)
    text = clean_text_for_summarization(text)
    
    bart_model = get_model("bart_model")
    bart_tokenizer = get_model("bart_tokenizer")
    
    if not bart_model or not bart_tokenizer or len(text) < 100:
        print("   ⚠️ BART model/tokenizer not available, using extractive only")
        return extractive_summary(text)
    
    try:
        # Get compression settings from preset
        preset = COMPRESSION_PRESETS[CURRENT_COMPRESSION]
        max_len = preset["max_len"]
        min_len = preset["min_len"]
        length_penalty = preset["length_penalty"]
        
        word_count = len(text.split())
        
        # Apply dynamic adjustment based on actual text length
        if word_count < 100:
            max_len = min(max_len, 50)
            min_len = min(min_len, 15)
        
        print(f"   📝 Compression Mode: {CURRENT_COMPRESSION.upper()}")
        print(f"   📝 Text: {word_count} words → Target: {min_len}-{max_len} words")
        
        # Summarize in chunks if too long
        if len(text) > 2000:
            print("   🔄 Text too long, summarizing in chunks...")
            chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
            summaries = []
            for chunk in chunks[:3]:
                inputs = bart_tokenizer(chunk, max_length=1024, truncation=True, return_tensors="pt")
                summary_ids = bart_model.generate(
                    inputs["input_ids"],
                    max_length=max_len//3,
                    min_length=min_len//3,
                    length_penalty=length_penalty,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3  # Prevents repetition
                )
                summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                summaries.append(summary)
            final_summary = " ".join(summaries)
        else:
            # Single summary with perfect compression
            inputs = bart_tokenizer(text, max_length=1024, truncation=True, return_tensors="pt")
            summary_ids = bart_model.generate(
                inputs["input_ids"],
                max_length=max_len,
                min_length=min_len,
                length_penalty=length_penalty,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=3  # Prevents repetition
            )
            final_summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        # Post-process summary
        final_summary = final_summary.strip()
        if final_summary and final_summary[0].islower():
            final_summary = final_summary[0].upper() + final_summary[1:]
        if final_summary and final_summary[-1] not in '.!?':
            final_summary += '.'
        
        # Calculate actual compression achieved
        actual_words = len(final_summary.split())
        compression_rate = (1 - actual_words / word_count) * 100 if word_count > 0 else 0
        print(f"   ✅ Achieved: {actual_words} words ({compression_rate:.0f}% compression)")
        
        return final_summary
            
    except Exception as e:
        print(f"   ⚠️ Abstractive summary failed: {e}")
        return extractive_summary(text)


def extractive_summary(text: str, num_sentences: int = None) -> str:
    """Generate extractive summary with perfect compression control"""
    
    # Clean text first
    text = smooth_conversation_text(text)
    text = clean_text_for_summarization(text)
    
    # Use preset if num_sentences not specified
    if num_sentences is None:
        num_sentences = COMPRESSION_PRESETS[CURRENT_COMPRESSION]["num_sentences"]
    
    def split_into_sentences(text: str) -> list:
        """Improved sentence splitting"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    sentences = split_into_sentences(text)
    if not sentences:
        return ""
    
    if len(sentences) <= num_sentences:
        return ". ".join(sentences) + "."
    
    # Score sentences based on importance heuristics
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        
        # Position: first and last sentences are important
        if i == 0 or i == len(sentences) - 1:
            score += 2
        
        # Length: medium-length sentences are often more informative
        word_count = len(sentence.split())
        if 8 <= word_count <= 25:
            score += 1
        
        # Keywords: sentences with important words
        important_words = ["important", "key", "summary", "conclusion", "result", "find", "main", "point"]
        if any(word in sentence.lower() for word in important_words):
            score += 2
        
        # Question sentences are usually less important in summaries
        if "?" in sentence:
            score -= 1
        
        # Sentences with numbers/dates might be important
        if any(c.isdigit() for c in sentence):
            score += 1
        
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s[1] for s in scored_sentences[:num_sentences]]
    
    # Preserve chronological order
    top_sentences.sort(key=lambda x: sentences.index(x))
    
    summary = ". ".join(top_sentences)
    if not summary.endswith('.'):
        summary += '.'
    
    return summary


# ============================================
# HELPER FUNCTIONS
# ============================================

def set_compression_level(level: str):
    """
    Change compression level dynamically
    
    Args:
        level: "brief", "standard", or "detailed"
    """
    global CURRENT_COMPRESSION
    if level in COMPRESSION_PRESETS:
        CURRENT_COMPRESSION = level
        print(f"✅ Compression level set to: {level.upper()} - {COMPRESSION_PRESETS[level]['description']}")
    else:
        print(f"❌ Invalid level. Choose from: {list(COMPRESSION_PRESETS.keys())}")


def get_compression_info() -> Dict:
    """Get current compression settings"""
    preset = COMPRESSION_PRESETS[CURRENT_COMPRESSION]
    return {
        "current_level": CURRENT_COMPRESSION,
        "max_length": preset["max_len"],
        "min_length": preset["min_len"],
        "length_penalty": preset["length_penalty"],
        "num_sentences": preset["num_sentences"],
        "description": preset["description"]
    }


def test_compression_levels(text: str):
    """Test all compression levels on the same text"""
    global CURRENT_COMPRESSION
    
    print("\n" + "="*60)
    print("📊 COMPRESSION LEVEL COMPARISON")
    print("="*60)
    print(f"Original text: {len(text.split())} words\n")
    
    for level in ["brief", "standard", "detailed"]:
        CURRENT_COMPRESSION = level
        preset = COMPRESSION_PRESETS[level]
        summary = abstractive_summary(text)
        words = len(summary.split())
        compression = (1 - words / len(text.split())) * 100
        print(f"\n{level.upper()} ({preset['description']}):")
        print(f"   Words: {words} ({compression:.0f}% compression)")
        print(f"   Summary: {summary[:150]}...")
    
    # Reset to standard
    CURRENT_COMPRESSION = "standard"
    print("\n" + "="*60)


# ============================================
# ALIAS FUNCTIONS FOR MAIN.PY COMPATIBILITY
# ============================================

def generate_abstractive_summary(text: str) -> str:
    """Alias for abstractive_summary"""
    return abstractive_summary(text)


def generate_extractive_summary(text: str) -> str:
    """Alias for extractive_summary"""
    return extractive_summary(text)


# Test if run directly
if __name__ == "__main__":
    test_text = """
    Artificial intelligence is transforming many industries. 
    Machine learning algorithms can now recognize patterns in data that humans cannot see.
    Natural language processing allows computers to understand and generate human language.
    These technologies are creating new opportunities for automation and innovation.
    However, they also raise important ethical questions about privacy and job displacement.
    """
    
    print("🧪 Testing compression control...")
    print(f"Original: {len(test_text.split())} words")
    
    print("\n📊 Current compression info:")
    print(get_compression_info())
    
    print("\n📝 Standard compression summary:")
    print(abstractive_summary(test_text))
    
    print("\n🔄 Changing to brief compression...")
    set_compression_level("brief")
    print(abstractive_summary(test_text))
    
    print("\n🔄 Changing back to standard...")
    set_compression_level("standard")