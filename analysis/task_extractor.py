# C:\Users\rasya\Desktop\NLP\AI_powered_summarizer\AI_powered_summarizer_final_project\analysis\task_extractor.py
from typing import List, Dict  # ADD THIS IMPORT
import re

def extract_tasks(text: str) -> List[str]:
    """Extract tasks/action items from text"""
    if not text:
        return []
    
    tasks = []
    sentences = [s.strip() for s in text.split('. ') if s.strip()]
    
    # Task patterns
    task_patterns = [
        r"(?:please|kindly|could you|can you)\s+(.+?)[.!?]",
        r"(?:need to|must|should)\s+(.+?)[.!?]",
        r"(?:todo|action item|task):\s*(.+?)[.!?]",
        r"(?:create|make|build|develop|send|submit|update|fix)\s+(.+?)[.!?]",
    ]
    
    for sentence in sentences:
        # Check patterns
        for pattern in task_patterns:
            matches = re.findall(pattern, sentence, re.IGNORECASE)
            tasks.extend(matches)
        
        # Additional heuristic: sentences with action verbs
        action_verbs = ["create", "make", "do", "send", "update", "complete", "fix"]
        if any(verb in sentence.lower() for verb in action_verbs):
            if sentence not in tasks:
                tasks.append(sentence)
    
    # Limit and clean tasks
    tasks = list(set(tasks))[:5]  # Remove duplicates, limit to 5
    return [t.strip() for t in tasks if t.strip()]

def categorize_tasks(tasks: List[str]) -> Dict[str, List[str]]:
    """Categorize tasks by type"""
    categories = {
        "requests": [],
        "requirements": [],
        "actions": [],
        "other": []
    }
    
    for task in tasks:
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["please", "kindly", "could you"]):
            categories["requests"].append(task)
        elif any(word in task_lower for word in ["need to", "must", "should"]):
            categories["requirements"].append(task)
        elif any(word in task_lower for word in ["create", "make", "do", "send"]):
            categories["actions"].append(task)
        else:
            categories["other"].append(task)
    
    return categories