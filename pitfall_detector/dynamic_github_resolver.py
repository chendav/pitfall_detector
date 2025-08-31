"""Dynamic GitHub URL Resolution using AI-powered search."""

import re
import requests
from typing import Optional, List, Dict, Any
from .config import config


class DynamicGitHubResolver:
    """Resolves GitHub URLs for dynamically detected frameworks using AI search."""
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        self.search_cache = {}
        
    def resolve_github_url(self, framework_info: Dict[str, Any]) -> Optional[str]:
        """
        Resolve GitHub URL for a dynamically detected framework.
        
        Args:
            framework_info: Dictionary containing framework detection info
            
        Returns:
            GitHub URL if found, None otherwise
        """
        framework_name = framework_info.get('name', '').lower()
        
        # Step 1: Check static rules first (current behavior)
        from .static_rules import KNOWN_AI_TOOLS
        if framework_name in KNOWN_AI_TOOLS:
            github_url = KNOWN_AI_TOOLS[framework_name].get('github_url')
            if github_url:
                return github_url
        
        # Step 2: Use suggested search terms from dynamic detection
        suggested_searches = framework_info.get('suggested_github_search', [])
        if suggested_searches:
            return self._search_with_ai_keywords(suggested_searches, framework_name)
        
        # Step 3: Fallback to basic framework name search
        return self._search_github_repositories(framework_name)
    
    def _search_with_ai_keywords(self, search_terms: List[str], framework_name: str) -> Optional[str]:
        """Search GitHub using AI-generated keywords."""
        best_match = None
        highest_score = 0
        
        for search_term in search_terms[:3]:  # Limit to top 3 searches
            if search_term in self.search_cache:
                results = self.search_cache[search_term]
            else:
                results = self._search_github_repositories(search_term)
                self.search_cache[search_term] = results
            
            if results:
                # Score repositories based on relevance to framework name
                for repo in results[:5]:  # Check top 5 results
                    score = self._calculate_relevance_score(repo, framework_name)
                    if score > highest_score:
                        highest_score = score
                        best_match = repo['html_url']
        
        return best_match if highest_score > 0.3 else None
    
    def _search_github_repositories(self, query: str) -> List[Dict]:
        """Search GitHub repositories via API."""
        try:
            # Clean and prepare search query
            clean_query = self._prepare_search_query(query)
            url = f"{self.github_api_base}/search/repositories"
            
            params = {
                'q': clean_query,
                'sort': 'stars', 
                'order': 'desc',
                'per_page': 10
            }
            
            # Add GitHub token if available
            headers = {}
            import os
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 401:
                # Try without authentication for public search
                print(f"  GitHub auth failed, trying public search...")
                response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 403:
                # Rate limited, try a simpler search
                print(f"  Rate limited, trying direct name search...")
                simple_params = {'q': clean_query, 'per_page': 5}
                response = requests.get(url, params=simple_params, timeout=10)
            
            response.raise_for_status()
            
            data = response.json()
            return data.get('items', [])
            
        except Exception as e:
            print(f"  GitHub search failed for '{query}': {e}")
            return []
    
    def _prepare_search_query(self, query: str) -> str:
        """Prepare search query for GitHub API."""
        # Remove special characters, normalize spacing
        clean_query = re.sub(r'[^\w\s-]', ' ', query)
        clean_query = re.sub(r'\s+', ' ', clean_query).strip()
        
        # Add relevant keywords for AI agent frameworks
        if any(keyword in query.lower() for keyword in ['agent', 'framework', 'ai']):
            clean_query += " agent framework"
        
        return clean_query
    
    def _calculate_relevance_score(self, repo: Dict, target_name: str) -> float:
        """Calculate relevance score for a repository match."""
        score = 0.0
        repo_name = repo.get('name', '').lower()
        repo_description = repo.get('description', '').lower() if repo.get('description') else ''
        target_lower = target_name.lower()
        
        # Exact name match gets highest score
        if target_lower == repo_name:
            score += 1.0
        elif target_lower in repo_name or repo_name in target_lower:
            score += 0.7
        
        # Description match
        if target_lower in repo_description:
            score += 0.3
        
        # Keywords match
        agent_keywords = ['agent', 'framework', 'ai', 'llm', 'multi-agent', 'orchestrat']
        for keyword in agent_keywords:
            if keyword in repo_description or keyword in repo_name:
                score += 0.1
        
        # Repository popularity (normalized)
        stars = repo.get('stargazers_count', 0)
        if stars > 100:
            score += min(stars / 10000, 0.2)  # Max 0.2 bonus for popularity
        
        # Recent activity (has recent updates)
        updated_at = repo.get('updated_at', '')
        if updated_at and '2024' in updated_at or '2025' in updated_at:
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _validate_repository(self, github_url: str) -> bool:
        """Validate that the GitHub repository exists and contains agent-related content."""
        try:
            # Extract owner/repo from URL
            match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
            if not match:
                return False
            
            owner, repo = match.groups()
            
            # Check repository exists
            api_url = f"{self.github_api_base}/repos/{owner}/{repo}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                description = repo_data.get('description', '').lower()
                
                # Basic validation for AI/agent related content
                agent_indicators = ['agent', 'ai', 'llm', 'framework', 'orchestrat', 'workflow']
                return any(indicator in description for indicator in agent_indicators)
            
            return False
            
        except Exception:
            return False


def resolve_dynamic_framework_url(framework_info: Dict[str, Any]) -> Optional[str]:
    """Convenience function to resolve GitHub URL for dynamic framework."""
    resolver = DynamicGitHubResolver()
    return resolver.resolve_github_url(framework_info)