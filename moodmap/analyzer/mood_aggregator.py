"""
Language and region-based sentiment statistics aggregation.
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import logging
from datetime import datetime, timedelta
import statistics


class MoodAggregator:
    """Aggregate sentiment statistics by language and region."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def aggregate_by_language(self, repositories: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Aggregate sentiment statistics by programming language."""
        language_stats = defaultdict(lambda: {
            'total_repos': 0,
            'total_commits': 0,
            'sentiment_counts': {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0},
            'confidence_scores': [],
            'repositories': [],
            'top_positive_commits': [],
            'top_negative_commits': []
        })
        
        for repo in repositories:
            primary_language = repo.get('primary_language')
            if not primary_language:
                continue
            
            commits = repo.get('commits', [])
            if not commits:
                continue
            
            # Analyze sentiment for commits (assuming sentiment analysis is already done)
            analyzed_commits = self._analyze_commits_sentiment(commits)
            
            # Update language statistics
            lang_stats = language_stats[primary_language]
            lang_stats['total_repos'] += 1
            lang_stats['total_commits'] += len(analyzed_commits)
            lang_stats['repositories'].append({
                'name': repo['full_name'],
                'stars': repo['stars'],
                'commits_count': len(analyzed_commits)
            })
            
            # Aggregate sentiment data
            for commit in analyzed_commits:
                if 'sentiment' in commit:
                    sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                    confidence = commit['sentiment'].get('confidence', 0)
                    
                    lang_stats['sentiment_counts'][sentiment] += 1
                    lang_stats['confidence_scores'].append(confidence)
                    
                    # Track top positive/negative commits
                    if sentiment == 'POSITIVE' and confidence > 0.8:
                        lang_stats['top_positive_commits'].append({
                            'repo': repo['full_name'],
                            'message': commit['message'][:100],
                            'confidence': confidence
                        })
                    elif sentiment == 'NEGATIVE' and confidence > 0.8:
                        lang_stats['top_negative_commits'].append({
                            'repo': repo['full_name'],
                            'message': commit['message'][:100],
                            'confidence': confidence
                        })
        
        # Calculate derived statistics
        for language, stats in language_stats.items():
            stats['average_confidence'] = statistics.mean(stats['confidence_scores']) if stats['confidence_scores'] else 0
            stats['sentiment_distribution'] = self._calculate_sentiment_distribution(stats['sentiment_counts'])
            stats['mood_score'] = self._calculate_mood_score(stats['sentiment_counts'])
            
            # Sort and limit top commits
            stats['top_positive_commits'] = sorted(
                stats['top_positive_commits'], 
                key=lambda x: x['confidence'], 
                reverse=True
            )[:10]
            stats['top_negative_commits'] = sorted(
                stats['top_negative_commits'], 
                key=lambda x: x['confidence'], 
                reverse=True
            )[:10]
        
        return dict(language_stats)
    
    def aggregate_by_region(self, repositories: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Aggregate sentiment statistics by geographic region."""
        # This is a simplified implementation
        # In practice, you'd need to geolocate contributors or use timezone data
        
        region_stats = defaultdict(lambda: {
            'total_repos': 0,
            'total_commits': 0,
            'sentiment_counts': {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0},
            'confidence_scores': [],
            'languages': Counter(),
            'repositories': []
        })
        
        for repo in repositories:
            # Simple region detection based on timezone patterns in commit times
            region = self._detect_region_from_commits(repo.get('commits', []))
            
            if not region:
                continue
            
            commits = repo.get('commits', [])
            analyzed_commits = self._analyze_commits_sentiment(commits)
            
            # Update region statistics
            reg_stats = region_stats[region]
            reg_stats['total_repos'] += 1
            reg_stats['total_commits'] += len(analyzed_commits)
            reg_stats['repositories'].append({
                'name': repo['full_name'],
                'language': repo.get('primary_language'),
                'stars': repo['stars']
            })
            
            # Aggregate sentiment and language data
            for commit in analyzed_commits:
                if 'sentiment' in commit:
                    sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                    confidence = commit['sentiment'].get('confidence', 0)
                    
                    reg_stats['sentiment_counts'][sentiment] += 1
                    reg_stats['confidence_scores'].append(confidence)
            
            # Track language usage in region
            if repo.get('primary_language'):
                reg_stats['languages'][repo['primary_language']] += 1
        
        # Calculate derived statistics
        for region, stats in region_stats.items():
            stats['average_confidence'] = statistics.mean(stats['confidence_scores']) if stats['confidence_scores'] else 0
            stats['sentiment_distribution'] = self._calculate_sentiment_distribution(stats['sentiment_counts'])
            stats['mood_score'] = self._calculate_mood_score(stats['sentiment_counts'])
            stats['top_languages'] = dict(stats['languages'].most_common(5))
        
        return dict(region_stats)
    
    def aggregate_by_time_period(self, repositories: List[Dict[str, Any]], 
                               period_days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Aggregate sentiment statistics by time periods."""
        time_stats = defaultdict(lambda: {
            'total_commits': 0,
            'sentiment_counts': {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0},
            'confidence_scores': [],
            'repositories': set()
        })
        
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        for repo in repositories:
            commits = repo.get('commits', [])
            analyzed_commits = self._analyze_commits_sentiment(commits)
            
            for commit in analyzed_commits:
                try:
                    commit_date = datetime.fromisoformat(
                        commit['author']['date'].replace('Z', '+00:00')
                    )
                    
                    if commit_date >= cutoff_date:
                        period_key = commit_date.strftime('%Y-%m-%d')
                        
                        if 'sentiment' in commit:
                            sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                            confidence = commit['sentiment'].get('confidence', 0)
                            
                            time_stats[period_key]['total_commits'] += 1
                            time_stats[period_key]['sentiment_counts'][sentiment] += 1
                            time_stats[period_key]['confidence_scores'].append(confidence)
                            time_stats[period_key]['repositories'].add(repo['full_name'])
                
                except (ValueError, KeyError) as e:
                    self.logger.warning(f"Error parsing commit date: {e}")
                    continue
        
        # Convert sets to counts and calculate derived statistics
        for period, stats in time_stats.items():
            stats['unique_repositories'] = len(stats['repositories'])
            del stats['repositories']  # Remove set, keep count
            
            stats['average_confidence'] = statistics.mean(stats['confidence_scores']) if stats['confidence_scores'] else 0
            stats['sentiment_distribution'] = self._calculate_sentiment_distribution(stats['sentiment_counts'])
            stats['mood_score'] = self._calculate_mood_score(stats['sentiment_counts'])
        
        return dict(time_stats)
    
    def _analyze_commits_sentiment(self, commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment for commits (placeholder implementation)."""
        # This would integrate with the core sentiment analyzer
        # For now, return commits with mock sentiment data
        analyzed_commits = []
        
        for commit in commits:
            # Mock sentiment analysis - in real implementation, use SentimentAnalyzer
            message = commit.get('message', '')
            sentiment = self._mock_sentiment_analysis(message)
            
            analyzed_commit = {
                **commit,
                'sentiment': sentiment
            }
            analyzed_commits.append(analyzed_commit)
        
        return analyzed_commits
    
    def _mock_sentiment_analysis(self, message: str) -> Dict[str, Any]:
        """Mock sentiment analysis for demonstration."""
        # Simple keyword-based sentiment analysis
        positive_words = ['fix', 'add', 'improve', 'enhance', 'optimize', 'update', 'feature']
        negative_words = ['bug', 'error', 'fail', 'broken', 'remove', 'delete', 'deprecate']
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return {'sentiment': 'POSITIVE', 'confidence': 0.7 + (positive_count * 0.1)}
        elif negative_count > positive_count:
            return {'sentiment': 'NEGATIVE', 'confidence': 0.7 + (negative_count * 0.1)}
        else:
            return {'sentiment': 'NEUTRAL', 'confidence': 0.5}
    
    def _detect_region_from_commits(self, commits: List[Dict[str, Any]]) -> Optional[str]:
        """Detect region from commit timezone patterns."""
        if not commits:
            return None
        
        # Simple timezone-based region detection
        timezones = []
        for commit in commits[:10]:  # Sample first 10 commits
            try:
                date_str = commit.get('author', {}).get('date', '')
                if date_str:
                    # Extract timezone offset
                    if '+' in date_str:
                        offset = date_str.split('+')[1].split(':')[0]
                        timezones.append(int(offset))
                    elif '-' in date_str:
                        offset = date_str.split('-')[1].split(':')[0]
                        timezones.append(-int(offset))
            except (ValueError, IndexError):
                continue
        
        if not timezones:
            return None
        
        # Map timezone to region
        avg_timezone = statistics.mean(timezones)
        
        if -12 <= avg_timezone <= -8:
            return 'Americas_West'
        elif -7 <= avg_timezone <= -5:
            return 'Americas_Central'
        elif -4 <= avg_timezone <= -2:
            return 'Americas_East'
        elif -1 <= avg_timezone <= 1:
            return 'Europe_West'
        elif 2 <= avg_timezone <= 4:
            return 'Europe_East'
        elif 5 <= avg_timezone <= 6:
            return 'Asia_India'
        elif 7 <= avg_timezone <= 9:
            return 'Asia_Southeast'
        elif 8 <= avg_timezone <= 10:
            return 'Asia_East'
        else:
            return 'Other'
    
    def _calculate_sentiment_distribution(self, sentiment_counts: Dict[str, int]) -> Dict[str, float]:
        """Calculate percentage distribution of sentiments."""
        total = sum(sentiment_counts.values())
        if total == 0:
            return {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
        
        return {
            sentiment: (count / total) * 100
            for sentiment, count in sentiment_counts.items()
        }
    
    def _calculate_mood_score(self, sentiment_counts: Dict[str, int]) -> float:
        """Calculate overall mood score (-1 to 1)."""
        total = sum(sentiment_counts.values())
        if total == 0:
            return 0
        
        positive = sentiment_counts.get('POSITIVE', 0)
        negative = sentiment_counts.get('NEGATIVE', 0)
        
        return (positive - negative) / total
