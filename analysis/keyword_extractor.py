"""
Keyword Extraction using KeyBERT and Transformer models - Enhanced Version
"""

from typing import List, Tuple
from models_manager import get_model
import re

def extract_keyphrases(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Extract keyphrases using KeyBERT with enhanced filtering
    """
    # Clean text before extraction
    text = clean_text_for_keywords(text)
    
    keybert_model = get_model("keybert")
    
    if keybert_model is None:
        return extract_keywords_fallback(text, top_n)
    
    try:
        # Extract keywords with KeyBERT
        keywords = keybert_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 2),  # Unigrams and bigrams
            stop_words='english',
            top_n=top_n * 2,  # Extract more, then filter
            diversity=0.5
        )
        
        # Post-process and filter keywords
        processed_keywords = post_process_keywords(keywords, top_n)
        
        return processed_keywords
        
    except Exception as e:
        print(f"KeyBERT extraction failed: {e}")
        return extract_keywords_fallback(text, top_n)


def clean_text_for_keywords(text: str) -> str:
    """
    Clean text specifically for keyword extraction
    """
    # Remove speaker labels (e.g., "Emily:", "Doctor:")
    text = re.sub(r'\b\w+:\s*', '', text)
    
    # Remove common filler words at start of sentences
    text = re.sub(r'^(So|Well|Like|Um|Uh|Actually|Basically)\s+', '', text, flags=re.IGNORECASE)
    
    # Remove excessive punctuation
    text = re.sub(r'[!?.]{2,}', '.', text)
    
    return text.strip()


def post_process_keywords(keywords: List[Tuple[str, float]], top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Filter and clean extracted keywords
    """
    filtered_keywords = []
    
    # Common meaningless words to filter
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'so', 'for', 'nor', 'yet',
        'to', 'of', 'in', 'on', 'at', 'by', 'with', 'without', 'about',
        'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
        'this', 'that', 'these', 'those', 'it', 'they', 'we', 'you', 'he', 'she'
    }
    
    for keyword, score in keywords:
        # Skip if too short
        if len(keyword) < 3:
            continue
        
        # Skip if only numbers
        if keyword.isdigit():
            continue
        
        # Skip if all stopwords
        words = keyword.lower().split()
        if all(word in stop_words for word in words):
            continue
        
        # Clean the keyword
        cleaned = clean_keyword(keyword)
        
        if cleaned and cleaned not in [k for k, _ in filtered_keywords]:
            # Boost score for meaningful bigrams
            if len(words) == 2 and score < 0.5:
                score = min(score * 1.2, 0.99)
            
            filtered_keywords.append((cleaned, score))
    
    # Sort by score and take top_n
    filtered_keywords.sort(key=lambda x: x[1], reverse=True)
    
    return filtered_keywords[:top_n]


def clean_keyword(keyword: str) -> str:
    """
    Clean individual keyword
    """
    # Convert to lowercase
    keyword = keyword.lower()
    
    # Remove extra spaces
    keyword = ' '.join(keyword.split())
    
    # Remove trailing punctuation
    keyword = re.sub(r'[.,!?;:]$', '', keyword)
    
    # Remove common prefixes
    keyword = re.sub(r'^(a|an|the)\s+', '', keyword)
    
    return keyword.strip()


def extract_keywords_fallback(text: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    Enhanced fallback keyword extraction using TF-IDF
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from collections import Counter
    
    # Clean text
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    
    # Remove common stopwords
    stopwords = set(['the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 
                     'on', 'that', 'with', 'by', 'at', 'from', 'as', 'are',
                     'was', 'were', 'be', 'this', 'that', 'these', 'those'])
    
    # Split into sentences
    sentences = [s.strip() for s in clean_text.split('.') if len(s.strip()) > 10]
    
    if not sentences:
        # Last resort: word frequency
        words = clean_text.split()
        word_freq = Counter(words)
        
        filtered_words = [(word, freq) for word, freq in word_freq.items() 
                         if word not in stopwords and len(word) > 3]
        
        filtered_words.sort(key=lambda x: x[1], reverse=True)
        return [(word, freq/len(words)) for word, freq in filtered_words[:top_n]]
    
    # Create TF-IDF matrix
    vectorizer = TfidfVectorizer(
        max_features=top_n * 3,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1
    )
    
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        # Get feature names and scores
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.sum(axis=0).A1
        
        # Create (keyword, score) pairs
        keywords = list(zip(feature_names, scores))
        
        # Filter and clean
        filtered = []
        for kw, score in keywords:
            if len(kw) > 3 and kw not in stopwords:
                # Boost bigrams slightly
                if ' ' in kw:
                    score = score * 1.1
                filtered.append((kw, score))
        
        # Sort by score
        filtered.sort(key=lambda x: x[1], reverse=True)
        
        return filtered[:top_n]
        
    except Exception as e:
        print(f"TF-IDF extraction failed: {e}")
        return []


def extract_keywords_with_categories(text: str, top_n: int = 10) -> Dict[str, List[Tuple[str, float]]]:
    """
    Extract and categorize keywords by type
    """
    keywords = extract_keyphrases(text, top_n * 2)
    
    categories = {
        "people": [],
        "places": [],
        "actions": [],
        "topics": [],
        "other": []
    }
    
    # Simple categorization based on word patterns
    people_indicators = ['mother', 'father', 'brother', 'sister', 'doctor', 'teacher', 'friend']
    places_indicators = ['house', 'school', 'hospital', 'office', 'restaurant', 'store']
    action_indicators = ['go', 'come', 'take', 'make', 'do', 'get', 'have', 'eat', 'drink']
    
    for keyword, score in keywords:
        keyword_lower = keyword.lower()
        
        if any(ind in keyword_lower for ind in people_indicators):
            categories["people"].append((keyword, score))
        elif any(ind in keyword_lower for ind in places_indicators):
            categories["places"].append((keyword, score))
        elif any(ind in keyword_lower for ind in action_indicators):
            categories["actions"].append((keyword, score))
        elif len(keyword.split()) >= 2:
            categories["topics"].append((keyword, score))
        else:
            categories["other"].append((keyword, score))
    
    # Limit each category
    for cat in categories:
        categories[cat] = categories[cat][:top_n//2]
    
    return categories