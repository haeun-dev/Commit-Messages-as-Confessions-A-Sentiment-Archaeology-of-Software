import * as vscode from 'vscode';
import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execAsync = promisify(exec);

export function activate(context: vscode.ExtensionContext) {
    console.log('CodeMood extension is now active!');

    // Register the analyze command
    const analyzeCommand = vscode.commands.registerCommand('codemood.analyze', async () => {
        await analyzeCodeMood();
    });

    // Register the view provider
    const provider = new CodeMoodViewProvider(context.extensionUri);
    vscode.window.registerTreeDataProvider('codemoodView', provider);

    context.subscriptions.push(analyzeCommand);
}

async function analyzeCodeMood() {
    try {
        // Get the current workspace folder
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('No workspace folder found');
            return;
        }

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing Code Mood",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0, message: "Starting analysis..." });

            // Run the codemood analysis
            const outputDir = path.join(workspaceFolder.uri.fsPath, 'codemood_output');
            const command = `python -m cli.main analyze --repo-path "${workspaceFolder.uri.fsPath}" --output-dir "${outputDir}" --limit 50`;

            progress.report({ increment: 30, message: "Extracting git data..." });
            
            try {
                const { stdout, stderr } = await execAsync(command, {
                    cwd: workspaceFolder.uri.fsPath
                });

                progress.report({ increment: 70, message: "Generating visualizations..." });

                if (stderr) {
                    console.warn('Analysis warnings:', stderr);
                }

                progress.report({ increment: 100, message: "Analysis complete!" });

                // Show results
                vscode.window.showInformationMessage(
                    'CodeMood analysis completed! Check the output folder for results.',
                    'Open Results'
                ).then(selection => {
                    if (selection === 'Open Results') {
                        vscode.commands.executeCommand('vscode.openFolder', vscode.Uri.file(outputDir));
                    }
                });

            } catch (error: any) {
                vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
                console.error('Analysis error:', error);
            }
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to analyze code mood: ${error.message}`);
    }
}

class CodeMoodViewProvider implements vscode.TreeDataProvider<CodeMoodItem> {
    constructor(private extensionUri: vscode.Uri) {}

    getTreeItem(element: CodeMoodItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: CodeMoodItem): Thenable<CodeMoodItem[]> {
        if (!element) {
            return Promise.resolve([
                new CodeMoodItem('Analyze Repository', vscode.TreeItemCollapsibleState.None, {
                    command: 'codemood.analyze',
                    title: 'Analyze Code Mood'
                })
            ]);
        }
        return Promise.resolve([]);
    }
}

class CodeMoodItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly command?: vscode.Command
    ) {
        super(label, collapsibleState);
    }
}

export function deactivate() {}
