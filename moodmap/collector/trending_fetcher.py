"""
GitHub API data collection for trending repositories.
"""

import requests
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging


class TrendingFetcher:
    """Fetch trending repositories from GitHub API."""
    
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        if github_token:
            self.session.headers.update({
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        self.logger = logging.getLogger(__name__)
    
    def get_trending_repositories(self, 
                                language: Optional[str] = None,
                                since: str = "daily",
                                limit: int = 100) -> List[Dict[str, Any]]:
        """Get trending repositories from GitHub."""
        # Note: GitHub doesn't have a direct trending API
        # This is a placeholder for the actual implementation
        # You would need to use GitHub's search API or scrape trending pages
        
        try:
            # Search for repositories with high star counts
            query = f"stars:>1000"
            if language:
                query += f" language:{language}"
            
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': min(limit, 100)  # GitHub API limit
            }
            
            response = self.session.get(f"{self.base_url}/search/repositories", 
                                      params=params)
            response.raise_for_status()
            
            data = response.json()
            repositories = []
            
            for repo in data.get('items', []):
                repositories.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo['description'],
                    'language': repo['language'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'url': repo['html_url'],
                    'clone_url': repo['clone_url']
                })
            
            self.logger.info(f"Fetched {len(repositories)} trending repositories")
            return repositories
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching trending repositories: {e}")
            return []
    
    def get_repository_commits(self, 
                             owner: str, 
                             repo: str, 
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent commits from a repository."""
        try:
            params = {
                'per_page': min(limit, 100),
                'page': 1
            }
            
            response = self.session.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits",
                params=params
            )
            response.raise_for_status()
            
            commits = []
            for commit_data in response.json():
                commit = commit_data['commit']
                commits.append({
                    'sha': commit_data['sha'],
                    'message': commit['message'],
                    'author': {
                        'name': commit['author']['name'],
                        'email': commit['author']['email'],
                        'date': commit['author']['date']
                    },
                    'committer': {
                        'name': commit['committer']['name'],
                        'email': commit['committer']['email'],
                        'date': commit['committer']['date']
                    },
                    'url': commit_data['html_url']
                })
            
            self.logger.info(f"Fetched {len(commits)} commits from {owner}/{repo}")
            return commits
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching commits from {owner}/{repo}: {e}")
            return []
    
    def get_repository_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get language statistics for a repository."""
        try:
            response = self.session.get(
                f"{self.base_url}/repos/{owner}/{repo}/languages"
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching languages from {owner}/{repo}: {e}")
            return {}
    
    def get_repository_contributors(self, 
                                  owner: str, 
                                  repo: str, 
                                  limit: int = 30) -> List[Dict[str, Any]]:
        """Get contributors for a repository."""
        try:
            params = {
                'per_page': min(limit, 100),
                'page': 1
            }
            
            response = self.session.get(
                f"{self.base_url}/repos/{owner}/{repo}/contributors",
                params=params
            )
            response.raise_for_status()
            
            contributors = []
            for contributor in response.json():
                contributors.append({
                    'login': contributor['login'],
                    'id': contributor['id'],
                    'contributions': contributor['contributions'],
                    'avatar_url': contributor['avatar_url'],
                    'html_url': contributor['html_url']
                })
            
            return contributors
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching contributors from {owner}/{repo}: {e}")
            return []
    
    def batch_fetch_repository_data(self, 
                                  repositories: List[Dict[str, Any]], 
                                  max_commits_per_repo: int = 50) -> List[Dict[str, Any]]:
        """Fetch comprehensive data for multiple repositories."""
        enriched_repos = []
        
        for i, repo in enumerate(repositories):
            self.logger.info(f"Processing repository {i+1}/{len(repositories)}: {repo['full_name']}")
            
            # Parse owner and repo name
            owner, repo_name = repo['full_name'].split('/', 1)
            
            # Fetch additional data
            commits = self.get_repository_commits(owner, repo_name, max_commits_per_repo)
            languages = self.get_repository_languages(owner, repo_name)
            contributors = self.get_repository_contributors(owner, repo_name)
            
            # Enrich repository data
            enriched_repo = {
                **repo,
                'commits': commits,
                'languages': languages,
                'contributors': contributors,
                'primary_language': max(languages.items(), key=lambda x: x[1])[0] if languages else None
            }
            
            enriched_repos.append(enriched_repo)
            
            # Rate limiting - GitHub allows 5000 requests per hour for authenticated users
            time.sleep(0.1)  # Small delay to be respectful
        
        return enriched_repos
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Check GitHub API rate limit status."""
        try:
            response = self.session.get(f"{self.base_url}/rate_limit")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error checking rate limit: {e}")
            return {}
