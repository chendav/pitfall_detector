"""GitHub API integration for fetching tool documentation."""

import re
import requests
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from .config import config


class GitHubClient:
    """Client for interacting with GitHub API to fetch tool documentation."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        # Add GitHub token if available for higher rate limits
        github_token = config.get('github.token')
        if github_token:
            self.session.headers.update({
                'Authorization': f'token {github_token}'
            })
        
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'ai-pitfall-detector/0.1.0'
        })
        
        self.timeout = config.get('github.timeout', 30)
    
    def parse_github_url(self, url: str) -> Optional[Tuple[str, str]]:
        """
        Parse GitHub URL to extract owner and repo.
        
        Args:
            url: GitHub URL (various formats supported)
            
        Returns:
            Tuple of (owner, repo) or None if invalid
        """
        # Clean up the URL
        url = url.strip().rstrip('/')
        
        # Handle different URL formats
        patterns = [
            r'github\.com/([^/]+)/([^/]+)',  # Standard format
            r'github\.com/([^/]+)/([^/]+)\.git',  # Git clone format
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                owner, repo = match.groups()
                # Remove .git suffix if present
                repo = repo.replace('.git', '')
                return owner, repo
        
        return None
    
    def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        Fetch README content from a GitHub repository.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content as string or None if not found
        """
        try:
            # Try common README filenames
            readme_files = ['README.md', 'README.txt', 'README.rst', 'README']
            
            for readme_file in readme_files:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{readme_file}"
                
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    content_data = response.json()
                    
                    # GitHub API returns base64 encoded content
                    if content_data.get('encoding') == 'base64':
                        import base64
                        content = base64.b64decode(content_data['content']).decode('utf-8')
                        return content
                    else:
                        return content_data.get('content', '')
            
            return None
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch README from {owner}/{repo}: {e}")
        except Exception as e:
            raise Exception(f"Error processing README from {owner}/{repo}: {e}")
    
    def get_repo_info(self, owner: str, repo: str) -> Optional[Dict]:
        """
        Get basic repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository info dict or None if not found
        """
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    'name': repo_data.get('name'),
                    'full_name': repo_data.get('full_name'),
                    'description': repo_data.get('description'),
                    'language': repo_data.get('language'),
                    'stars': repo_data.get('stargazers_count'),
                    'forks': repo_data.get('forks_count'),
                    'topics': repo_data.get('topics', []),
                    'url': repo_data.get('html_url'),
                    'private': repo_data.get('private', False)
                }
            elif response.status_code == 404:
                return None
            else:
                response.raise_for_status()
                
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch repo info for {owner}/{repo}: {e}")
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate if a GitHub URL is accessible.
        
        Args:
            url: GitHub URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parsed = self.parse_github_url(url)
            if not parsed:
                return False, "Invalid GitHub URL format"
            
            owner, repo = parsed
            repo_info = self.get_repo_info(owner, repo)
            
            if repo_info is None:
                return False, f"Repository {owner}/{repo} not found or private"
            
            if repo_info.get('private', False):
                return False, f"Repository {owner}/{repo} is private"
            
            return True, ""
            
        except Exception as e:
            return False, str(e)


class ToolExtractor:
    """Extract tool information from GitHub repositories."""
    
    def __init__(self, github_client: GitHubClient):
        self.github = github_client
    
    def extract_tool_info(self, url: str) -> Dict:
        """
        Extract comprehensive tool information from a GitHub URL.
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Dict containing tool information
        """
        parsed = self.github.parse_github_url(url)
        if not parsed:
            raise ValueError(f"Invalid GitHub URL: {url}")
        
        owner, repo = parsed
        
        # Get repository info
        repo_info = self.github.get_repo_info(owner, repo)
        if not repo_info:
            raise Exception(f"Repository {owner}/{repo} not found")
        
        # Get README content
        readme_content = self.github.get_readme(owner, repo)
        
        # Extract tool metadata
        tool_info = {
            'name': repo_info['name'],
            'full_name': repo_info['full_name'],
            'url': url,
            'description': repo_info.get('description', ''),
            'language': repo_info.get('language', ''),
            'stars': repo_info.get('stars', 0),
            'topics': repo_info.get('topics', []),
            'readme': readme_content or '',
            'metadata': self._extract_metadata(readme_content or '')
        }
        
        return tool_info
    
    def _extract_metadata(self, readme_content: str) -> Dict:
        """
        Extract metadata from README content.
        
        Args:
            readme_content: README file content
            
        Returns:
            Dict containing extracted metadata
        """
        metadata = {
            'installation_methods': [],
            'dependencies': [],
            'ports': [],
            'environment_vars': [],
            'config_files': [],
            'categories': []
        }
        
        if not readme_content:
            return metadata
        
        # Extract installation methods
        if re.search(r'pip install', readme_content, re.IGNORECASE):
            metadata['installation_methods'].append('pip')
        if re.search(r'conda install', readme_content, re.IGNORECASE):
            metadata['installation_methods'].append('conda')
        if re.search(r'npm install', readme_content, re.IGNORECASE):
            metadata['installation_methods'].append('npm')
        if re.search(r'docker', readme_content, re.IGNORECASE):
            metadata['installation_methods'].append('docker')
        
        # Extract common ports
        port_patterns = [
            r':(\d{4,5})',  # :8000, :3000, etc.
            r'port[:\s]+(\d{4,5})',  # port: 8000
            r'localhost:(\d{4,5})',  # localhost:8000
        ]
        
        for pattern in port_patterns:
            matches = re.findall(pattern, readme_content, re.IGNORECASE)
            for match in matches:
                port = int(match)
                if 1000 <= port <= 65535 and port not in metadata['ports']:
                    metadata['ports'].append(port)
        
        # Extract environment variables
        env_patterns = [
            r'([A-Z_][A-Z0-9_]*_API_KEY)',  # API_KEY variables
            r'([A-Z_][A-Z0-9_]*_TOKEN)',    # TOKEN variables
            r'export ([A-Z_][A-Z0-9_]*)',   # export statements
            r'\$([A-Z_][A-Z0-9_]*)',        # $VARIABLE references
        ]
        
        for pattern in env_patterns:
            matches = re.findall(pattern, readme_content)
            for match in matches:
                if match not in metadata['environment_vars']:
                    metadata['environment_vars'].append(match)
        
        # Categorize tool type
        content_lower = readme_content.lower()
        
        if any(word in content_lower for word in ['agent', 'multi-agent', 'crew']):
            metadata['categories'].append('agent-framework')
        if any(word in content_lower for word in ['llm', 'language model', 'gpt', 'claude']):
            metadata['categories'].append('llm-interface')
        if any(word in content_lower for word in ['rag', 'retrieval', 'vector', 'embedding']):
            metadata['categories'].append('rag-tool')
        if any(word in content_lower for word in ['memory', 'context', 'conversation']):
            metadata['categories'].append('memory-management')
        if any(word in content_lower for word in ['streamlit', 'gradio', 'web', 'ui']):
            metadata['categories'].append('web-interface')
        
        return metadata