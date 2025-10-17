"""
Tests for core module functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from core.git_extractor import GitExtractor
from core.sentiment_analyzer import SentimentAnalyzer
from core.preprocessor import Preprocessor
from core.visualizer import Visualizer
from core.utils import setup_logger, format_timestamp, ensure_directory


class TestGitExtractor(unittest.TestCase):
    """Test GitExtractor functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.git_extractor = GitExtractor(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.run')
    def test_get_commit_messages_success(self, mock_run):
        """Test successful commit message extraction."""
        mock_result = Mock()
        mock_result.stdout = "abc123|John Doe|john@example.com|2024-01-15T10:30:00Z|Fix bug in authentication\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        commits = self.git_extractor.get_commit_messages(10)
        
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]['hash'], 'abc123')
        self.assertEqual(commits[0]['author'], 'John Doe')
        self.assertEqual(commits[0]['message'], 'Fix bug in authentication')
    
    @patch('subprocess.run')
    def test_get_commit_messages_failure(self, mock_run):
        """Test commit message extraction failure."""
        mock_run.side_effect = Exception("Git command failed")
        
        commits = self.git_extractor.get_commit_messages(10)
        
        self.assertEqual(len(commits), 0)
    
    @patch('subprocess.run')
    def test_get_file_changes(self, mock_run):
        """Test file changes extraction."""
        mock_result = Mock()
        mock_result.stdout = "M\tfile1.py\nA\tfile2.py\nD\tfile3.py\n"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        changes = self.git_extractor.get_file_changes("abc123")
        
        self.assertEqual(len(changes), 3)
        self.assertEqual(changes[0]['status'], 'M')
        self.assertEqual(changes[0]['file'], 'file1.py')


class TestSentimentAnalyzer(unittest.TestCase):
    """Test SentimentAnalyzer functionality."""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer("huggingface")
    
    @patch('transformers.pipeline')
    def test_load_model_huggingface(self, mock_pipeline):
        """Test loading HuggingFace model."""
        mock_model = Mock()
        mock_pipeline.return_value = mock_model
        
        self.analyzer.load_model()
        
        self.assertEqual(self.analyzer.model, mock_model)
        mock_pipeline.assert_called_once()
    
    def test_analyze_text_mock(self):
        """Test text analysis with mock model."""
        self.analyzer.model = Mock()
        self.analyzer.model.return_value = [{'label': 'POSITIVE', 'score': 0.9}]
        
        result = self.analyzer.analyze_text("This is great!")
        
        self.assertEqual(result['sentiment'], 'POSITIVE')
        self.assertEqual(result['confidence'], 0.9)
        self.assertEqual(result['text'], 'This is great!')
    
    def test_analyze_batch(self):
        """Test batch text analysis."""
        self.analyzer.model = Mock()
        self.analyzer.model.return_value = [{'label': 'POSITIVE', 'score': 0.8}]
        
        texts = ["Great work!", "Nice job!"]
        results = self.analyzer.analyze_batch(texts)
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['sentiment'], 'POSITIVE')
        self.assertEqual(results[1]['sentiment'], 'POSITIVE')


class TestPreprocessor(unittest.TestCase):
    """Test Preprocessor functionality."""
    
    def setUp(self):
        self.preprocessor = Preprocessor()
    
    def test_clean_commit_message(self):
        """Test commit message cleaning."""
        # Test merge commit removal
        message = "Merge branch 'feature' into main"
        cleaned = self.preprocessor.clean_commit_message(message)
        self.assertEqual(cleaned, "")
        
        # Test issue reference removal
        message = "Fix bug #123 in authentication"
        cleaned = self.preprocessor.clean_commit_message(message)
        self.assertNotIn("#123", cleaned)
        
        # Test URL removal
        message = "Update docs https://example.com"
        cleaned = self.preprocessor.clean_commit_message(message)
        self.assertNotIn("https://example.com", cleaned)
    
    def test_filter_meaningful_commits(self):
        """Test filtering meaningful commits."""
        commits = [
            {'message': 'Fix authentication bug', 'author': 'John'},
            {'message': 'Merge branch', 'author': 'Jane'},
            {'message': 'Add new feature', 'author': 'Bob'},
            {'message': 'a', 'author': 'Alice'}  # Too short
        ]
        
        meaningful = self.preprocessor.filter_meaningful_commits(commits, min_length=5)
        
        self.assertEqual(len(meaningful), 2)
        self.assertEqual(meaningful[0]['message'], 'Fix authentication bug')
        self.assertEqual(meaningful[1]['message'], 'Add new feature')
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = "Fix authentication bug in user login system"
        keywords = self.preprocessor.extract_keywords(text)
        
        self.assertIn('authentication', keywords)
        self.assertIn('login', keywords)
        self.assertNotIn('the', keywords)  # Stop word should be filtered
    
    def test_normalize_text(self):
        """Test text normalization."""
        text = "  Fix   BUG!!!  "
        normalized = self.preprocessor.normalize_text(text)
        
        self.assertEqual(normalized, "fix bug")


class TestVisualizer(unittest.TestCase):
    """Test Visualizer functionality."""
    
    def setUp(self):
        self.visualizer = Visualizer()
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.show')
    def test_create_sentiment_timeline(self, mock_show, mock_savefig):
        """Test sentiment timeline creation."""
        commits = [
            {
                'date': '2024-01-15T10:30:00Z',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            },
            {
                'date': '2024-01-16T10:30:00Z',
                'sentiment': {'sentiment': 'NEGATIVE', 'confidence': 0.7}
            }
        ]
        
        # Should not raise an exception
        self.visualizer.create_sentiment_timeline(commits, "test.png")
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_sentiment_distribution(self, mock_savefig):
        """Test sentiment distribution creation."""
        commits = [
            {'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}},
            {'sentiment': {'sentiment': 'NEGATIVE', 'confidence': 0.7}},
            {'sentiment': {'sentiment': 'NEUTRAL', 'confidence': 0.6}}
        ]
        
        # Should not raise an exception
        self.visualizer.create_sentiment_distribution(commits, "test.png")
        mock_savefig.assert_called_once()
    
    @patch('matplotlib.pyplot.savefig')
    def test_create_word_cloud(self, mock_savefig):
        """Test word cloud creation."""
        commits = [
            {'keywords': ['fix', 'bug', 'authentication']},
            {'keywords': ['add', 'feature', 'login']}
        ]
        
        # Should not raise an exception
        self.visualizer.create_word_cloud(commits, "test.png")
        mock_savefig.assert_called_once()


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_setup_logger(self):
        """Test logger setup."""
        logger = setup_logger("test_logger")
        
        self.assertIsInstance(logger, type(logger))
        self.assertEqual(logger.name, "test_logger")
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        timestamp = "2024-01-15T10:30:00Z"
        
        # Test human format
        formatted = format_timestamp(timestamp, "human")
        self.assertIn("2024-01-15", formatted)
        
        # Test date format
        formatted = format_timestamp(timestamp, "date")
        self.assertEqual(formatted, "2024-01-15")
        
        # Test time format
        formatted = format_timestamp(timestamp, "time")
        self.assertEqual(formatted, "10:30:00")
    
    def test_ensure_directory(self):
        """Test directory creation."""
        temp_dir = tempfile.mkdtemp()
        new_dir = os.path.join(temp_dir, "test_subdir")
        
        result_path = ensure_directory(new_dir)
        
        self.assertTrue(os.path.exists(new_dir))
        self.assertEqual(result_path, Path(new_dir))
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_is_code_file(self):
        """Test code file detection."""
        from core.utils import is_code_file
        
        self.assertTrue(is_code_file("test.py"))
        self.assertTrue(is_code_file("script.js"))
        self.assertTrue(is_code_file("style.css"))
        self.assertFalse(is_code_file("readme.txt"))
        self.assertFalse(is_code_file("data.csv"))


if __name__ == '__main__':
    unittest.main()
