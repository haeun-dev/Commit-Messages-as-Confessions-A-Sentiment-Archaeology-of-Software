# CodeMood: A Sentiment Analysis Framework for Software Development Workflows

## Abstract

CodeMood is a research-oriented tool that applies natural language processing and sentiment analysis techniques to analyze the emotional patterns embedded in software development artifacts. By examining commit messages, code comments, and function naming conventions across multiple programming languages, CodeMood provides quantitative insights into developer emotional states and project dynamics. The tool supports 25+ programming languages and generates comprehensive reports with statistical analysis and visualizations.

## 1. Introduction

Software development is inherently a human activity that involves complex cognitive and emotional processes. While traditional software engineering metrics focus on code quality, performance, and maintainability, the emotional aspects of development have received limited attention in empirical research. CodeMood addresses this gap by providing a systematic approach to analyzing emotional patterns in development workflows.

### 1.1 Research Motivation

The motivation for this work stems from several observations:

- Developer emotional state correlates with code quality and productivity
- Commit messages often contain emotional indicators that reflect development stress
- Code comments and function names can reveal developer frustration or satisfaction
- Understanding emotional patterns can improve team dynamics and project management

### 1.2 Objectives

The primary objectives of CodeMood are:

1. **Quantitative Analysis**: Provide measurable metrics for emotional patterns in software development
2. **Multi-language Support**: Analyze codebases across diverse programming languages
3. **Temporal Analysis**: Track emotional patterns over time to identify trends
4. **Team Dynamics**: Understand how different developers contribute to project emotional tone
5. **Research Foundation**: Enable empirical studies on the relationship between emotions and software quality

## 2. System Architecture

CodeMood implements a modular architecture consisting of four core components:

### 2.1 Core Components

- **GitExtractor**: Extracts and processes Git repository metadata
- **SentimentAnalyzer**: Applies NLP models for emotion classification
- **Preprocessor**: Normalizes and filters textual data
- **Visualizer**: Generates statistical visualizations and reports

## 3. Installation and Setup

### 3.1 System Requirements

- Python 3.8 or higher
- Git version control system
- Minimum 4GB RAM (for NLP model processing)
- 2GB available disk space

### 3.2 Dependencies

CodeMood requires the following Python packages:

- `transformers>=4.21.0` - HuggingFace NLP models
- `torch>=1.12.0` - PyTorch for model inference
- `matplotlib>=3.5.0` - Data visualization
- `seaborn>=0.11.0` - Statistical visualization
- `pandas>=1.4.0` - Data manipulation
- `numpy>=1.21.0` - Numerical computing
- `wordcloud>=1.9.0` - Word cloud generation

### 3.3 Installation

```bash
# Clone the repository
git clone https://github.com/codemood/codemood.git
cd codemood

# Install dependencies
pip install -r requirements.txt

# For OpenAI support (optional)
pip install openai

# Verify installation
python3 -m cli.main --help
```

### 3.4 AI Model Configuration

CodeMood supports both free and paid AI models for sentiment analysis:

#### 3.4.1 Free Models (Default)

- **HuggingFace Models**: Uses local models that run entirely on your machine
- **No API costs**: Completely free to use
- **Privacy**: All data stays on your local machine
- **Default model**: `cardiffnlp/twitter-roberta-base-sentiment-latest`

#### 3.4.2 Paid Models (OpenAI)

- **OpenAI GPT models**: Higher accuracy and better understanding of code context
- **API costs**: Pay per token usage (typically $0.001-0.03 per 1K tokens)
- **Setup required**: API key configuration needed

**Setting up OpenAI API:**

```bash
# Option 1: Environment variable
export OPENAI_API_KEY="your-api-key-here"

# Option 2: Create .env file
cp env.example .env
# Edit .env and add your API key

# Option 3: Pass via CLI
python3 -m cli.main analyze --model openai --api-key "your-api-key-here"
```

**Cost Estimation:**

- Small repository (100 commits): ~$0.01-0.05
- Medium repository (1000 commits): ~$0.10-0.50
- Large repository (10000 commits): ~$1.00-5.00

## 4. Usage

### 4.1 Command Line Interface

The primary interface is a command-line tool that follows standard Unix conventions:

```bash
python3 -m cli.main analyze [REPOSITORY_PATH] [OPTIONS]
```

#### 4.1.1 Basic Usage

```bash
# Analyze current directory
python3 -m cli.main analyze

# Analyze specific repository
python3 -m cli.main analyze /path/to/repository

# Generate visualizations
python3 -m cli.main analyze . --visualize
```

#### 4.1.2 Advanced Configuration

```bash
# Using free HuggingFace models (default)
python3 -m cli.main analyze . \
  --visualize \
  --limit 200 \
  --output-dir ./analysis_results \
  --model huggingface \
  --model-name cardiffnlp/twitter-roberta-base-sentiment-latest \
  --verbose

# Using paid OpenAI models with cost tracking
python3 -m cli.main analyze . \
  --model openai \
  --model-name gpt-3.5-turbo \
  --api-key "your-openai-api-key" \
  --show-costs \
  --visualize

# Using environment variables for API keys
export OPENAI_API_KEY="your-api-key"
python3 -m cli.main analyze . --model openai --show-costs
```

### 4.2 Command Line Options

| Option                         | Description                      | Default             |
| ------------------------------ | -------------------------------- | ------------------- |
| `--visualize`                  | Generate visualization dashboard | False               |
| `--output-dir DIR`             | Output directory for results     | `./codemood_output` |
| `--limit N`                    | Maximum commits to analyze       | 100                 |
| `--model {huggingface,openai}` | Sentiment analysis model         | `huggingface`       |
| `--model-name NAME`            | Specific model identifier        | Auto-selected       |
| `--api-key KEY`                | API key for paid models          | From environment    |
| `--organization ID`            | OpenAI organization ID           | None                |
| `--show-costs`                 | Display cost tracking info       | False               |
| `--verbose`                    | Enable detailed logging          | False               |

## 5. Technical Implementation

### 5.1 Data Extraction Pipeline

#### 5.1.1 GitExtractor Module

The `GitExtractor` class implements a comprehensive data extraction pipeline:

```python
class GitExtractor:
    def get_commit_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Extract commit messages with metadata including hash, author, date, and message."""

    def get_function_names(self, file_path: str) -> List[str]:
        """Extract function and class names using language-specific regex patterns."""

    def get_comments_from_file(self, file_path: str) -> List[str]:
        """Extract meaningful comments using language-specific comment syntax."""
```

**Supported Programming Languages:**

- **Core Languages**: Python, JavaScript, TypeScript, Java, C/C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, Scala
- **Additional Languages**: R, MATLAB, Perl, Shell Scripts, PowerShell, SQL, Lua, Dart
- **Web Technologies**: HTML, Vue.js, Svelte, Astro
- **Configuration Files**: YAML, JSON, TOML, XML, INI

#### 5.1.2 Sentiment Analysis Engine

The `SentimentAnalyzer` class implements state-of-the-art NLP models:

```python
class SentimentAnalyzer:
    def __init__(self, model_type: str = "huggingface", model_name: Optional[str] = None):
        self.model_name = model_name or "cardiffnlp/twitter-roberta-base-sentiment-latest"

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using transformer-based models."""
        # Returns: {'sentiment': 'POSITIVE/NEGATIVE/NEUTRAL', 'confidence': float, 'text': str}
```

**Model Architecture:**

- **Base Model**: RoBERTa (Robustly Optimized BERT Pretraining Approach)
- **Training Data**: Twitter sentiment analysis dataset
- **Output Classes**: Positive, Negative, Neutral
- **Confidence Scoring**: Probability distribution over sentiment classes

#### 5.1.3 Text Preprocessing Pipeline

The `Preprocessor` class implements robust text normalization:

```python
class Preprocessor:
    def clean_commit_message(self, message: str) -> str:
        """Remove merge commits, issue references, and URLs."""

    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords using stop-word filtering."""

    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent analysis."""
```

**Preprocessing Steps:**

1. **Filtering**: Remove merge commits, revert commits, and meaningless messages
2. **Cleaning**: Strip URLs, issue references, and special characters
3. **Normalization**: Convert to lowercase, remove extra whitespace
4. **Keyword Extraction**: Apply stop-word filtering and frequency analysis

### 5.2 Visualization Framework

The `Visualizer` class generates comprehensive statistical visualizations:

```python
class Visualizer:
    def create_combined_mood_graph(self, commits: List[Dict], output_path: str):
        """Generate 4-panel dashboard with temporal and distributional analysis."""
```

**Visualization Components:**

1. **Sentiment Timeline**: Temporal analysis with trend lines and confidence intervals
2. **Sentiment Distribution**: Statistical breakdown of emotional categories
3. **Word Cloud**: Frequency analysis of commit message vocabulary
4. **Author Analysis**: Comparative sentiment analysis across team members

## 6. Output and Results

### 6.1 Console Output

The tool provides real-time feedback during analysis:

```bash
🔍 Collected 84 commits, 217 comments, 152 functions
🧠 Average sentiment: -0.21 (Frustration dominant)
📈 Visualization: codemood_graph.png generated
```

### 6.2 JSON Report Structure

CodeMood generates comprehensive JSON reports with the following schema:

```json
{
  "metadata": {
    "generated_at": "2025-10-17T18:49:49.216491",
    "codemood_version": "0.1.0",
    "analysis_type": "git_repository_sentiment"
  },
  "repository": {
    "path": "/path/to/repo",
    "total_commits": 84,
    "total_files": 45,
    "repository_size": "2.3M"
  },
  "analysis_summary": {
    "commits_analyzed": 84,
    "comments_found": 217,
    "functions_found": 152,
    "average_sentiment": -0.21,
    "mood_category": "Frustrated",
    "mood_description": "The codebase shows signs of frustration and stress"
  },
  "sentiment_distribution": {
    "POSITIVE": 25,
    "NEUTRAL": 35,
    "NEGATIVE": 24
  },
  "top_insights": {
    "most_positive_commits": [...],
    "most_negative_commits": [...]
  },
  "detailed_commits": [...],
  "extracted_data": {
    "sample_comments": [...],
    "sample_functions": [...]
  }
}
```

### 6.3 Visualization Dashboard

The tool generates a comprehensive dashboard (`codemood_graph.png`) with four analytical panels:

1. **Sentiment Timeline**: Temporal analysis showing emotional patterns over time with trend lines
2. **Sentiment Distribution**: Statistical breakdown of emotional categories with confidence intervals
3. **Word Cloud**: Frequency analysis of commit message vocabulary
4. **Author Analysis**: Comparative sentiment analysis across team members

## 7. Applications and Use Cases

### 7.1 Research Applications

CodeMood enables empirical studies in software engineering research:

- **Developer Productivity**: Correlate emotional patterns with code quality metrics
- **Team Dynamics**: Analyze how emotional states affect collaboration
- **Project Management**: Identify stress periods and their impact on delivery
- **Code Quality**: Study the relationship between developer emotions and bug introduction

### 7.2 Industrial Applications

Practical applications in software development organizations:

- **Team Health Monitoring**: Track emotional well-being of development teams
- **Retrospective Analysis**: Use emotional data in sprint retrospectives
- **Project Risk Assessment**: Identify periods of high stress that may impact quality
- **Developer Experience**: Improve tooling and processes based on emotional feedback

### 7.3 Case Study Example

Analysis of a typical React.js project:

```bash
python3 -m cli.main analyze ~/projects/react-app --visualize --limit 200
```

**Results:**

- 156 commits analyzed with 89 comments and 67 functions extracted
- Average sentiment: 0.12 (Joy dominant)
- Sentiment distribution: 45% positive, 35% neutral, 20% negative
- Temporal patterns: Peak frustration during debugging sessions, highest positivity during feature releases

## 8. Future Work and Extensions

### 8.1 Planned Extensions

The current implementation provides a foundation for several extensions:

- **GitHub Action Integration**: Automated analysis of pull requests with mood summaries
- **VSCode Extension**: Real-time emotional feedback during development
- **Web Dashboard**: Team-wide mood monitoring interface
- **Slack Integration**: Daily mood reports and notifications

### 8.2 Research Directions

Potential research extensions:

- **Multi-modal Analysis**: Incorporate code complexity metrics and emotional patterns
- **Predictive Modeling**: Predict project outcomes based on emotional trends
- **Cross-project Analysis**: Compare emotional patterns across different projects
- **Cultural Analysis**: Study how cultural factors influence emotional expression in code

## 9. Contributing

We welcome contributions to CodeMood. Please see our contributing guidelines for:

- Code style and standards
- Testing requirements
- Documentation standards
- Issue reporting procedures

## 10. License

This project is licensed under the MIT License - see the LICENSE file for details.

## 11. Citation

If you use CodeMood in your research, please cite:

```bibtex
@software{codemood2024,
  title={CodeMood: A Sentiment Analysis Framework for Software Development Workflows},
  author={CodeMood Team},
  year={2024},
  url={https://github.com/codemood/codemood}
}
```

---

For more information and examples, visit our [documentation](CLI_USAGE.md) or run `python3 -m cli.main analyze --help`.
