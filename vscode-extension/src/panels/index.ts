// VSCode extension panels for CodeMood
// This file will contain UI components for displaying analysis results

export interface AnalysisResult {
    totalCommits: number;
    sentimentDistribution: {
        positive: number;
        neutral: number;
        negative: number;
    };
    averageConfidence: number;
    topPositiveCommits: string[];
    topNegativeCommits: string[];
}

export class CodeMoodPanel {
    private panel: vscode.WebviewPanel;
    private extensionUri: vscode.Uri;

    constructor(extensionUri: vscode.Uri) {
        this.extensionUri = extensionUri;
        this.panel = vscode.window.createWebviewPanel(
            'codemoodResults',
            'Code Mood Analysis',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [vscode.Uri.joinPath(extensionUri, 'media')]
            }
        );
    }

    public updateContent(result: AnalysisResult) {
        this.panel.webview.html = this.getWebviewContent(result);
    }

    private getWebviewContent(result: AnalysisResult): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Mood Analysis</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                    background-color: var(--vscode-editor-background);
                    padding: 20px;
                }
                .summary {
                    background-color: var(--vscode-editor-background);
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    padding: 20px;
                    margin-bottom: 20px;
                }
                .metric {
                    display: inline-block;
                    margin: 10px 20px 10px 0;
                }
                .metric-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: var(--vscode-textLink-foreground);
                }
                .metric-label {
                    font-size: 12px;
                    color: var(--vscode-descriptionForeground);
                }
                .sentiment-bar {
                    display: flex;
                    height: 20px;
                    border-radius: 10px;
                    overflow: hidden;
                    margin: 10px 0;
                }
                .sentiment-positive { background-color: #2E8B57; }
                .sentiment-neutral { background-color: #FFD700; }
                .sentiment-negative { background-color: #DC143C; }
                .commits-list {
                    max-height: 200px;
                    overflow-y: auto;
                    border: 1px solid var(--vscode-panel-border);
                    border-radius: 4px;
                    padding: 10px;
                }
                .commit-item {
                    padding: 5px 0;
                    border-bottom: 1px solid var(--vscode-panel-border);
                }
                .commit-item:last-child {
                    border-bottom: none;
                }
            </style>
        </head>
        <body>
            <h1>Code Mood Analysis Results</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="metric">
                    <div class="metric-value">${result.totalCommits}</div>
                    <div class="metric-label">Total Commits</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${result.averageConfidence.toFixed(2)}</div>
                    <div class="metric-label">Avg Confidence</div>
                </div>
                
                <h3>Sentiment Distribution</h3>
                <div class="sentiment-bar">
                    <div class="sentiment-positive" style="width: ${(result.sentimentDistribution.positive / result.totalCommits) * 100}%"></div>
                    <div class="sentiment-neutral" style="width: ${(result.sentimentDistribution.neutral / result.totalCommits) * 100}%"></div>
                    <div class="sentiment-negative" style="width: ${(result.sentimentDistribution.negative / result.totalCommits) * 100}%"></div>
                </div>
                <p>
                    Positive: ${result.sentimentDistribution.positive} | 
                    Neutral: ${result.sentimentDistribution.neutral} | 
                    Negative: ${result.sentimentDistribution.negative}
                </p>
            </div>
            
            <div class="summary">
                <h2>Top Positive Commits</h2>
                <div class="commits-list">
                    ${result.topPositiveCommits.map(commit => `<div class="commit-item">${commit}</div>`).join('')}
                </div>
            </div>
            
            <div class="summary">
                <h2>Top Negative Commits</h2>
                <div class="commits-list">
                    ${result.topNegativeCommits.map(commit => `<div class="commit-item">${commit}</div>`).join('')}
                </div>
            </div>
        </body>
        </html>`;
    }
}
