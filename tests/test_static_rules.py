"""Tests for static conflict rules."""

import pytest
from pitfall_detector.static_rules import StaticConflictDetector


class TestStaticConflictDetector:
    """Test the StaticConflictDetector class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.detector = StaticConflictDetector()
    
    def test_detect_port_conflicts(self):
        """Test port conflict detection."""
        tools = [
            {
                'name': 'streamlit',
                'metadata': {'ports': [8501]}
            },
            {
                'name': 'custom-app', 
                'metadata': {'ports': [8501]}  # Same port
            }
        ]
        
        conflicts = self.detector.detect_port_conflicts(tools)
        
        assert len(conflicts) == 1
        assert conflicts[0]['type'] == 'port_conflict'
        assert conflicts[0]['severity'] == 'high'
        assert set(conflicts[0]['tools_involved']) == {'streamlit', 'custom-app'}
        assert '8501' in conflicts[0]['description']
    
    def test_detect_known_tool_ports(self):
        """Test detection using known tool ports."""
        tools = [
            {
                'name': 'streamlit',
                'metadata': {'ports': []}  # No extracted ports
            },
            {
                'name': 'gradio',
                'metadata': {'ports': []}
            }
        ]
        
        # Should not conflict as they use different known ports
        conflicts = self.detector.detect_port_conflicts(tools)
        assert len(conflicts) == 0
        
        # But if both try to use same port
        tools[1]['metadata']['ports'] = [8501]  # Gradio trying to use Streamlit's port
        conflicts = self.detector.detect_port_conflicts(tools)
        assert len(conflicts) == 1
    
    def test_detect_env_conflicts(self):
        """Test environment variable conflict detection."""
        tools = [
            {
                'name': 'openai-tool',
                'metadata': {'environment_vars': ['OPENAI_API_KEY']}
            },
            {
                'name': 'langchain',
                'metadata': {'environment_vars': []}  # Will be detected by name
            }
        ]
        
        conflicts = self.detector.detect_env_conflicts(tools)
        
        assert len(conflicts) == 1
        assert conflicts[0]['type'] == 'environment_conflict'
        assert 'OPENAI_API_KEY' in conflicts[0]['description']
    
    def test_detect_functional_overlaps(self):
        """Test functional overlap detection."""
        tools = [
            {
                'name': 'crewai',
                'metadata': {'categories': ['agent-framework']}
            },
            {
                'name': 'autogen',
                'metadata': {'categories': ['agent-framework']}
            }
        ]
        
        conflicts = self.detector.detect_functional_overlaps(tools)
        
        assert len(conflicts) == 1
        assert conflicts[0]['type'] == 'functionality_overlap'
        assert set(conflicts[0]['tools_involved']) == {'crewai', 'autogen'}
    
    def test_detect_all_static_conflicts(self):
        """Test comprehensive static conflict detection."""
        tools = [
            {
                'name': 'streamlit',
                'metadata': {
                    'ports': [8501],
                    'categories': ['web-interface'],
                    'environment_vars': []
                }
            },
            {
                'name': 'gradio',
                'metadata': {
                    'ports': [8501],  # Port conflict
                    'categories': ['web-interface'],  # Functional overlap
                    'environment_vars': []
                }
            }
        ]
        
        conflicts = self.detector.detect_all_static_conflicts(tools)
        
        # Should detect both port conflict and functional overlap
        assert len(conflicts) >= 2
        
        conflict_types = [c['type'] for c in conflicts]
        assert 'port_conflict' in conflict_types
        assert 'functionality_overlap' in conflict_types
    
    def test_no_conflicts_different_tools(self):
        """Test that different tools with no conflicts are handled correctly."""
        tools = [
            {
                'name': 'tensorflow',
                'metadata': {
                    'ports': [],
                    'categories': ['ml-framework'],
                    'environment_vars': []
                }
            },
            {
                'name': 'requests',
                'metadata': {
                    'ports': [],
                    'categories': ['http-client'],
                    'environment_vars': []
                }
            }
        ]
        
        conflicts = self.detector.detect_all_static_conflicts(tools)
        assert len(conflicts) == 0
    
    def test_single_tool_no_conflicts(self):
        """Test that a single tool generates no conflicts."""
        tools = [
            {
                'name': 'streamlit',
                'metadata': {
                    'ports': [8501],
                    'categories': ['web-interface']
                }
            }
        ]
        
        conflicts = self.detector.detect_all_static_conflicts(tools)
        assert len(conflicts) == 0