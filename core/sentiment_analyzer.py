"""
Sentiment analysis using HuggingFace or OpenAI models.
"""

from typing import List, Dict, Any, Optional
import logging


class SentimentAnalyzer:
    """Analyze sentiment of code-related text."""
    
    def __init__(self, model_type: str = "huggingface", model_name: Optional[str] = None):
        self.model_type = model_type
        self.model_name = model_name or "cardiffnlp/twitter-roberta-base-sentiment-latest"
        self.model = None
        self.tokenizer = None
        self.logger = logging.getLogger(__name__)
        
    def load_model(self):
        """Load the sentiment analysis model."""
        try:
            if self.model_type == "huggingface":
                from transformers import pipeline
                self.model = pipeline("sentiment-analysis", 
                                    model=self.model_name,
                                    top_k=None)
                self.logger.info(f"Loaded HuggingFace model: {self.model_name}")
            elif self.model_type == "openai":
                # OpenAI implementation would go here
                self.logger.info("OpenAI model configuration ready")
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text."""
        if not self.model:
            self.load_model()
        
        try:
            if self.model_type == "huggingface":
                results = self.model(text)
                # Handle the new format where results is a list of lists
                if isinstance(results, list) and len(results) > 0:
                    if isinstance(results[0], list):
                        # Multiple results format
                        best_result = results[0][0]  # Get the first result from the first item
                    else:
                        # Single result format
                        best_result = results[0]
                    
                    # Map labels to our expected format
                    label_mapping = {
                        'LABEL_0': 'NEGATIVE',
                        'LABEL_1': 'NEUTRAL', 
                        'LABEL_2': 'POSITIVE',
                        'NEGATIVE': 'NEGATIVE',
                        'NEUTRAL': 'NEUTRAL',
                        'POSITIVE': 'POSITIVE'
                    }
                    
                    sentiment = label_mapping.get(best_result['label'], 'NEUTRAL')
                    
                    return {
                        'text': text,
                        'sentiment': sentiment,
                        'confidence': best_result['score'],
                        'all_scores': results
                    }
                else:
                    return {
                        'text': text,
                        'sentiment': 'NEUTRAL',
                        'confidence': 0.5,
                        'all_scores': []
                    }
            else:
                # Placeholder for other model types
                return {
                    'text': text,
                    'sentiment': 'NEUTRAL',
                    'confidence': 0.5,
                    'all_scores': []
                }
        except Exception as e:
            self.logger.error(f"Error analyzing text: {e}")
            return {
                'text': text,
                'sentiment': 'ERROR',
                'confidence': 0.0,
                'all_scores': []
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze sentiment of multiple texts."""
        return [self.analyze_text(text) for text in texts]
    
    def analyze_commit_messages(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment of commit messages."""
        messages = [commit['message'] for commit in commits]
        sentiments = self.analyze_batch(messages)
        
        # Combine with commit metadata
        for i, commit in enumerate(commits):
            commit['sentiment'] = sentiments[i]
        
        return commits
