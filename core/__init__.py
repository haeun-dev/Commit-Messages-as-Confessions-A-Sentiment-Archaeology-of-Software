"""
Core module for codemood - the heart of all modules.
Contains common logic for sentiment analysis, git extraction, and visualization.
"""

__version__ = "0.1.0"
__author__ = "codemood team"

from .git_extractor import GitExtractor
from .sentiment_analyzer import SentimentAnalyzer
from .preprocessor import Preprocessor
from .visualizer import Visualizer
from .utils import setup_logger, format_timestamp

__all__ = [
    "GitExtractor",
    "SentimentAnalyzer", 
    "Preprocessor",
    "Visualizer",
    "setup_logger",
    "format_timestamp"
]
