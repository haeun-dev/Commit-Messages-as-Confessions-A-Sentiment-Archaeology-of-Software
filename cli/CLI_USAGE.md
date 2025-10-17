# CodeMood CLI Usage Guide

## Quick Start

The CodeMood CLI analyzes the emotional tone of your Git repository by examining commit messages, comments, and function names.

### Basic Usage

```bash
# Analyze current directory
python3 -m cli.main analyze

# Analyze specific repository with visualizations
python3 -m cli.main analyze ~/projects/my-repo --visualize

# Analyze with custom output directory
python3 -m cli.main analyze . --output-dir ./my_results
```

### Command Line Options

- `analyze` - The main command to analyze repository sentiment
- `repo_path` - Path to git repository (default: current directory)
- `--visualize` - Generate visualizations (creates `codemood_graph.png`)
- `--output-dir` - Output directory for results (default: `./codemood_output`)
- `--limit` - Maximum number of commits to analyze (default: 100)
- `--model` - Sentiment analysis model: `huggingface` or `openai` (default: `huggingface`)
- `--model-name` - Specific model name (optional)
- `--verbose` - Enable verbose logging

### Example Output

```
🔍 Collected 84 commits, 217 comments, 152 functions
🧠 Average sentiment: -0.21 (Frustration dominant)
📈 Visualization: codemood_graph.png generated
```

### Generated Files

- `codemood_report.json` - Comprehensive analysis report
- `codemood_graph.png` - Combined visualization dashboard (if `--visualize` is used)

### Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Run the CLI:
   ```bash
   python3 -m cli.main analyze --help
   ```

### Features

- **Commit Analysis**: Extracts and analyzes commit messages for emotional tone
- **Code Analysis**: Extracts function names and comments from source files
- **Sentiment Analysis**: Uses HuggingFace transformers for emotion detection
- **Visualizations**: Creates timeline, distribution, word cloud, and author analysis
- **JSON Reports**: Detailed analysis results in structured format

### Supported File Types

The tool can extract functions and comments from:

- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`)
- And many more programming languages

### Tips

- Use `--verbose` to see detailed processing information
- Increase `--limit` for repositories with many commits
- The tool automatically filters out merge commits and meaningless messages
- Results are saved in the specified output directory for further analysis
