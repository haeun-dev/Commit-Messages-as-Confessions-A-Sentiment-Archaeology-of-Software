"""
Common utility functions for path handling, time formatting, and logging.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


def setup_logger(name: str, level: int = logging.INFO, 
                log_file: Optional[str] = None) -> logging.Logger:
    """Set up a logger with console and optional file output."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def format_timestamp(timestamp: str, format_type: str = "human") -> str:
    """Format timestamp for display."""
    try:
        # Parse ISO format timestamp
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        if format_type == "human":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        elif format_type == "iso":
            return dt.isoformat()
        elif format_type == "date":
            return dt.strftime("%Y-%m-%d")
        elif format_type == "time":
            return dt.strftime("%H:%M:%S")
        else:
            return str(dt)
    except Exception:
        return timestamp


def ensure_directory(path: str) -> Path:
    """Ensure a directory exists, create if it doesn't."""
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "pyproject.toml").exists() or (current / "README.md").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing config file {config_path}: {e}")
        return {}


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """Save configuration to JSON file."""
    ensure_directory(os.path.dirname(config_path))
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_file_extension(file_path: str) -> str:
    """Get file extension from path."""
    return Path(file_path).suffix.lower()


def is_code_file(file_path: str) -> bool:
    """Check if file is a code file based on extension."""
    code_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
        '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
        '.r', '.m', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1',
        '.sql', '.html', '.css', '.scss', '.sass', '.less', '.vue',
        '.svelte', '.dart', '.lua', '.vim', '.yaml', '.yml', '.json',
        '.xml', '.toml', '.ini', '.cfg', '.conf'
    }
    return get_file_extension(file_path) in code_extensions


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def safe_filename(filename: str) -> str:
    """Convert string to safe filename."""
    import re
    # Remove or replace invalid characters
    safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    safe = re.sub(r'_+', '_', safe)
    # Remove leading/trailing underscores
    safe = safe.strip('_')
    return safe or 'unnamed'


def get_relative_path(file_path: str, base_path: str) -> str:
    """Get relative path from base path."""
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        return file_path


def validate_git_repo(path: str) -> bool:
    """Check if path is a valid git repository."""
    git_dir = Path(path) / ".git"
    return git_dir.exists() and git_dir.is_dir()


def get_git_remote_url(repo_path: str = ".") -> Optional[str]:
    """Get the remote URL of a git repository."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
