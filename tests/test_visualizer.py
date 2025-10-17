"""
Tests for visualizer module functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from core.visualizer import Visualizer


class TestVisualizer(unittest.TestCase):
    """Test Visualizer functionality."""
    
    def setUp(self):
        self.visualizer = Visualizer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_sentiment_timeline_success(self, mock_show, mock_savefig):
        """Test successful sentiment timeline creation."""
        commits = [
            {
                'date': '2024-01-15T10:30:00Z',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            },
            {
                'date': '2024-01-16T10:30:00Z',
                'sentiment': {'sentiment': 'NEGATIVE', 'confidence': 0.7}
            },
            {
                'date': '2024-01-17T10:30:00Z',
                'sentiment': {'sentiment': 'NEUTRAL', 'confidence': 0.6}
            }
        ]
        
        output_path = os.path.join(self.temp_dir, 'timeline.png')
        
        # Should not raise an exception
        self.visualizer.create_sentiment_timeline(commits, output_path)
        
        mock_savefig.assert_called_once_with(output_path, dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_sentiment_timeline_no_commits(self, mock_savefig):
        """Test sentiment timeline with no commits."""
        commits = []
        
        # Should not raise an exception
        self.visualizer.create_sentiment_timeline(commits)
        
        # Should not call savefig for empty commits
        mock_savefig.assert_not_called()
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_sentiment_timeline_invalid_dates(self, mock_savefig):
        """Test sentiment timeline with invalid dates."""
        commits = [
            {
                'date': 'invalid-date',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            }
        ]
        
        # Should not raise an exception
        self.visualizer.create_sentiment_timeline(commits)
        
        # Should not call savefig for invalid dates
        mock_savefig.assert_not_called()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_sentiment_distribution_success(self, mock_show, mock_savefig):
        """Test successful sentiment distribution creation."""
        commits = [
            {'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}},
            {'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.7}},
            {'sentiment': {'sentiment': 'NEGATIVE', 'confidence': 0.6}},
            {'sentiment': {'sentiment': 'NEUTRAL', 'confidence': 0.5}}
        ]
        
        output_path = os.path.join(self.temp_dir, 'distribution.png')
        
        # Should not raise an exception
        self.visualizer.create_sentiment_distribution(commits, output_path)
        
        mock_savefig.assert_called_once_with(output_path, dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_sentiment_distribution_no_commits(self, mock_savefig):
        """Test sentiment distribution with no commits."""
        commits = []
        
        # Should not raise an exception
        self.visualizer.create_sentiment_distribution(commits)
        
        # Should not call savefig for empty commits
        mock_savefig.assert_not_called()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_word_cloud_success(self, mock_show, mock_savefig):
        """Test successful word cloud creation."""
        commits = [
            {'keywords': ['fix', 'bug', 'authentication']},
            {'keywords': ['add', 'feature', 'login']},
            {'keywords': ['update', 'documentation']}
        ]
        
        output_path = os.path.join(self.temp_dir, 'wordcloud.png')
        
        # Should not raise an exception
        self.visualizer.create_word_cloud(commits, output_path)
        
        mock_savefig.assert_called_once_with(output_path, dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_word_cloud_no_keywords(self, mock_savefig):
        """Test word cloud with no keywords."""
        commits = [
            {'keywords': []},
            {'keywords': []}
        ]
        
        # Should not raise an exception
        self.visualizer.create_word_cloud(commits)
        
        # Should not call savefig for no keywords
        mock_savefig.assert_not_called()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_author_sentiment_heatmap_success(self, mock_show, mock_savefig):
        """Test successful author sentiment heatmap creation."""
        commits = [
            {
                'author': 'John Doe',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            },
            {
                'author': 'John Doe',
                'sentiment': {'sentiment': 'NEGATIVE', 'confidence': 0.7}
            },
            {
                'author': 'Jane Smith',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.9}
            }
        ]
        
        output_path = os.path.join(self.temp_dir, 'heatmap.png')
        
        # Should not raise an exception
        self.visualizer.create_author_sentiment_heatmap(commits, output_path)
        
        mock_savefig.assert_called_once_with(output_path, dpi=300, bbox_inches='tight')
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_author_sentiment_heatmap_no_commits(self, mock_savefig):
        """Test author sentiment heatmap with no commits."""
        commits = []
        
        # Should not raise an exception
        self.visualizer.create_author_sentiment_heatmap(commits)
        
        # Should not call savefig for empty commits
        mock_savefig.assert_not_called()
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_author_sentiment_heatmap_no_sentiment_data(self, mock_savefig):
        """Test author sentiment heatmap with no sentiment data."""
        commits = [
            {'author': 'John Doe'},  # No sentiment data
            {'author': 'Jane Smith'}  # No sentiment data
        ]
        
        # Should not raise an exception
        self.visualizer.create_author_sentiment_heatmap(commits)
        
        # Should not call savefig for no sentiment data
        mock_savefig.assert_not_called()
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization."""
        visualizer = Visualizer("seaborn-v0_8")
        self.assertEqual(visualizer.style, "seaborn-v0_8")
        
        # Test default initialization
        visualizer_default = Visualizer()
        self.assertEqual(visualizer_default.style, "seaborn-v0_8")
    
    @patch('matplotlib.pyplot.savefig')
    def test_visualization_with_show_only(self, mock_savefig):
        """Test visualization methods with show only (no save)."""
        commits = [
            {
                'date': '2024-01-15T10:30:00Z',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            }
        ]
        
        # Test timeline without output path
        self.visualizer.create_sentiment_timeline(commits)
        mock_savefig.assert_not_called()
        
        # Test distribution without output path
        self.visualizer.create_sentiment_distribution(commits)
        mock_savefig.assert_not_called()
        
        # Test word cloud without output path
        commits_with_keywords = [{'keywords': ['test', 'example']}]
        self.visualizer.create_word_cloud(commits_with_keywords)
        mock_savefig.assert_not_called()
        
        # Test heatmap without output path
        self.visualizer.create_author_sentiment_heatmap(commits)
        mock_savefig.assert_not_called()


if __name__ == '__main__':
    unittest.main()
