"""
Text normalization and filtering for sentiment analysis.
"""

import re
from typing import List, Dict, Any, Optional
import logging


class Preprocessor:
    """Preprocess text data for sentiment analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def clean_commit_message(self, message: str) -> str:
        """Clean and normalize commit messages."""
        # Remove common git patterns
        message = re.sub(r'^Merge.*', '', message, flags=re.IGNORECASE)
        message = re.sub(r'^Revert.*', '', message, flags=re.IGNORECASE)
        
        # Remove issue references
        message = re.sub(r'#\d+', '', message)
        message = re.sub(r'fixes?\s+#\d+', '', message, flags=re.IGNORECASE)
        
        # Remove URLs
        message = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', message)
        
        # Clean up whitespace
        message = re.sub(r'\s+', ' ', message).strip()
        
        return message
    
    def filter_meaningful_commits(self, commits: List[Dict[str, Any]], 
                                min_length: int = 5) -> List[Dict[str, Any]]:
        """Filter out commits that are not meaningful for sentiment analysis."""
        meaningful = []
        
        for commit in commits:
            cleaned_message = self.clean_commit_message(commit['message'])
            
            # Skip if too short or empty
            if len(cleaned_message) < min_length:
                continue
                
            # Skip merge commits
            if cleaned_message.lower().startswith('merge'):
                continue
                
            # Skip revert commits
            if cleaned_message.lower().startswith('revert'):
                continue
                
            meaningful.append({
                **commit,
                'cleaned_message': cleaned_message
            })
        
        return meaningful
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction - could be enhanced with NLP
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out common words
        stop_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can'
        }
        
        keywords = [word for word in words if word not in stop_words]
        return keywords[:10]  # Return top 10 keywords
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?]', '', text)
        
        return text.strip()
    
    def preprocess_commits(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Complete preprocessing pipeline for commits."""
        # Clean messages
        for commit in commits:
            commit['cleaned_message'] = self.clean_commit_message(commit['message'])
            commit['normalized_message'] = self.normalize_text(commit['cleaned_message'])
            commit['keywords'] = self.extract_keywords(commit['cleaned_message'])
        
        # Filter meaningful commits
        meaningful_commits = self.filter_meaningful_commits(commits)
        
        self.logger.info(f"Preprocessed {len(meaningful_commits)} meaningful commits from {len(commits)} total")
        
        return meaningful_commits
