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
            
            import re
            
            if extension == '.py':
                # Python function patterns
                patterns = [
                    r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]',
                    r'async\s+def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript function patterns
                patterns = [
                    r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(',
                    r'const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s+)?\(',
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*(?:async\s+)?\(',
                    r'class\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*[\(\{]',
                    r'export\s+(?:default\s+)?(?:async\s+)?function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(',
                    r'export\s+const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.java', '.c', '.cpp', '.h', '.hpp']:
                # C/C++/Java function patterns
                patterns = [
                    r'(?:public|private|protected)?\s*(?:static\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>,\s]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'interface\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'enum\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.go':
                # Go function patterns
                patterns = [
                    r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'func\s+\([^)]*\)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'type\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:struct|interface)',
                    r'func\s+\([^)]*\)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*[a-zA-Z_][a-zA-Z0-9_]*',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.rs':
                # Rust function patterns
                patterns = [
                    r'fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'impl\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'struct\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'enum\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'trait\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.cs':
                # C# function patterns
                patterns = [
                    r'(?:public|private|protected|internal)?\s*(?:static\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>,\s]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'interface\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'struct\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'enum\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.php':
                # PHP function patterns
                patterns = [
                    r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'interface\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'trait\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'public\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'private\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'protected\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.rb':
                # Ruby function patterns
                patterns = [
                    r'def\s+([a-zA-Z_][a-zA-Z0-9_?!]*)\s*[\(\)]?',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'module\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'def\s+self\.([a-zA-Z_][a-zA-Z0-9_?!]*)\s*[\(\)]?',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.swift':
                # Swift function patterns
                patterns = [
                    r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'struct\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'enum\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'protocol\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'extension\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.kt':
                # Kotlin function patterns
                patterns = [
                    r'fun\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'interface\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'data\s+class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'object\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'enum\s+class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.scala':
                # Scala function patterns
                patterns = [
                    r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'object\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'trait\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'case\s+class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.r':
                # R function patterns
                patterns = [
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*<-\s*function\s*\(',
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function\s*\(',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.m':
                # MATLAB/Objective-C function patterns
                patterns = [
                    r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\)]',
                    r'-?\s*\([^)]*\)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'@interface\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'@implementation\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.pl':
                # Perl function patterns
                patterns = [
                    r'sub\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'package\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.sh', '.bash', '.zsh', '.fish']:
                # Shell script function patterns
                patterns = [
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(\s*\)\s*[\(\{]',
                    r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.ps1':
                # PowerShell function patterns
                patterns = [
                    r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.sql':
                # SQL function patterns
                patterns = [
                    r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'CREATE\s+(?:OR\s+REPLACE\s+)?PROCEDURE\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                    r'CREATE\s+TRIGGER\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.html', '.htm']:
                # HTML function patterns (for embedded JavaScript)
                patterns = [
                    r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(',
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:\s*function\s*\(',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension in ['.vue', '.svelte']:
                # Vue.js and Svelte function patterns
                patterns = [
                    r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(',
                    r'const\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*\([^)]*\)\s*=>',
                    r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*=>',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.dart':
                # Dart function patterns
                patterns = [
                    r'(?:[a-zA-Z_][a-zA-Z0-9_<>,\s]*\s+)*([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*[\(\{]',
                    r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                    r'abstract\s+class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(\{]',
                ]
                for pattern in patterns:
                    matches = re.findall(pattern, content)
                    functions.extend(matches)
            
            elif extension == '.lua':
                # Lua function patterns
                patterns = [
                    r'function\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s*\(',
                    r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function\s*\(',
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
            
            # Languages that use # for comments
            if extension in ['.py', '.rb', '.r', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.yaml', '.yml']:
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:  # Skip very short comments
                            comments.append(comment)
            
            # Languages that use // for single-line comments
            elif extension in ['.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs', '.kt', '.swift', '.dart', '.scala', '.m']:
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Languages that use -- for comments
            elif extension in ['.sql', '.lua', '.hs']:  # SQL, Lua, Haskell
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('--'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Languages that use % for comments
            elif extension in ['.m', '.matlab']:  # MATLAB
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('%'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Languages that use <!-- --> for comments (HTML, XML)
            elif extension in ['.html', '.htm', '.xml', '.vue', '.svelte']:
                import re
                # Extract HTML/XML comments
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                html_comments = re.findall(r'<!--\s*(.*?)\s*-->', content, re.DOTALL)
                for comment in html_comments:
                    comment = comment.strip()
                    if comment and len(comment) > 3:
                        comments.append(comment)
                
                # Also extract JavaScript comments in script tags
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Languages that use /* */ for multi-line comments
            elif extension in ['.c', '.cpp', '.h', '.hpp', '.java', '.js', '.ts', '.jsx', '.tsx', '.cs', '.php', '.scala', '.swift', '.kt', '.dart']:
                import re
                # Extract multi-line comments
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                multiline_comments = re.findall(r'/\*\s*(.*?)\s*\*/', content, re.DOTALL)
                for comment in multiline_comments:
                    # Split multi-line comments into individual lines
                    for line in comment.split('\n'):
                        line = line.strip()
                        if line and len(line) > 3:
                            comments.append(line)
            
            # PHP specific comments
            elif extension == '.php':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//') or stripped.startswith('#'):
                        comment = stripped[2:].strip() if stripped.startswith('//') else stripped[1:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Ruby specific comments
            elif extension == '.rb':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Go specific comments
            elif extension == '.go':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Rust specific comments
            elif extension == '.rs':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # C# specific comments
            elif extension == '.cs':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Swift specific comments
            elif extension == '.swift':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Kotlin specific comments
            elif extension == '.kt':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Scala specific comments
            elif extension == '.scala':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Dart specific comments
            elif extension == '.dart':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Lua specific comments
            elif extension == '.lua':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('--'):
                        comment = stripped[2:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Perl specific comments
            elif extension == '.pl':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # Shell script specific comments
            elif extension in ['.sh', '.bash', '.zsh', '.fish']:
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # PowerShell specific comments
            elif extension == '.ps1':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()
                        if comment and len(comment) > 3:
                            comments.append(comment)
            
            # SQL specific comments
            elif extension == '.sql':
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('--'):
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
            # Core languages
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.r', '.m', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1',
            '.sql', '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue',
            '.svelte', '.dart', '.lua', '.vim', '.yaml', '.yml', '.json',
            '.xml', '.toml', '.ini', '.cfg', '.conf',
            # Additional languages
            '.hs', '.elm', '.ex', '.exs', '.erl', '.hrl', '.clj', '.cljs',
            '.fs', '.fsx', '.ml', '.mli', '.nim', '.zig', '.v', '.cr', '.jl',
            # Web technologies
            '.astro',
            # Configuration files
            '.env', '.properties', '.gradle', '.maven', '.pom'
        }
        return Path(file_path).suffix.lower() in code_extensions
