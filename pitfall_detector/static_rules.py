"""Static conflict rules for common AI tool conflicts."""

from typing import Dict, List, Any


# Known default ports for popular AI tools
KNOWN_TOOL_PORTS = {
    'streamlit': [8501],
    'gradio': [7860],
    'jupyter': [8888],
    'tensorboard': [6006],
    'mlflow': [5000],
    'fastapi': [8000],
    'flask': [5000],
    'dash': [8050],
    'bokeh': [5006],
    'voila': [8866]
}

# Known environment variable conflicts
KNOWN_ENV_CONFLICTS = {
    'OPENAI_API_KEY': ['openai', 'langchain', 'llama-index', 'autogen'],
    'ANTHROPIC_API_KEY': ['anthropic', 'claude'],
    'HF_TOKEN': ['huggingface', 'transformers'],
    'CUDA_VISIBLE_DEVICES': ['pytorch', 'tensorflow', 'jax'],
    'TOKENIZERS_PARALLELISM': ['transformers', 'datasets']
}

# Known dependency conflicts
KNOWN_DEPENDENCY_CONFLICTS = [
    {
        'conflict_type': 'version_conflict',
        'packages': ['tensorflow', 'torch'],
        'description': 'TensorFlow and PyTorch may have CUDA compatibility issues',
        'severity': 'medium'
    },
    {
        'conflict_type': 'version_conflict', 
        'packages': ['numpy', 'tensorflow'],
        'description': 'TensorFlow requires specific numpy versions',
        'severity': 'high'
    }
]

# Known functional overlaps
FUNCTIONAL_OVERLAPS = {
    'agent-framework': {
        'tools': ['crewai', 'autogen', 'langchain-agents', 'semantic-kernel'],
        'conflict_level': 'medium',
        'description': 'Multiple agent frameworks may compete for resources'
    },
    'web-interface': {
        'tools': ['streamlit', 'gradio', 'dash', 'bokeh'],
        'conflict_level': 'high',
        'description': 'Web interfaces typically conflict on default ports'
    },
    'vector-db': {
        'tools': ['chroma', 'pinecone', 'weaviate', 'qdrant'],
        'conflict_level': 'low',
        'description': 'Multiple vector databases may cause configuration confusion'
    }
}


class StaticConflictDetector:
    """Detects conflicts using hardcoded rules for common AI tools."""
    
    def detect_port_conflicts(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect port conflicts between tools."""
        conflicts = []
        port_usage = {}
        
        # Check extracted ports and known tool ports
        for tool in tools:
            tool_name = tool.get('name', '').lower()
            extracted_ports = tool.get('metadata', {}).get('ports', [])
            known_ports = KNOWN_TOOL_PORTS.get(tool_name, [])
            
            all_ports = list(set(extracted_ports + known_ports))
            
            for port in all_ports:
                if port in port_usage:
                    conflicts.append({
                        'type': 'port_conflict',
                        'severity': 'high',
                        'tools_involved': [port_usage[port], tool_name],
                        'description': f'Both tools use port {port}',
                        'potential_issues': f'Cannot run both tools simultaneously on port {port}',
                        'mitigation': f'Configure one tool to use a different port (e.g., --port {port + 1})',
                        'confidence': 'high',
                        'source': 'static_rule'
                    })
                else:
                    port_usage[port] = tool_name
        
        return conflicts
    
    def detect_env_conflicts(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect environment variable conflicts."""
        conflicts = []
        
        for env_var, related_tools in KNOWN_ENV_CONFLICTS.items():
            matching_tools = []
            
            for tool in tools:
                tool_name = tool.get('name', '').lower()
                extracted_envs = tool.get('metadata', {}).get('environment_vars', [])
                
                # Check if tool uses this env var (either extracted or known)
                if (env_var in extracted_envs or 
                    any(related_tool in tool_name for related_tool in related_tools)):
                    matching_tools.append(tool_name)
            
            if len(matching_tools) > 1:
                conflicts.append({
                    'type': 'environment_conflict',
                    'severity': 'medium',
                    'tools_involved': matching_tools,
                    'description': f'Multiple tools may use environment variable {env_var}',
                    'potential_issues': 'Environment variable conflicts may cause authentication issues',
                    'mitigation': f'Ensure {env_var} is set correctly for all tools that need it',
                    'confidence': 'medium',
                    'source': 'static_rule'
                })
        
        return conflicts
    
    def detect_functional_overlaps(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect functional overlaps between tools."""
        conflicts = []
        
        for category, overlap_info in FUNCTIONAL_OVERLAPS.items():
            matching_tools = []
            
            for tool in tools:
                tool_name = tool.get('name', '').lower()
                tool_categories = tool.get('metadata', {}).get('categories', [])
                
                if (category in tool_categories or 
                    any(overlap_tool in tool_name for overlap_tool in overlap_info['tools'])):
                    matching_tools.append(tool_name)
            
            if len(matching_tools) > 1:
                conflicts.append({
                    'type': 'functionality_overlap',
                    'severity': overlap_info['conflict_level'],
                    'tools_involved': matching_tools,
                    'description': overlap_info['description'],
                    'potential_issues': 'May cause resource competition or user confusion',
                    'mitigation': 'Consider using only one tool from this category, or configure them carefully',
                    'confidence': 'high',
                    'source': 'static_rule'
                })
        
        return conflicts
    
    def detect_all_static_conflicts(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run all static conflict detection methods."""
        all_conflicts = []
        
        all_conflicts.extend(self.detect_port_conflicts(tools))
        all_conflicts.extend(self.detect_env_conflicts(tools))
        all_conflicts.extend(self.detect_functional_overlaps(tools))
        
        return all_conflicts


# Predefined conflict rules that can be easily updated
STATIC_CONFLICT_RULES = [
    {
        'name': 'streamlit_gradio_port_conflict',
        'tools': ['streamlit', 'gradio'],
        'type': 'port_conflict',
        'severity': 'high',
        'description': 'Streamlit (8501) and Gradio (7860) may conflict if both try to use default ports',
        'mitigation': 'Use streamlit run --server.port 8502 or gradio.launch(server_port=7861)'
    },
    {
        'name': 'jupyter_notebook_port_conflict',
        'tools': ['jupyter', 'jupyterlab', 'notebook'],
        'type': 'port_conflict',
        'severity': 'medium', 
        'description': 'Multiple Jupyter instances may conflict on port 8888',
        'mitigation': 'Use jupyter lab --port 8889 for additional instances'
    },
    {
        'name': 'agent_framework_overlap',
        'tools': ['crewai', 'autogen', 'langchain'],
        'type': 'functionality_overlap',
        'severity': 'medium',
        'description': 'Multiple agent frameworks may compete for resources and cause confusion',
        'mitigation': 'Choose one primary agent framework and use others for specific features only'
    }
]