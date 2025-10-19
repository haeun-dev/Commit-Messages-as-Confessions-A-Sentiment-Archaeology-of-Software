"""
CLI entry point for codemood analyze command.
"""

import argparse
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

from core import GitExtractor, SentimentAnalyzer, Preprocessor, Visualizer, setup_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze code mood from git repository",
        prog="codemood"
    )
    
    parser.add_argument(
        "command",
        choices=["analyze"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "repo_path",
        type=str,
        nargs="?",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate visualizations (default: False)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./codemood_output",
        help="Output directory for results (default: ./codemood_output)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of commits to analyze (default: 100)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        choices=["huggingface", "openai"],
        default="huggingface",
        help="Sentiment analysis model to use (default: huggingface)"
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        help="Specific model name (optional)"
    )
    
    parser.add_argument(
        "--api-key",
        type=str,
        help="API key for paid models (e.g., OpenAI). Can also be set via OPENAI_API_KEY environment variable"
    )
    
    parser.add_argument(
        "--organization",
        type=str,
        help="Organization ID for OpenAI API (optional)"
    )
    
    parser.add_argument(
        "--show-costs",
        action="store_true",
        help="Show cost tracking information for paid models"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger("codemood", level=log_level)
    
    try:
        if args.command == "analyze":
            analyze_repository(
                repo_path=args.repo_path,
                output_dir=args.output_dir,
                limit=args.limit,
                model_type=args.model,
                model_name=args.model_name,
                api_key=args.api_key,
                organization=args.organization,
                show_costs=args.show_costs,
                generate_visualizations=args.visualize,
                logger=logger
            )
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def analyze_repository(
    repo_path: str,
    output_dir: str,
    limit: int,
    model_type: str,
    model_name: Optional[str],
    api_key: Optional[str],
    organization: Optional[str],
    show_costs: bool,
    generate_visualizations: bool,
    logger
):
    """Analyze repository sentiment."""
    logger.info(f"Starting analysis of repository: {repo_path}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    git_extractor = GitExtractor(repo_path)
    sentiment_analyzer = SentimentAnalyzer(
        model_type=model_type, 
        model_name=model_name,
        api_key=api_key,
        organization=organization
    )
    preprocessor = Preprocessor()
    visualizer = Visualizer()
    
    # Get repository stats
    repo_stats = git_extractor.get_repository_stats()
    
    # Extract git data
    logger.info("Extracting git commit data...")
    commits = git_extractor.get_commit_messages(limit)
    logger.info(f"Found {len(commits)} commits")
    
    if not commits:
        logger.warning("No commits found in repository")
        return
    
    # Extract additional data (comments and functions)
    logger.info("Extracting comments and function names...")
    all_comments = []
    all_functions = []
    
    # Get list of files in the repository
    try:
        cmd = ["git", "ls-files"]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        # Sample files for analysis (limit to avoid performance issues)
        sample_files = files[:50]  # Analyze up to 50 files
        
        for file_path in sample_files:
            if git_extractor.is_code_file(file_path):
                full_path = Path(repo_path) / file_path
                comments = git_extractor.get_comments_from_file(str(full_path))
                functions = git_extractor.get_function_names(str(full_path))
                all_comments.extend(comments)
                all_functions.extend(functions)
    except Exception as e:
        logger.warning(f"Error extracting additional data: {e}")
    
    # Preprocess commits
    logger.info("Preprocessing commit messages...")
    processed_commits = preprocessor.preprocess_commits(commits)
    logger.info(f"Processed {len(processed_commits)} meaningful commits")
    
    if not processed_commits:
        logger.warning("No meaningful commits found after preprocessing")
        return
    
    # Analyze sentiment
    logger.info("Analyzing sentiment...")
    sentiment_analyzer.load_model()
    analyzed_commits = sentiment_analyzer.analyze_commit_messages(processed_commits)
    
    # Calculate overall sentiment
    sentiment_scores = []
    for commit in analyzed_commits:
        if 'sentiment' in commit:
            sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
            confidence = commit['sentiment'].get('confidence', 0.5)
            # Convert to numeric score: POSITIVE=1, NEUTRAL=0, NEGATIVE=-1
            score_map = {'POSITIVE': 1, 'NEUTRAL': 0, 'NEGATIVE': -1}
            sentiment_scores.append(score_map.get(sentiment, 0) * confidence)
    
    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    # Print summary to console
    print(f"🔍 Collected {len(commits)} commits, {len(all_comments)} comments, {len(all_functions)} functions")
    
    if avg_sentiment > 0.1:
        mood = "Joy dominant"
    elif avg_sentiment < -0.1:
        mood = "Frustration dominant"
    else:
        mood = "Neutral"
    
    print(f"🧠 Average sentiment: {avg_sentiment:.2f} ({mood})")
    
    # Show cost information if requested
    if show_costs and model_type == "openai":
        cost_info = sentiment_analyzer.get_cost_info()
        print(f"💰 Cost tracking - Tokens used: {cost_info['tokens_used']}, "
              f"Estimated cost: ${cost_info['estimated_cost']:.4f}")
    
    # Generate JSON report
    generate_json_report(analyzed_commits, repo_stats, all_comments, all_functions, 
                        avg_sentiment, output_path, logger, sentiment_analyzer if show_costs else None)
    
    # Generate visualizations
    if generate_visualizations:
        logger.info("Generating visualizations...")
        generate_visualizations_output(analyzed_commits, output_path, visualizer, logger)
        print(f"📈 Visualization: codemood_graph.png generated")
    
    logger.info(f"Analysis complete! Results saved to: {output_path}")


def generate_json_report(commits, repo_stats, comments, functions, avg_sentiment, output_path: Path, logger, sentiment_analyzer=None):
    """Generate comprehensive JSON report."""
    report_path = output_path / "codemood_report.json"
    
    # Calculate sentiment distribution
    sentiment_counts = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
    for commit in commits:
        if 'sentiment' in commit:
            sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
            sentiment_counts[sentiment] += 1
    
    # Get top positive and negative commits
    positive_commits = [c for c in commits if c.get('sentiment', {}).get('sentiment') == 'POSITIVE']
    negative_commits = [c for c in commits if c.get('sentiment', {}).get('sentiment') == 'NEGATIVE']
    
    positive_commits.sort(key=lambda x: x.get('sentiment', {}).get('confidence', 0), reverse=True)
    negative_commits.sort(key=lambda x: x.get('sentiment', {}).get('confidence', 0), reverse=True)
    
    # Determine mood category
    if avg_sentiment > 0.1:
        mood_category = "Joyful"
        mood_description = "The codebase shows positive energy and enthusiasm"
    elif avg_sentiment < -0.1:
        mood_category = "Frustrated"
        mood_description = "The codebase shows signs of frustration and stress"
    else:
        mood_category = "Neutral"
        mood_description = "The codebase maintains a balanced emotional tone"
    
    # Create comprehensive report
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "codemood_version": "0.1.0",
            "analysis_type": "git_repository_sentiment"
        },
        "repository": {
            "path": repo_stats.get('repository_path', ''),
            "total_commits": repo_stats.get('total_commits', 0),
            "total_files": repo_stats.get('total_files', 0),
            "repository_size": repo_stats.get('repository_size', 'Unknown')
        },
        "analysis_summary": {
            "commits_analyzed": len(commits),
            "comments_found": len(comments),
            "functions_found": len(functions),
            "average_sentiment": round(avg_sentiment, 3),
            "mood_category": mood_category,
            "mood_description": mood_description
        },
        "cost_tracking": sentiment_analyzer.get_cost_info() if sentiment_analyzer else None,
        "sentiment_distribution": sentiment_counts,
        "top_insights": {
            "most_positive_commits": [
                {
                    "message": commit.get('cleaned_message', commit.get('message', ''))[:100],
                    "confidence": commit.get('sentiment', {}).get('confidence', 0),
                    "date": commit.get('date', ''),
                    "author": commit.get('author', '')
                }
                for commit in positive_commits[:5]
            ],
            "most_negative_commits": [
                {
                    "message": commit.get('cleaned_message', commit.get('message', ''))[:100],
                    "confidence": commit.get('sentiment', {}).get('confidence', 0),
                    "date": commit.get('date', ''),
                    "author": commit.get('author', '')
                }
                for commit in negative_commits[:5]
            ]
        },
        "detailed_commits": [
            {
                "hash": commit.get('hash', ''),
                "author": commit.get('author', ''),
                "date": commit.get('date', ''),
                "message": commit.get('message', ''),
                "cleaned_message": commit.get('cleaned_message', ''),
                "sentiment": commit.get('sentiment', {}),
                "keywords": commit.get('keywords', [])
            }
            for commit in commits
        ],
        "extracted_data": {
            "sample_comments": comments[:20],  # First 20 comments
            "sample_functions": functions[:20]  # First 20 functions
        }
    }
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"JSON report saved to {report_path}")


def generate_summary(commits, output_path: Path, logger):
    """Generate text summary of analysis."""
    summary_path = output_path / "summary.txt"
    
    # Calculate statistics
    total_commits = len(commits)
    sentiment_counts = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
    total_confidence = 0
    
    for commit in commits:
        if 'sentiment' in commit:
            sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
            confidence = commit['sentiment'].get('confidence', 0)
            sentiment_counts[sentiment] += 1
            total_confidence += confidence
    
    avg_confidence = total_confidence / total_commits if total_commits > 0 else 0
    
    # Write summary
    with open(summary_path, 'w') as f:
        f.write("CodeMood Analysis Summary\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Total commits analyzed: {total_commits}\n")
        f.write(f"Average confidence: {avg_confidence:.2f}\n\n")
        f.write("Sentiment distribution:\n")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total_commits) * 100 if total_commits > 0 else 0
            f.write(f"  {sentiment}: {count} ({percentage:.1f}%)\n")
        
        f.write("\nTop positive commits:\n")
        positive_commits = [c for c in commits if c.get('sentiment', {}).get('sentiment') == 'POSITIVE']
        positive_commits.sort(key=lambda x: x.get('sentiment', {}).get('confidence', 0), reverse=True)
        for commit in positive_commits[:5]:
            f.write(f"  - {commit['cleaned_message'][:100]}...\n")
        
        f.write("\nTop negative commits:\n")
        negative_commits = [c for c in commits if c.get('sentiment', {}).get('sentiment') == 'NEGATIVE']
        negative_commits.sort(key=lambda x: x.get('sentiment', {}).get('confidence', 0), reverse=True)
        for commit in negative_commits[:5]:
            f.write(f"  - {commit['cleaned_message'][:100]}...\n")
    
    logger.info(f"Summary saved to {summary_path}")


def generate_visualizations_output(commits, output_path: Path, visualizer: Visualizer, logger):
    """Generate all visualization outputs."""
    try:
        # Combined mood graph
        combined_path = output_path / "codemood_graph.png"
        visualizer.create_combined_mood_graph(commits, str(combined_path))
        
        logger.info("Visualizations generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating visualizations: {e}")


if __name__ == "__main__":
    main()
