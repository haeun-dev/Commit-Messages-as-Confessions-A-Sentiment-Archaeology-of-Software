"""
Tests for CLI module functionality.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys
import io

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cli.main import main, analyze_repository, generate_summary, generate_visualizations_output


class TestCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('sys.argv', ['codemood', 'analyze', '--help'])
    @patch('argparse.ArgumentParser.print_help')
    def test_main_help(self, mock_print_help):
        """Test help command."""
        with self.assertRaises(SystemExit):
            main()
        mock_print_help.assert_called_once()
    
    @patch('sys.argv', ['codemood', 'analyze', '--repo-path', '.', '--limit', '10'])
    @patch('cli.main.analyze_repository')
    def test_main_analyze(self, mock_analyze):
        """Test analyze command."""
        main()
        mock_analyze.assert_called_once()
    
    @patch('cli.main.GitExtractor')
    @patch('cli.main.SentimentAnalyzer')
    @patch('cli.main.Preprocessor')
    @patch('cli.main.Visualizer')
    def test_analyze_repository_success(self, mock_visualizer, mock_preprocessor, 
                                      mock_sentiment_analyzer, mock_git_extractor):
        """Test successful repository analysis."""
        # Mock components
        mock_git_instance = Mock()
        mock_git_instance.get_commit_messages.return_value = [
            {'hash': 'abc123', 'message': 'Fix bug', 'author': 'John', 'date': '2024-01-15T10:30:00Z'}
        ]
        mock_git_extractor.return_value = mock_git_instance
        
        mock_preprocessor_instance = Mock()
        mock_preprocessor_instance.preprocess_commits.return_value = [
            {'hash': 'abc123', 'message': 'Fix bug', 'author': 'John', 'date': '2024-01-15T10:30:00Z', 'cleaned_message': 'Fix bug'}
        ]
        mock_preprocessor.return_value = mock_preprocessor_instance
        
        mock_sentiment_instance = Mock()
        mock_sentiment_instance.analyze_commit_messages.return_value = [
            {
                'hash': 'abc123', 
                'message': 'Fix bug', 
                'author': 'John', 
                'date': '2024-01-15T10:30:00Z',
                'cleaned_message': 'Fix bug',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            }
        ]
        mock_sentiment_analyzer.return_value = mock_sentiment_instance
        
        mock_visualizer_instance = Mock()
        mock_visualizer.return_value = mock_visualizer_instance
        
        # Mock logger
        mock_logger = Mock()
        
        # Run analysis
        analyze_repository(
            repo_path=self.temp_dir,
            output_dir=os.path.join(self.temp_dir, 'output'),
            limit=10,
            model_type='huggingface',
            model_name=None,
            generate_visualizations=True,
            logger=mock_logger
        )
        
        # Verify calls
        mock_git_instance.get_commit_messages.assert_called_once_with(10)
        mock_preprocessor_instance.preprocess_commits.assert_called_once()
        mock_sentiment_instance.load_model.assert_called_once()
        mock_sentiment_instance.analyze_commit_messages.assert_called_once()
    
    @patch('cli.main.GitExtractor')
    def test_analyze_repository_no_commits(self, mock_git_extractor):
        """Test analysis with no commits."""
        mock_git_instance = Mock()
        mock_git_instance.get_commit_messages.return_value = []
        mock_git_extractor.return_value = mock_git_instance
        
        mock_logger = Mock()
        
        # Should not raise an exception
        analyze_repository(
            repo_path=self.temp_dir,
            output_dir=os.path.join(self.temp_dir, 'output'),
            limit=10,
            model_type='huggingface',
            model_name=None,
            generate_visualizations=True,
            logger=mock_logger
        )
        
        mock_logger.warning.assert_called_with("No commits found in repository")
    
    def test_generate_summary(self):
        """Test summary generation."""
        commits = [
            {
                'cleaned_message': 'Fix authentication bug',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.9}
            },
            {
                'cleaned_message': 'Add new feature',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            },
            {
                'cleaned_message': 'Remove deprecated code',
                'sentiment': {'sentiment': 'NEGATIVE', 'confidence': 0.7}
            }
        ]
        
        output_path = Path(self.temp_dir) / "summary.txt"
        mock_logger = Mock()
        
        generate_summary(commits, output_path, mock_logger)
        
        # Check if summary file was created
        self.assertTrue(output_path.exists())
        
        # Check summary content
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("Total commits analyzed: 3", content)
            self.assertIn("POSITIVE: 2", content)
            self.assertIn("NEGATIVE: 1", content)
    
    @patch('cli.main.Visualizer')
    def test_generate_visualizations_output(self, mock_visualizer_class):
        """Test visualization generation."""
        commits = [
            {
                'cleaned_message': 'Fix bug',
                'sentiment': {'sentiment': 'POSITIVE', 'confidence': 0.8}
            }
        ]
        
        output_path = Path(self.temp_dir)
        mock_visualizer_instance = Mock()
        mock_visualizer_class.return_value = mock_visualizer_instance
        mock_logger = Mock()
        
        generate_visualizations_output(commits, output_path, mock_visualizer_instance, mock_logger)
        
        # Verify visualization methods were called
        mock_visualizer_instance.create_sentiment_timeline.assert_called_once()
        mock_visualizer_instance.create_sentiment_distribution.assert_called_once()
        mock_visualizer_instance.create_word_cloud.assert_called_once()
        mock_visualizer_instance.create_author_sentiment_heatmap.assert_called_once()
    
    @patch('cli.main.Visualizer')
    def test_generate_visualizations_error(self, mock_visualizer_class):
        """Test visualization generation with error."""
        commits = []
        output_path = Path(self.temp_dir)
        mock_visualizer_instance = Mock()
        mock_visualizer_instance.create_sentiment_timeline.side_effect = Exception("Visualization error")
        mock_visualizer_class.return_value = mock_visualizer_instance
        mock_logger = Mock()
        
        # Should not raise an exception
        generate_visualizations_output(commits, output_path, mock_visualizer_instance, mock_logger)
        
        mock_logger.error.assert_called_with("Error generating visualizations: Visualization error")


class TestCLIArgumentParsing(unittest.TestCase):
    """Test CLI argument parsing."""
    
    def test_parse_analyze_command(self):
        """Test parsing analyze command with arguments."""
        with patch('sys.argv', [
            'codemood', 'analyze', 
            '--repo-path', '/path/to/repo',
            '--output-dir', '/path/to/output',
            '--limit', '50',
            '--model', 'openai',
            '--model-name', 'gpt-3.5-turbo',
            '--verbose'
        ]):
            with patch('cli.main.analyze_repository') as mock_analyze:
                main()
                
                # Verify analyze_repository was called with correct arguments
                args, kwargs = mock_analyze.call_args
                self.assertEqual(kwargs['repo_path'], '/path/to/repo')
                self.assertEqual(kwargs['output_dir'], '/path/to/output')
                self.assertEqual(kwargs['limit'], 50)
                self.assertEqual(kwargs['model_type'], 'openai')
                self.assertEqual(kwargs['model_name'], 'gpt-3.5-turbo')
                self.assertTrue(kwargs['generate_visualizations'])
    
    def test_parse_invalid_command(self):
        """Test parsing invalid command."""
        with patch('sys.argv', ['codemood', 'invalid']):
            with patch('argparse.ArgumentParser.print_help') as mock_help:
                with self.assertRaises(SystemExit):
                    main()
                mock_help.assert_called_once()


if __name__ == '__main__':
    unittest.main()
