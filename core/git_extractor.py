"""
Git log, comments, function names, and timezone data extraction.
"""

import subprocess
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class GitExtractor:
    """Extract git information for sentiment analysis."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        
    def get_commit_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Extract commit messages with metadata."""
        try:
            cmd = [
                "git", "log", 
                f"--max-count={limit}",
                "--pretty=format:%H|%an|%ae|%ad|%s",
                "--date=iso"
            ]
            result = subprocess.run(cmd, cwd=self.repo_path, 
                                  capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) == 5:
                        commits.append({
                            'hash': parts[0],
                            'author': parts[1],
                            'email': parts[2],
                            'date': parts[3],
                            'message': parts[4]
                        })
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error extracting git commits: {e}")
            return []
    
    def get_file_changes(self, commit_hash: str) -> List[Dict[str, Any]]:
        """Get file changes for a specific commit."""
        try:
            cmd = ["git", "show", "--name-status", "--pretty=format:", commit_hash]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            
            changes = []
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('commit'):
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        changes.append({
                            'status': parts[0],
                            'file': parts[1]
                        })
            return changes
        except subprocess.CalledProcessError as e:
            print(f"Error getting file changes: {e}")
            return []
    
    def get_function_names(self, file_path: str) -> List[str]:
        """Extract function names from a file."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return []
            
            extension = file_path_obj.suffix.lower()
            functions = []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if extension == '.py':
                # Python function patterns
                import re
                patterns = [
                    r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript function patterns
                import re
                patterns = [
                    r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(',
                    r'const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?\(',
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s+)?\(',
                    r'class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.java', '.c', '.cpp', '.h']:
                # C/C++/Java function patterns
                import re
                patterns = [
                    r'(?:public|private|protected)?\s*(?:static\s+)?(?:[a-zA-Z_][a-zA-Z0-9_]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            return list(set(functions))  # Remove duplicates
            
        except Exception as e:
            print(f"Error extracting functions from {file_path}: {e}")
            return []
    
    def get_commit_timezone(self, commit_hash: str) -> Optional[str]:
        """Get timezone information for a commit."""
        try:
            cmd = ["git", "show", "-s", "--format=%ci", commit_hash]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_comments_from_file(self, file_path: str) -> List[str]:
        """Extract comments from a file."""
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return []
            
            extension = file_path_obj.suffix.lower()
            comments = []
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            if extension == '.py':
                # Python comments
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:  # Skip very short comments
                            comments.append(comment)
            
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript comments
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            elif extension in ['.java', '.c', '.cpp', '.h']:
                # C/C++/Java comments
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            return comments
            
        except Exception as e:
            print(f"Error extracting comments from {file_path}: {e}")
            return []
    
    def get_repository_stats(self) -> Dict[str, Any]:
        """Get overall repository statistics."""
        try:
            # Get total commits
            cmd = ["git", "rev-list", "--count", "HEAD"]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            total_commits = int(result.stdout.strip())
            
            # Get total files
            cmd = ["git", "ls-files"]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            total_files = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            # Get repository size
            cmd = ["du", "-sh", "."]
            result = subprocess.run(cmd, cwd=self.repo_path,
                                  capture_output=True, text=True, check=True)
            repo_size = result.stdout.strip().split('\t')[0]
            
            return {
                'total_commits': total_commits,
                'total_files': total_files,
                'repository_size': repo_size,
                'repository_path': str(self.repo_path)
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting repository stats: {e}")
            return {
                'total_commits': 0,
                'total_files': 0,
                'repository_size': 'Unknown',
                'repository_path': str(self.repo_path)
            }
    
    def is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file based on extension."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.r', '.m', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1',
            '.sql', '.html', '.css', '.scss', '.sass', '.less', '.vue',
            '.svelte', '.dart', '.lua', '.vim', '.yaml', '.yml', '.json',
            '.xml', '.toml', '.ini', '.cfg', '.conf'
        }
        return Path(file_path).suffix.lower() in code_extensions
