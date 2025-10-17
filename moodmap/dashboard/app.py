"""
Streamlit dashboard for GitHub Trending Mood Map visualization.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="GitHub Trending Mood Map",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sentiment-positive { color: #2E8B57; }
    .sentiment-neutral { color: #FFD700; }
    .sentiment-negative { color: #DC143C; }
</style>
""", unsafe_allow_html=True)

def load_sample_data() -> Dict[str, Any]:
    """Load sample data for demonstration."""
    return {
        "languages": {
            "Python": {
                "total_repos": 45,
                "total_commits": 1250,
                "sentiment_counts": {"POSITIVE": 750, "NEUTRAL": 350, "NEGATIVE": 150},
                "average_confidence": 0.78,
                "mood_score": 0.48,
                "top_languages": ["Python", "JavaScript", "TypeScript"]
            },
            "JavaScript": {
                "total_repos": 38,
                "total_commits": 980,
                "sentiment_counts": {"POSITIVE": 580, "NEUTRAL": 280, "NEGATIVE": 120},
                "average_confidence": 0.75,
                "mood_score": 0.47,
                "top_languages": ["JavaScript", "TypeScript", "HTML"]
            },
            "TypeScript": {
                "total_repos": 32,
                "total_commits": 890,
                "sentiment_counts": {"POSITIVE": 520, "NEUTRAL": 250, "NEGATIVE": 120},
                "average_confidence": 0.76,
                "mood_score": 0.45,
                "top_languages": ["TypeScript", "JavaScript", "CSS"]
            }
        },
        "regions": {
            "Americas_West": {
                "total_repos": 25,
                "total_commits": 650,
                "sentiment_counts": {"POSITIVE": 380, "NEUTRAL": 180, "NEGATIVE": 90},
                "average_confidence": 0.77,
                "mood_score": 0.45
            },
            "Europe_West": {
                "total_repos": 30,
                "total_commits": 780,
                "sentiment_counts": {"POSITIVE": 460, "NEUTRAL": 220, "NEGATIVE": 100},
                "average_confidence": 0.76,
                "mood_score": 0.46
            },
            "Asia_East": {
                "total_repos": 28,
                "total_commits": 720,
                "sentiment_counts": {"POSITIVE": 420, "NEUTRAL": 200, "NEGATIVE": 100},
                "average_confidence": 0.75,
                "mood_score": 0.44
            }
        },
        "time_periods": {
            "2024-01-15": {
                "total_commits": 45,
                "sentiment_counts": {"POSITIVE": 28, "NEUTRAL": 12, "NEGATIVE": 5},
                "average_confidence": 0.78,
                "mood_score": 0.51
            },
            "2024-01-16": {
                "total_commits": 52,
                "sentiment_counts": {"POSITIVE": 32, "NEUTRAL": 14, "NEGATIVE": 6},
                "average_confidence": 0.76,
                "mood_score": 0.50
            }
        }
    }

def create_sentiment_distribution_chart(data: Dict[str, Any], title: str) -> go.Figure:
    """Create a sentiment distribution pie chart."""
    sentiment_counts = data.get('sentiment_counts', {})
    total = sum(sentiment_counts.values())
    
    if total == 0:
        return go.Figure()
    
    labels = list(sentiment_counts.keys())
    values = list(sentiment_counts.values())
    colors = ['#2E8B57', '#FFD700', '#DC143C']  # Green, Gold, Red
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title=title,
        showlegend=True,
        height=400
    )
    
    return fig

def create_mood_timeline_chart(time_data: Dict[str, Any]) -> go.Figure:
    """Create a mood timeline chart."""
    dates = list(time_data.keys())
    mood_scores = [data.get('mood_score', 0) for data in time_data.values()]
    commit_counts = [data.get('total_commits', 0) for data in time_data.values()]
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Mood Score Over Time', 'Commit Activity'),
        vertical_spacing=0.1
    )
    
    # Mood score line
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=mood_scores,
            mode='lines+markers',
            name='Mood Score',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # Commit count bar
    fig.add_trace(
        go.Bar(
            x=dates,
            y=commit_counts,
            name='Commits',
            marker_color='#ff7f0e'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="GitHub Trending Mood Timeline",
        height=600,
        showlegend=True
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Mood Score (-1 to 1)", row=1, col=1)
    fig.update_yaxes(title_text="Number of Commits", row=2, col=1)
    
    return fig

def create_language_comparison_chart(language_data: Dict[str, Any]) -> go.Figure:
    """Create a language comparison chart."""
    languages = list(language_data.keys())
    mood_scores = [data.get('mood_score', 0) for data in language_data.values()]
    repo_counts = [data.get('total_repos', 0) for data in language_data.values()]
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Mood Score by Language', 'Repository Count by Language'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Mood scores
    fig.add_trace(
        go.Bar(
            x=languages,
            y=mood_scores,
            name='Mood Score',
            marker_color=['#2E8B57' if score > 0 else '#DC143C' if score < 0 else '#FFD700' for score in mood_scores]
        ),
        row=1, col=1
    )
    
    # Repository counts
    fig.add_trace(
        go.Bar(
            x=languages,
            y=repo_counts,
            name='Repository Count',
            marker_color='#1f77b4'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Programming Language Comparison",
        height=500,
        showlegend=False
    )
    
    fig.update_xaxes(title_text="Programming Language", row=1, col=1)
    fig.update_xaxes(title_text="Programming Language", row=1, col=2)
    fig.update_yaxes(title_text="Mood Score", row=1, col=1)
    fig.update_yaxes(title_text="Number of Repositories", row=1, col=2)
    
    return fig

def main():
    """Main dashboard application."""
    # Header
    st.markdown('<h1 class="main-header">😊 GitHub Trending Mood Map</h1>', unsafe_allow_html=True)
    
    # Load data
    data = load_sample_data()
    
    # Sidebar
    st.sidebar.title("Dashboard Controls")
    
    # Data refresh
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Analysis period
    period = st.sidebar.selectbox(
        "Analysis Period",
        ["Last 7 days", "Last 30 days", "Last 90 days"],
        index=1
    )
    
    # Language filter
    available_languages = list(data['languages'].keys())
    selected_languages = st.sidebar.multiselect(
        "Programming Languages",
        available_languages,
        default=available_languages
    )
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    total_repos = sum(data['languages'][lang]['total_repos'] for lang in selected_languages)
    total_commits = sum(data['languages'][lang]['total_commits'] for lang in selected_languages)
    avg_mood = sum(data['languages'][lang]['mood_score'] for lang in selected_languages) / len(selected_languages) if selected_languages else 0
    avg_confidence = sum(data['languages'][lang]['average_confidence'] for lang in selected_languages) / len(selected_languages) if selected_languages else 0
    
    with col1:
        st.metric("Total Repositories", total_repos)
    with col2:
        st.metric("Total Commits", total_commits)
    with col3:
        st.metric("Average Mood Score", f"{avg_mood:.2f}")
    with col4:
        st.metric("Average Confidence", f"{avg_confidence:.2f}")
    
    # Charts section
    st.markdown("---")
    
    # Language comparison
    st.subheader("📊 Programming Language Analysis")
    filtered_language_data = {lang: data['languages'][lang] for lang in selected_languages}
    lang_chart = create_language_comparison_chart(filtered_language_data)
    st.plotly_chart(lang_chart, use_container_width=True)
    
    # Sentiment distributions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Regional Sentiment Distribution")
        if data['regions']:
            # Use first region as example
            first_region = list(data['regions'].keys())[0]
            region_chart = create_sentiment_distribution_chart(
                data['regions'][first_region],
                f"Sentiment in {first_region}"
            )
            st.plotly_chart(region_chart, use_container_width=True)
    
    with col2:
        st.subheader("💻 Language Sentiment Distribution")
        if selected_languages:
            # Use first selected language as example
            first_lang = selected_languages[0]
            lang_sentiment_chart = create_sentiment_distribution_chart(
                data['languages'][first_lang],
                f"Sentiment in {first_lang}"
            )
            st.plotly_chart(lang_sentiment_chart, use_container_width=True)
    
    # Timeline
    st.subheader("📈 Mood Timeline")
    timeline_chart = create_mood_timeline_chart(data['time_periods'])
    st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Detailed tables
    st.markdown("---")
    st.subheader("📋 Detailed Statistics")
    
    # Language statistics table
    lang_stats_data = []
    for lang, stats in filtered_language_data.items():
        lang_stats_data.append({
            'Language': lang,
            'Repositories': stats['total_repos'],
            'Commits': stats['total_commits'],
            'Mood Score': f"{stats['mood_score']:.2f}",
            'Avg Confidence': f"{stats['average_confidence']:.2f}",
            'Positive %': f"{(stats['sentiment_counts']['POSITIVE'] / sum(stats['sentiment_counts'].values()) * 100):.1f}%"
        })
    
    lang_df = pd.DataFrame(lang_stats_data)
    st.dataframe(lang_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>GitHub Trending Mood Map - Analyzing the emotional pulse of open source development</p>
            <p>Built with ❤️ using Streamlit and CodeMood</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
