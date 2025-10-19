"""
Sentiment analysis using HuggingFace or OpenAI models.
"""

from typing import List, Dict, Any, Optional
import logging
import os
import warnings


class SentimentAnalyzer:
    """Analyze sentiment of code-related text."""
    
    def __init__(self, model_type: str = "huggingface", model_name: Optional[str] = None, 
                 api_key: Optional[str] = None, organization: Optional[str] = None):
        self.model_type = model_type
        self.model_name = model_name or self._get_default_model_name()
        self.api_key = api_key or self._get_api_key()
        self.organization = organization
        self.model = None
        self.tokenizer = None
        self.logger = logging.getLogger(__name__)
        self._cost_tracker = {"tokens_used": 0, "cost": 0.0}
    
    def _get_default_model_name(self) -> str:
        """Get default model name based on model type."""
        if self.model_type == "huggingface":
            # Alternative models that don't show the warning:
            # "distilbert-base-uncased-finetuned-sst-2-english" - smaller, faster
            # "nlptown/bert-base-multilingual-uncased-sentiment" - multilingual
            return "cardiffnlp/twitter-roberta-base-sentiment-latest"
        elif self.model_type == "openai":
            return "gpt-3.5-turbo"
        else:
            return "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment variables."""
        if self.model_type == "openai":
            return os.getenv("OPENAI_API_KEY")
        return None
    
    def _validate_api_key(self) -> bool:
        """Validate that API key is available for paid models."""
        if self.model_type == "openai" and not self.api_key:
            self.logger.error("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
            return False
        return True
        
    def load_model(self):
        """Load the sentiment analysis model."""
        try:
            if self.model_type == "huggingface":
                from transformers import pipeline
                
                # Suppress the expected warning about unused weights
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message="Some weights of the model checkpoint.*were not used")
                    self.model = pipeline("sentiment-analysis", 
                                        model=self.model_name,
                                        top_k=None)
                self.logger.info(f"Loaded HuggingFace model: {self.model_name}")
            elif self.model_type == "openai":
                if not self._validate_api_key():
                    raise ValueError("OpenAI API key is required")
                try:
                    import openai
                    self.model = openai.OpenAI(api_key=self.api_key, organization=self.organization)
                    self.logger.info(f"OpenAI client initialized with model: {self.model_name}")
                except ImportError:
                    raise ImportError("OpenAI package is required. Install with: pip install openai")
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
            elif self.model_type == "openai":
                return self._analyze_with_openai(text)
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
    
    def _analyze_with_openai(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI API."""
        try:
            # Truncate text if too long (OpenAI has token limits)
            max_length = 1000
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            prompt = f"""Analyze the sentiment of this commit message and return ONLY a JSON response with the following format:
{{
    "sentiment": "POSITIVE", "NEGATIVE", or "NEUTRAL",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Commit message: {text}"""

            response = self.model.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis expert. Analyze commit messages for emotional tone."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            # Track usage and cost
            usage = response.usage
            if usage:
                self._cost_tracker["tokens_used"] += usage.total_tokens
                # Approximate cost calculation (varies by model)
                cost_per_1k_tokens = 0.0015 if "gpt-3.5" in self.model_name else 0.03
                self._cost_tracker["cost"] += (usage.total_tokens / 1000) * cost_per_1k_tokens
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            import json
            try:
                # Remove any markdown formatting
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                result = json.loads(content)
                sentiment = result.get("sentiment", "NEUTRAL").upper()
                confidence = float(result.get("confidence", 0.5))
                
                return {
                    'text': text,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'all_scores': [{"label": sentiment, "score": confidence}],
                    'reasoning': result.get("reasoning", "")
                }
            except json.JSONDecodeError:
                # Fallback parsing if JSON parsing fails
                sentiment = "NEUTRAL"
                confidence = 0.5
                if any(word in content.lower() for word in ["positive", "good", "great", "excellent"]):
                    sentiment = "POSITIVE"
                    confidence = 0.7
                elif any(word in content.lower() for word in ["negative", "bad", "terrible", "awful"]):
                    sentiment = "NEGATIVE"
                    confidence = 0.7
                
                return {
                    'text': text,
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'all_scores': [{"label": sentiment, "score": confidence}],
                    'reasoning': content
                }
                
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return {
                'text': text,
                'sentiment': 'ERROR',
                'confidence': 0.0,
                'all_scores': [],
                'reasoning': f"API Error: {str(e)}"
            }
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get current cost tracking information."""
        return {
            "tokens_used": self._cost_tracker["tokens_used"],
            "estimated_cost": self._cost_tracker["cost"],
            "model_type": self.model_type,
            "model_name": self.model_name
        }
    
    def reset_cost_tracker(self):
        """Reset cost tracking."""
        self._cost_tracker = {"tokens_used": 0, "cost": 0.0}
