"""
Generate graphs and word clouds for sentiment visualization.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import logging


class Visualizer:
    """Create visualizations for sentiment analysis results."""
    
    def __init__(self, style: str = "seaborn-v0_8"):
        self.style = style
        self.logger = logging.getLogger(__name__)
        plt.style.use(style)
        
    def create_sentiment_timeline(self, commits: List[Dict[str, Any]], 
                                output_path: Optional[str] = None) -> None:
        """Create a timeline showing sentiment over time."""
        if not commits:
            self.logger.warning("No commits to visualize")
            return
        
        # Prepare data
        dates = []
        sentiments = []
        confidences = []
        
        for commit in commits:
            if 'sentiment' in commit and 'date' in commit:
                try:
                    date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                    dates.append(date)
                    
                    sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                    confidence = commit['sentiment'].get('confidence', 0.5)
                    
                    # Convert sentiment to numeric for plotting
                    sentiment_map = {'POSITIVE': 1, 'NEUTRAL': 0, 'NEGATIVE': -1}
                    sentiments.append(sentiment_map.get(sentiment, 0))
                    confidences.append(confidence)
                except Exception as e:
                    self.logger.error(f"Error processing commit date: {e}")
                    continue
        
        if not dates:
            self.logger.warning("No valid dates found in commits")
            return
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot sentiment over time
        ax.scatter(dates, sentiments, alpha=0.6, s=50, c=confidences, 
                  cmap='RdYlGn', edgecolors='black', linewidth=0.5)
        
        # Add trend line
        if len(dates) > 1:
            import numpy as np
            dates_numeric = [d.timestamp() for d in dates]
            z = np.polyfit(dates_numeric, sentiments, 1)
            p = np.poly1d(z)
            ax.plot(dates, p(dates_numeric), "r--", alpha=0.8, linewidth=2)
        
        ax.set_xlabel('Date')
        ax.set_ylabel('Sentiment')
        ax.set_title('Code Mood Timeline')
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(['Negative', 'Neutral', 'Positive'])
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(ax.collections[0], ax=ax)
        cbar.set_label('Confidence')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Timeline saved to {output_path}")
        else:
            plt.show()
    
    def create_sentiment_distribution(self, commits: List[Dict[str, Any]], 
                                    output_path: Optional[str] = None) -> None:
        """Create a distribution chart of sentiments."""
        if not commits:
            return
        
        # Count sentiments
        sentiment_counts = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
        
        for commit in commits:
            if 'sentiment' in commit:
                sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                sentiment_counts[sentiment] += 1
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = list(sentiment_counts.keys())
        sizes = list(sentiment_counts.values())
        colors = ['#2E8B57', '#FFD700', '#DC143C']  # Green, Gold, Red
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                         autopct='%1.1f%%', startangle=90)
        
        ax.set_title('Sentiment Distribution')
        
        # Enhance text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Distribution chart saved to {output_path}")
        else:
            plt.show()
    
    def create_word_cloud(self, commits: List[Dict[str, Any]], 
                         output_path: Optional[str] = None) -> None:
        """Create a word cloud from commit messages."""
        if not commits:
            return
        
        # Collect all keywords
        all_keywords = []
        for commit in commits:
            if 'keywords' in commit:
                all_keywords.extend(commit['keywords'])
        
        if not all_keywords:
            self.logger.warning("No keywords found for word cloud")
            return
        
        # Create word cloud
        text = ' '.join(all_keywords)
        
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate(text)
        
        # Display
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Most Common Words in Commit Messages')
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Word cloud saved to {output_path}")
        else:
            plt.show()
    
    def create_author_sentiment_heatmap(self, commits: List[Dict[str, Any]], 
                                      output_path: Optional[str] = None) -> None:
        """Create a heatmap showing sentiment by author."""
        if not commits:
            return
        
        # Prepare data
        author_sentiments = {}
        
        for commit in commits:
            author = commit.get('author', 'Unknown')
            if 'sentiment' in commit:
                sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                
                if author not in author_sentiments:
                    author_sentiments[author] = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
                
                author_sentiments[author][sentiment] += 1
        
        if not author_sentiments:
            return
        
        # Create DataFrame
        df = pd.DataFrame(author_sentiments).T
        df = df.fillna(0)
        
        # Normalize by row (author)
        df_norm = df.div(df.sum(axis=1), axis=0)
        
        # Create heatmap
        plt.figure(figsize=(10, max(6, len(author_sentiments) * 0.5)))
        sns.heatmap(df_norm, annot=True, fmt='.2f', cmap='RdYlGn', 
                   cbar_kws={'label': 'Proportion'})
        
        plt.title('Sentiment Distribution by Author')
        plt.xlabel('Sentiment')
        plt.ylabel('Author')
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Author heatmap saved to {output_path}")
        else:
            plt.show()
    
    def create_combined_mood_graph(self, commits: List[Dict[str, Any]], 
                                 output_path: Optional[str] = None) -> None:
        """Create a combined mood graph with multiple visualizations."""
        if not commits:
            self.logger.warning("No commits to visualize")
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Sentiment Timeline (top left)
        ax1 = plt.subplot(2, 2, 1)
        self._plot_sentiment_timeline(commits, ax1)
        
        # 2. Sentiment Distribution (top right)
        ax2 = plt.subplot(2, 2, 2)
        self._plot_sentiment_distribution(commits, ax2)
        
        # 3. Word Cloud (bottom left)
        ax3 = plt.subplot(2, 2, 3)
        self._plot_word_cloud(commits, ax3)
        
        # 4. Author Sentiment (bottom right)
        ax4 = plt.subplot(2, 2, 4)
        self._plot_author_sentiment(commits, ax4)
        
        plt.suptitle('CodeMood Analysis Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Combined mood graph saved to {output_path}")
        else:
            plt.show()
    
    def _plot_sentiment_timeline(self, commits: List[Dict[str, Any]], ax) -> None:
        """Plot sentiment timeline on given axis."""
        dates = []
        sentiments = []
        confidences = []
        
        for commit in commits:
            if 'sentiment' in commit and 'date' in commit:
                try:
                    date = datetime.fromisoformat(commit['date'].replace('Z', '+00:00'))
                    dates.append(date)
                    
                    sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                    confidence = commit['sentiment'].get('confidence', 0.5)
                    
                    sentiment_map = {'POSITIVE': 1, 'NEUTRAL': 0, 'NEGATIVE': -1}
                    sentiments.append(sentiment_map.get(sentiment, 0))
                    confidences.append(confidence)
                except Exception:
                    continue
        
        if dates:
            # Check if we have variation in sentiment
            unique_sentiments = set(sentiments)
            if len(unique_sentiments) > 1:
                # Normal timeline with variation
                ax.scatter(dates, sentiments, alpha=0.6, s=50, c=confidences, 
                          cmap='RdYlGn', edgecolors='black', linewidth=0.5)
                ax.set_yticks([-1, 0, 1])
                ax.set_yticklabels(['Negative', 'Neutral', 'Positive'])
            else:
                # All neutral - show as a line with confidence variation
                ax.plot(dates, sentiments, 'o-', alpha=0.7, markersize=4, color='gold')
                ax.fill_between(dates, [s-0.1 for s in sentiments], [s+0.1 for s in sentiments], 
                               alpha=0.3, color='gold')
                ax.set_ylim(-0.2, 0.2)
                ax.set_yticks([0])
                ax.set_yticklabels(['Neutral'])
            
            ax.set_xlabel('Date')
            ax.set_ylabel('Sentiment')
            ax.set_title('Sentiment Timeline')
            ax.grid(True, alpha=0.3)
    
    def _plot_sentiment_distribution(self, commits: List[Dict[str, Any]], ax) -> None:
        """Plot sentiment distribution on given axis."""
        sentiment_counts = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
        
        for commit in commits:
            if 'sentiment' in commit:
                sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                sentiment_counts[sentiment] += 1
        
        # Check if we have variation
        non_zero_counts = [count for count in sentiment_counts.values() if count > 0]
        
        if len(non_zero_counts) > 1:
            # Normal pie chart with multiple sentiments
            labels = list(sentiment_counts.keys())
            sizes = list(sentiment_counts.values())
            colors = ['#2E8B57', '#FFD700', '#DC143C']
            
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, 
                                             autopct='%1.1f%%', startangle=90)
            ax.set_title('Sentiment Distribution')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        else:
            # All one sentiment - show as a single colored circle with text
            total_commits = sum(sentiment_counts.values())
            sentiment_type = [k for k, v in sentiment_counts.items() if v > 0][0]
            
            colors = {'POSITIVE': '#2E8B57', 'NEUTRAL': '#FFD700', 'NEGATIVE': '#DC143C'}
            
            ax.pie([total_commits], labels=[sentiment_type], colors=[colors[sentiment_type]], 
                   autopct='%1.1f%%', startangle=90)
            ax.set_title(f'Sentiment Distribution\n(All {sentiment_type.lower()})')
    
    def _plot_word_cloud(self, commits: List[Dict[str, Any]], ax) -> None:
        """Plot word cloud on given axis."""
        all_keywords = []
        for commit in commits:
            if 'keywords' in commit:
                all_keywords.extend(commit['keywords'])
        
        # If no keywords, use cleaned commit messages
        if not all_keywords:
            for commit in commits:
                if 'cleaned_message' in commit:
                    # Split into words and filter out common words
                    words = commit['cleaned_message'].lower().split()
                    # Filter out very short words and common words
                    filtered_words = [w for w in words if len(w) > 2 and w not in 
                                    ['the', 'and', 'or', 'but', 'for', 'with', 'from', 'this', 'that']]
                    all_keywords.extend(filtered_words)
        
        if all_keywords:
            text = ' '.join(all_keywords)
            wordcloud = WordCloud(
                width=400, 
                height=200, 
                background_color='white',
                max_words=50,
                colormap='viridis'
            ).generate(text)
            
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.set_title('Most Common Words')
        else:
            ax.text(0.5, 0.5, 'No text data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('Most Common Words')
        
        ax.axis('off')
    
    def _plot_author_sentiment(self, commits: List[Dict[str, Any]], ax) -> None:
        """Plot author sentiment on given axis."""
        author_sentiments = {}
        
        for commit in commits:
            author = commit.get('author', 'Unknown')
            if 'sentiment' in commit:
                sentiment = commit['sentiment'].get('sentiment', 'NEUTRAL')
                
                if author not in author_sentiments:
                    author_sentiments[author] = {'POSITIVE': 0, 'NEUTRAL': 0, 'NEGATIVE': 0}
                
                author_sentiments[author][sentiment] += 1
        
        if author_sentiments:
            # Limit to top 10 authors
            sorted_authors = sorted(author_sentiments.items(), 
                                  key=lambda x: sum(x[1].values()), reverse=True)[:10]
            
            authors = [author for author, _ in sorted_authors]
            positive_counts = [data['POSITIVE'] for _, data in sorted_authors]
            neutral_counts = [data['NEUTRAL'] for _, data in sorted_authors]
            negative_counts = [data['NEGATIVE'] for _, data in sorted_authors]
            
            # Check if we have variation in sentiment
            has_variation = any(positive_counts) or any(negative_counts)
            
            if has_variation:
                # Normal stacked bar chart
                x = range(len(authors))
                width = 0.6
                
                ax.bar(x, positive_counts, width, label='Positive', color='#2E8B57', bottom=[0]*len(authors))
                ax.bar(x, neutral_counts, width, label='Neutral', color='#FFD700', 
                      bottom=positive_counts)
                ax.bar(x, negative_counts, width, label='Negative', color='#DC143C',
                      bottom=[p+n for p, n in zip(positive_counts, neutral_counts)])
                
                ax.legend()
            else:
                # All neutral - show simple bar chart
                x = range(len(authors))
                width = 0.6
                
                ax.bar(x, neutral_counts, width, color='#FFD700', label='Neutral')
                ax.set_title('Commits by Author\n(All Neutral)')
            
            ax.set_xlabel('Authors')
            ax.set_ylabel('Commit Count')
            if has_variation:
                ax.set_title('Sentiment by Author')
            ax.set_xticks(x)
            ax.set_xticklabels(authors, rotation=45, ha='right')
        else:
            ax.text(0.5, 0.5, 'No author data', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('Sentiment by Author')