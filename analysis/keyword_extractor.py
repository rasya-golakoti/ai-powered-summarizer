# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\analysis\keyword_extractor.py
"""
Keyword Extraction using KeyBERT and Transformer models
"""

from typing import List, Tuple
from models_manager import get_model

def extract_keyphrases(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Extract keyphrases using KeyBERT
    
    Args:
        text: Input text
        top_n: Number of keyphrases to extract
        
    Returns:
        List of (keyphrase, score) tuples
    """
    keybert_model = get_model("keybert")
    
    if keybert_model is None:
        # Fallback: simple TF-IDF based extraction
        return extract_keywords_fallback(text, top_n)
    
    try:
        # Extract keywords with KeyBERT
        keywords = keybert_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english',
            top_n=top_n,
            diversity=0.5
        )
        
        return keywords
        
    except Exception as e:
        print(f"KeyBERT extraction failed: {e}")
        return extract_keywords_fallback(text, top_n)

def extract_keywords_fallback(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Fallback keyword extraction using TF-IDF
    
    Args:
        text: Input text
        top_n: Number of keywords
        
    Returns:
        List of (keyword, score) tuples
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    import re
    
    # Clean text
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Split into sentences
    sentences = [s.strip() for s in clean_text.split('.') if len(s.strip()) > 10]
    
    if not sentences:
        return []
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(
        max_features=top_n * 2,
        stop_words='english',
        ngram_range=(1, 2)
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Get feature names and scores
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        # Create (keyword, score) pairs
        keywords = list(zip(feature_names, scores))
        
        # Sort by score
        keywords.sort(key=lambda x: x[1], reverse=True)
        
        return keywords[:top_n]
        
    except Exception as e:
        print(f"TF-IDF extraction failed: {e}")
        
        # Last resort: simple word frequency
        words = clean_text.split()
        from collections import Counter
        word_freq = Counter(words)
        
        # Remove stopwords
        stopwords = set(['the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'on', 'that', 'with', 'by'])
        filtered_words = [(word, freq) for word, freq in word_freq.items() 
                         if word not in stopwords and len(word) > 3]
        
        filtered_words.sort(key=lambda x: x[1], reverse=True)
        return [(word, freq/len(words)) for word, freq in filtered_words[:top_n]]