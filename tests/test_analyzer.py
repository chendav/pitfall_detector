"""Tests for AI conflict analyzer."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pitfall_detector.analyzer import ConflictAnalyzer, ConflictTypes, Severity


class TestConflictAnalyzer:
    """Test the ConflictAnalyzer class."""
    
    def setup_method(self):
        """Set up test environment."""
        with patch('pitfall_detector.analyzer.openai.OpenAI'):
            with patch('pitfall_detector.config.config.get_api_key', return_value='test-key'):
                self.analyzer = ConflictAnalyzer()
    
    def test_analyze_single_tool(self):
        """Test analysis with only one tool (should return no conflicts)."""
        tools = [{'name': 'single-tool', 'readme': 'A single tool'}]
        
        result = self.analyzer.analyze_tool_conflicts(tools)
        
        assert result['tool_count'] == 1
        assert len(result['conflicts']) == 0
        assert 'Need at least 2 tools' in result['summary']
    
    def test_create_tool_summary(self):
        """Test tool summary creation."""
        tool = {
            'name': 'test-tool',
            'description': 'A test tool',
            'metadata': {
                'categories': ['agent-framework'],
                'installation_methods': ['pip'],
                'ports': [8000],
                'environment_vars': ['API_KEY']
            },
            'readme': 'This is a long readme content that should be truncated properly for analysis...' * 100
        }
        
        summary = self.analyzer._create_tool_summary(tool)
        
        assert 'test-tool' in summary
        assert 'agent-framework' in summary
        assert 'pip' in summary
        assert '8000' in summary
        assert 'API_KEY' in summary
    
    def test_extract_readme_excerpt(self):
        """Test README excerpt extraction."""
        readme = """
        # Test Tool
        
        Some intro text.
        
        ## Installation
        
        pip install test-tool
        
        ## Configuration
        
        Set the following environment variables:
        - API_KEY=your_key
        
        ## Usage
        
        Run the tool with default settings.
        """
        
        excerpt = self.analyzer._extract_readme_excerpt(readme)
        
        assert 'Installation' in excerpt
        assert 'Configuration' in excerpt
        assert 'pip install' in excerpt
        assert 'API_KEY' in excerpt
    
    @patch('pitfall_detector.analyzer.openai.OpenAI')
    def test_call_llm_success(self, mock_openai_class):
        """Test successful LLM API call."""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"conflicts": [], "summary": "No conflicts"}'
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Create analyzer with mocked client
        with patch('pitfall_detector.config.config.get_api_key', return_value='test-key'):
            analyzer = ConflictAnalyzer()
            analyzer.client = mock_client
        
        result = analyzer._call_llm("test prompt")
        
        assert result == '{"conflicts": [], "summary": "No conflicts"}'
        mock_client.chat.completions.create.assert_called_once()
    
    def test_parse_analysis_result_valid_json(self):
        """Test parsing valid JSON response."""
        json_response = '''
        {
            "conflicts": [
                {
                    "type": "port_conflict",
                    "severity": "high",
                    "tools_involved": ["tool1", "tool2"],
                    "description": "Port conflict on 8000",
                    "confidence": "high"
                }
            ],
            "recommendations": ["Use different ports"],
            "overall_assessment": "One conflict found"
        }
        '''
        
        tools = [{'name': 'tool1'}, {'name': 'tool2'}]
        result = self.analyzer._parse_analysis_result(json_response, tools)
        
        assert len(result['conflicts']) == 1
        assert result['conflicts'][0]['type'] == 'port_conflict'
        assert result['conflicts'][0]['severity'] == 'high'
        assert result['tool_count'] == 2
        assert 'analysis_timestamp' in result
    
    def test_parse_analysis_result_invalid_json(self):
        """Test parsing invalid JSON response."""
        invalid_response = "This is not JSON response about conflicts"
        
        tools = [{'name': 'tool1'}, {'name': 'tool2'}]
        result = self.analyzer._parse_analysis_result(invalid_response, tools)
        
        # Should create fallback result
        assert 'raw_response' in result
        assert result['tool_count'] == 2
        assert len(result['tools_analyzed']) == 2
    
    def test_validate_result(self):
        """Test result validation and cleanup."""
        incomplete_result = {
            'conflicts': [
                {'type': 'port_conflict'},  # Missing required fields
                {'invalid': 'conflict'}      # Invalid conflict structure
            ]
        }
        
        validated = self.analyzer._validate_result(incomplete_result)
        
        # Should have required fields
        assert 'recommendations' in validated
        assert 'overall_assessment' in validated
        
        # Should only keep valid conflicts
        assert len(validated['conflicts']) == 1
        assert validated['conflicts'][0]['type'] == 'port_conflict'
        assert 'severity' in validated['conflicts'][0]  # Should add defaults
    
    def test_create_fallback_result(self):
        """Test fallback result creation."""
        error_text = "Error in analysis"
        
        result = self.analyzer._create_fallback_result(error_text)
        
        assert len(result['conflicts']) == 1
        assert result['conflicts'][0]['type'] == 'analysis_error'
        assert 'raw_response' in result
        assert result['raw_response'] == error_text


class TestConflictTypes:
    """Test conflict type constants."""
    
    def test_conflict_types_defined(self):
        """Test that all conflict types are properly defined."""
        expected_types = [
            'port_conflict',
            'dependency_conflict', 
            'functionality_overlap',
            'resource_competition',
            'environment_conflict',
            'config_conflict'
        ]
        
        for conflict_type in expected_types:
            assert hasattr(ConflictTypes, conflict_type.upper())
            assert getattr(ConflictTypes, conflict_type.upper()) == conflict_type


class TestSeverity:
    """Test severity level constants."""
    
    def test_severity_levels_defined(self):
        """Test that all severity levels are properly defined."""
        expected_levels = ['high', 'medium', 'low']
        
        for level in expected_levels:
            assert hasattr(Severity, level.upper())
            assert getattr(Severity, level.upper()) == level