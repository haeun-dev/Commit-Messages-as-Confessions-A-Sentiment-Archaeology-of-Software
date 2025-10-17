#!/bin/bash

# GitHub Action entrypoint script for CodeMood

set -e

echo "Starting CodeMood analysis..."

# Set default values
REPO_PATH="${INPUT_REPO_PATH:-.}"
OUTPUT_DIR="${INPUT_OUTPUT_DIR:-./codemood_output}"
LIMIT="${INPUT_LIMIT:-100}"
MODEL="${INPUT_MODEL:-huggingface}"
MODEL_NAME="${INPUT_MODEL_NAME:-}"
VERBOSE="${INPUT_VERBOSE:-false}"

# Build command arguments
ARGS="analyze --repo-path $REPO_PATH --output-dir $OUTPUT_DIR --limit $LIMIT --model $MODEL"

if [ -n "$MODEL_NAME" ]; then
    ARGS="$ARGS --model-name $MODEL_NAME"
fi

if [ "$VERBOSE" = "true" ]; then
    ARGS="$ARGS --verbose"
fi

# Run the analysis
echo "Running: python -m cli.main $ARGS"
python -m cli.main $ARGS

# Set outputs
echo "summary-path=$OUTPUT_DIR/summary.txt" >> $GITHUB_OUTPUT
echo "timeline-path=$OUTPUT_DIR/sentiment_timeline.png" >> $GITHUB_OUTPUT
echo "distribution-path=$OUTPUT_DIR/sentiment_distribution.png" >> $GITHUB_OUTPUT
echo "wordcloud-path=$OUTPUT_DIR/word_cloud.png" >> $GITHUB_OUTPUT
echo "heatmap-path=$OUTPUT_DIR/author_sentiment_heatmap.png" >> $GITHUB_OUTPUT

echo "CodeMood analysis completed successfully!"
