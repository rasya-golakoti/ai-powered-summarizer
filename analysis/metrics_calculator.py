# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\analysis\metrics_calculator.py
"""
Metrics Calculator - ROUGE-L, BLEU, BERT-F1
"""

from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from sentence_transformers import util
import numpy as np

def calculate_rouge(reference: str, candidate: str) -> dict:
    """
    Calculate ROUGE scores
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        Dictionary with ROUGE scores
    """
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, candidate)
    
    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rouge_l': scores['rougeL'].fmeasure
    }

def calculate_bleu(reference: str, candidate: str) -> float:
    """
    Calculate BLEU score
    
    Args:
        reference: Reference text
        candidate: Candidate text
        
    Returns:
        BLEU score
    """
    # Tokenize
    ref_tokens = reference.split()
    cand_tokens = candidate.split()
    
    # Calculate BLEU
    smoothing = SmoothingFunction().method1
    score = sentence_bleu([ref_tokens], cand_tokens, smoothing_function=smoothing)
    
    return score

def calculate_bert_f1(reference: str, candidate: str, model) -> float:
    """
    Calculate BERT-F1 score using sentence embeddings
    
    Args:
        reference: Reference text
        candidate: Candidate text
        model: Sentence transformer model
        
    Returns:
        BERT-F1 score
    """
    if model is None:
        return 0.0
    
    # Encode sentences
    ref_embedding = model.encode(reference, convert_to_tensor=True)
    cand_embedding = model.encode(candidate, convert_to_tensor=True)
    
    # Calculate cosine similarity
    cosine_score = util.pytorch_cos_sim(ref_embedding, cand_embedding).item()
    
    # Convert to F1-like score (0-1)
    bert_f1 = max(0, cosine_score)
    
    return bert_f1

def calculate_all_metrics(original_text: str, summary_text: str, reference_summary: str = "") -> dict:
    """
    Calculate all metrics: ROUGE-L, BLEU, BERT-F1
    
    Args:
        original_text: Original transcript text
        summary_text: Generated summary
        reference_summary: Reference summary (if available)
        
    Returns:
        Dictionary with all metrics
    """
    from models_manager import get_model
    
    metrics = {}
    
    # Use extractive summary as reference if no reference provided
    reference = reference_summary if reference_summary else original_text[:500]  # First 500 chars as reference
    
    # Calculate ROUGE
    try:
        rouge_scores = calculate_rouge(reference, summary_text)
        metrics.update(rouge_scores)
    except Exception as e:
        print(f"ROUGE calculation failed: {e}")
        metrics.update({'rouge1': 0, 'rouge2': 0, 'rouge_l': 0})
    
    # Calculate BLEU
    try:
        bleu_score = calculate_bleu(reference, summary_text)
        metrics['bleu'] = bleu_score
    except Exception as e:
        print(f"BLEU calculation failed: {e}")
        metrics['bleu'] = 0
    
    # Calculate BERT-F1
    try:
        model = get_model("sentence_transformer")
        bert_f1 = calculate_bert_f1(reference, summary_text, model)
        metrics['bert_f1'] = bert_f1
    except Exception as e:
        print(f"BERT-F1 calculation failed: {e}")
        metrics['bert_f1'] = 0
    
    # Calculate compression ratio
    original_words = len(original_text.split())
    summary_words = len(summary_text.split())
    if original_words > 0:
        metrics['compression_ratio'] = summary_words / original_words
    else:
        metrics['compression_ratio'] = 0
    
    return metrics