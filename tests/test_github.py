"""Tests for GitHub integration."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pitfall_detector.github import GitHubClient, ToolExtractor


class TestGitHubClient:
    """Test the GitHubClient class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = GitHubClient()
    
    def test_parse_github_url_standard(self):
        """Test parsing standard GitHub URLs."""
        test_cases = [
            ("https://github.com/owner/repo", ("owner", "repo")),
            ("https://github.com/owner/repo.git", ("owner", "repo")),
            ("github.com/owner/repo", ("owner", "repo")),
            ("github.com/owner/repo/", ("owner", "repo")),
        ]
        
        for url, expected in test_cases:
            result = self.client.parse_github_url(url)
            assert result == expected
    
    def test_parse_github_url_invalid(self):
        """Test parsing invalid GitHub URLs."""
        invalid_urls = [
            "not-a-url",
            "https://gitlab.com/owner/repo",
            "https://github.com/owner",
            "",
        ]
        
        for url in invalid_urls:
            result = self.client.parse_github_url(url)
            assert result is None
    
    @patch('requests.Session.get')
    def test_get_readme_success(self, mock_get):
        """Test successful README fetching."""
        import base64
        
        # Mock successful response
        readme_content = "# Test README\nThis is a test."
        encoded_content = base64.b64encode(readme_content.encode('utf-8')).decode('utf-8')
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'content': encoded_content,
            'encoding': 'base64'
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_readme("owner", "repo")
        assert result == readme_content
    
    @patch('requests.Session.get')
    def test_get_readme_not_found(self, mock_get):
        """Test README not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.client.get_readme("owner", "repo")
        assert result is None
    
    @patch('requests.Session.get')
    def test_get_repo_info_success(self, mock_get):
        """Test successful repository info fetching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test-repo',
            'full_name': 'owner/test-repo',
            'description': 'A test repository',
            'language': 'Python',
            'stargazers_count': 100,
            'forks_count': 20,
            'topics': ['ai', 'ml'],
            'html_url': 'https://github.com/owner/test-repo',
            'private': False
        }
        mock_get.return_value = mock_response
        
        result = self.client.get_repo_info("owner", "test-repo")
        
        assert result['name'] == 'test-repo'
        assert result['stars'] == 100
        assert result['topics'] == ['ai', 'ml']
        assert result['private'] is False
    
    @patch('requests.Session.get')
    def test_get_repo_info_not_found(self, mock_get):
        """Test repository not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.client.get_repo_info("owner", "nonexistent")
        assert result is None
    
    def test_validate_url_invalid_format(self):
        """Test URL validation with invalid format."""
        is_valid, error = self.client.validate_url("invalid-url")
        assert not is_valid
        assert "Invalid GitHub URL format" in error


class TestToolExtractor:
    """Test the ToolExtractor class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.github_client = Mock(spec=GitHubClient)
        self.extractor = ToolExtractor(self.github_client)
    
    def test_extract_metadata_pip_install(self):
        """Test metadata extraction for pip installation."""
        readme_content = """
        # Test Tool
        
        Install with pip:
        ```
        pip install test-tool
        ```
        
        Uses port 8000 by default.
        Set OPENAI_API_KEY environment variable.
        """
        
        metadata = self.extractor._extract_metadata(readme_content)
        
        assert 'pip' in metadata['installation_methods']
        assert 8000 in metadata['ports']
        assert 'OPENAI_API_KEY' in metadata['environment_vars']
    
    def test_extract_metadata_categorization(self):
        """Test tool categorization."""
        test_cases = [
            ("This is an agent framework for multi-agent systems", ['agent-framework']),
            ("LLM interface for GPT models", ['llm-interface']),
            ("RAG tool with vector embeddings", ['rag-tool']),
            ("Memory management for conversations", ['memory-management']),
            ("Streamlit web interface", ['web-interface']),
        ]
        
        for content, expected_categories in test_cases:
            metadata = self.extractor._extract_metadata(content)
            for category in expected_categories:
                assert category in metadata['categories']
    
    def test_extract_tool_info_success(self):
        """Test successful tool information extraction."""
        # Mock GitHub client responses
        self.github_client.parse_github_url.return_value = ("owner", "repo")
        self.github_client.get_repo_info.return_value = {
            'name': 'test-tool',
            'full_name': 'owner/test-tool',
            'description': 'A test tool',
            'language': 'Python',
            'stars': 50,
            'topics': ['ai']
        }
        self.github_client.get_readme.return_value = "# Test Tool\npip install test-tool"
        
        result = self.extractor.extract_tool_info("https://github.com/owner/repo")
        
        assert result['name'] == 'test-tool'
        assert result['description'] == 'A test tool'
        assert result['language'] == 'Python'
        assert result['stars'] == 50
        assert 'metadata' in result
    
    def test_extract_tool_info_invalid_url(self):
        """Test tool extraction with invalid URL."""
        self.github_client.parse_github_url.return_value = None
        
        with pytest.raises(ValueError, match="Invalid GitHub URL"):
            self.extractor.extract_tool_info("invalid-url")
    
    def test_extract_tool_info_repo_not_found(self):
        """Test tool extraction when repository is not found."""
        self.github_client.parse_github_url.return_value = ("owner", "repo")
        self.github_client.get_repo_info.return_value = None
        
        with pytest.raises(Exception, match="Repository .* not found"):
            self.extractor.extract_tool_info("https://github.com/owner/repo")