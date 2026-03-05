# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\summarization\dual_summarizer.py
from typing import Dict
from models_manager import get_model
from config import MAX_CHAPTERS

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
    """Generate abstractive summary using BART"""
    # FIXED: Use correct model keys
    bart_model = get_model("bart_model")
    bart_tokenizer = get_model("bart_tokenizer")
    
    if not bart_model or not bart_tokenizer or len(text) < 100:
        print("   ⚠️ BART model/tokenizer not available, using extractive only")
        return extractive_summary(text)
    
    try:
        # Calculate appropriate lengths
        word_count = len(text.split())
        max_len = min(150, max(50, word_count // 3))
        min_len = min(30, max(10, word_count // 10))
        
        print(f"   📝 Text: {word_count} words, Target: {min_len}-{max_len} words")
        
        # Summarize in chunks if too long
        if len(text) > 2000:
            print("   🔄 Text too long, summarizing in chunks...")
            chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
            summaries = []
            for chunk in chunks[:3]:  # First 3 chunks only
                inputs = bart_tokenizer(chunk, max_length=1024, truncation=True, return_tensors="pt")
                summary_ids = bart_model.generate(
                    inputs["input_ids"],
                    max_length=max_len//3,
                    min_length=min_len//3,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
                summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                summaries.append(summary)
            return " ".join(summaries)
        else:
            # Single summary
            inputs = bart_tokenizer(text, max_length=1024, truncation=True, return_tensors="pt")
            summary_ids = bart_model.generate(
                inputs["input_ids"],
                max_length=max_len,
                min_length=min_len,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary.strip()
            
    except Exception as e:
        print(f"   ⚠️ Abstractive summary failed: {e}")
        return extractive_summary(text)  # Fallback to extractive

def extractive_summary(text: str, num_sentences: int = 4) -> str:
    """Generate extractive summary by selecting important sentences"""
    
    # Local function to avoid import issues
    def split_into_sentences(text: str) -> list:
        """Simple sentence splitting"""
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
    
    # Try to maintain some chronological order
    top_sentences.sort(key=lambda x: sentences.index(x))
    
    return ". ".join(top_sentences) + "."

def test_summarization() -> None:
    """Test function to verify summarization works"""
    test_text = """
    Artificial intelligence is transforming many industries. 
    Machine learning algorithms can now recognize patterns in data that humans cannot see.
    Natural language processing allows computers to understand and generate human language.
    These technologies are creating new opportunities for automation and innovation.
    However, they also raise important ethical questions about privacy and job displacement.
    """
    
    print("🧪 Testing summarization...")
    print(f"Original text: {len(test_text.split())} words")
    
    abstractive = abstractive_summary(test_text)
    extractive = extractive_summary(test_text)
    
    print(f"✅ Abstractive summary: {len(abstractive.split())} words")
    print(f"   {abstractive}")
    print(f"✅ Extractive summary: {len(extractive.split())} words")
    print(f"   {extractive}")

# ============================================
# ALIAS FUNCTIONS FOR MAIN.PY COMPATIBILITY
# ============================================

def generate_abstractive_summary(text: str) -> str:
    """Alias for abstractive_summary (for main.py compatibility)"""
    return abstractive_summary(text)

def generate_extractive_summary(text: str) -> str:
    """Alias for extractive_summary (for main.py compatibility)"""
    return extractive_summary(text)

# Test if run directly
if __name__ == "__main__":
    test_summarization()