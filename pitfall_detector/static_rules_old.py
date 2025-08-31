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
    'voila': [8866],
    'wandb': [8080],
    'ray': [8265, 10001],
    'dask': [8786, 8787],
    'prefect': [4200]
}

# Load tools from the external database
def _load_known_tools() -> Dict[str, Dict]:
    """Load known AI tools from the external database."""
    try:
        from .tools_database_loader import get_tools_database
        db = get_tools_database()
        return db.get_all_tools()
    except Exception as e:
        print(f"Warning: Failed to load tools database: {e}")
        return {}

# Known AI tools - loaded from external database  
KNOWN_AI_TOOLS = _load_known_tools()

# Legacy tools data (kept for backward compatibility, but loaded from database)
_LEGACY_KNOWN_AI_TOOLS = {
    'streamlit': {
        'package_names': ['streamlit'],
        'github_url': 'https://github.com/streamlit/streamlit',
        'category': 'web-interface',
        'default_ports': [8501],
        'common_env_vars': ['STREAMLIT_SERVER_PORT'],
        'description': 'Web app framework for ML/AI applications'
    },
    'gradio': {
        'package_names': ['gradio'],
        'github_url': 'https://github.com/gradio-app/gradio',
        'category': 'web-interface',
        'default_ports': [7860, 7861, 7862],
        'common_env_vars': ['GRADIO_SERVER_PORT'],
        'description': 'Web UI for ML models'
    },
    'jupyter': {
        'package_names': ['jupyter', 'jupyterlab', 'notebook'],
        'github_url': 'https://github.com/jupyter/notebook',
        'category': 'notebook',
        'default_ports': [8888, 8889],
        'common_env_vars': ['JUPYTER_PORT', 'JUPYTER_TOKEN'],
        'description': 'Interactive computing environment'
    },
    'langchain': {
        'package_names': ['langchain', 'langchain-core', 'langchain-community'],
        'github_url': 'https://github.com/langchain-ai/langchain',
        'category': 'llm-framework',
        'default_ports': [],
        'common_env_vars': ['LANGCHAIN_API_KEY', 'LANGSMITH_API_KEY'],
        'description': 'LLM application framework'
    },
    'openai': {
        'package_names': ['openai'],
        'github_url': 'https://github.com/openai/openai-python',
        'category': 'llm-client',
        'default_ports': [],
        'common_env_vars': ['OPENAI_API_KEY'],
        'description': 'OpenAI API client'
    },
    'transformers': {
        'package_names': ['transformers'],
        'github_url': 'https://github.com/huggingface/transformers',
        'category': 'ml-library',
        'default_ports': [],
        'common_env_vars': ['HUGGINGFACE_API_TOKEN', 'HF_TOKEN'],
        'description': 'HuggingFace transformers library'
    },
    'torch': {
        'package_names': ['torch', 'pytorch'],
        'github_url': 'https://github.com/pytorch/pytorch',
        'category': 'ml-framework',
        'default_ports': [],
        'common_env_vars': ['CUDA_VISIBLE_DEVICES'],
        'description': 'PyTorch deep learning framework'
    },
    'tensorflow': {
        'package_names': ['tensorflow', 'tensorflow-gpu'],
        'github_url': 'https://github.com/tensorflow/tensorflow',
        'category': 'ml-framework',
        'default_ports': [],
        'common_env_vars': ['CUDA_VISIBLE_DEVICES', 'TF_CPP_MIN_LOG_LEVEL'],
        'description': 'TensorFlow machine learning platform'
    },
    'fastapi': {
        'package_names': ['fastapi'],
        'github_url': 'https://github.com/tiangolo/fastapi',
        'category': 'api-framework',
        'default_ports': [8000],
        'common_env_vars': [],
        'description': 'Modern web framework for APIs'
    },
    'flask': {
        'package_names': ['flask'],
        'github_url': 'https://github.com/pallets/flask',
        'category': 'web-framework',
        'default_ports': [5000],
        'common_env_vars': ['FLASK_APP', 'FLASK_ENV'],
        'description': 'Lightweight web framework'
    },
    'mlflow': {
        'package_names': ['mlflow'],
        'github_url': 'https://github.com/mlflow/mlflow',
        'category': 'ml-ops',
        'default_ports': [5000, 5001],
        'common_env_vars': ['MLFLOW_TRACKING_URI'],
        'description': 'ML lifecycle management'
    },
    'wandb': {
        'package_names': ['wandb'],
        'github_url': 'https://github.com/wandb/wandb',
        'category': 'ml-ops',
        'default_ports': [8080],
        'common_env_vars': ['WANDB_API_KEY', 'WANDB_PROJECT'],
        'description': 'ML experiment tracking'
    },
    'tensorboard': {
        'package_names': ['tensorboard'],
        'github_url': 'https://github.com/tensorflow/tensorboard',
        'category': 'visualization',
        'default_ports': [6006],
        'common_env_vars': [],
        'description': 'Visualization toolkit for ML'
    },
    'crewai': {
        'package_names': ['crewai'],
        'github_url': 'https://github.com/joaomdmoura/crewAI',
        'category': 'agent-framework',
        'default_ports': [],
        'common_env_vars': ['OPENAI_API_KEY'],
        'description': 'Multi-agent orchestration framework'
    },
    'autogen': {
        'package_names': ['pyautogen'],
        'github_url': 'https://github.com/microsoft/autogen',
        'category': 'agent-framework',
        'default_ports': [],
        'common_env_vars': ['OPENAI_API_KEY'],
        'description': 'Multi-agent conversation framework'
    },
    'bmad': {
        'package_names': ['bmad-method'],
        'github_url': 'https://github.com/chendav/BMAD-METHOD',
        'category': 'agent-framework',
        'default_ports': [],
        'common_env_vars': ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY'],
        'description': 'Breakthrough Method of Agile AI-driven Development',
        'detection_patterns': {
            'directories': ['.bmad-core'],
            'files': ['bmad-master.md', 'bmad-orchestrator.md'],
            'config_files': ['core-config.yaml', 'install-manifest.yaml']
        }
    },
    'nextjs': {
        'package_names': ['next'],
        'github_url': 'https://github.com/vercel/next.js',
        'category': 'web-framework',
        'default_ports': [3000],
        'common_env_vars': ['NEXT_PUBLIC_API_URL'],
        'description': 'React framework for production',
        'detection_patterns': {
            'files': ['next.config.js', 'next.config.ts'],
            'directories': ['.next', 'pages', 'app'],
            'config_files': ['next.config.js', 'next.config.ts']
        }
    },
    'django': {
        'package_names': ['django'],
        'github_url': 'https://github.com/django/django',
        'category': 'web-framework',
        'default_ports': [8000],
        'common_env_vars': ['DJANGO_SECRET_KEY', 'DJANGO_DEBUG'],
        'description': 'High-level Python web framework',
        'detection_patterns': {
            'files': ['manage.py', 'settings.py', 'urls.py'],
            'directories': ['migrations'],
            'config_files': ['settings.py', 'wsgi.py']
        }
    },
    'hugginface-transformers': {
        'package_names': ['transformers'],
        'github_url': 'https://github.com/huggingface/transformers',
        'category': 'ml-framework',
        'default_ports': [],
        'common_env_vars': ['HF_TOKEN', 'HUGGINGFACE_HUB_CACHE'],
        'description': 'State-of-the-art ML models',
        'detection_patterns': {
            'directories': ['models', '.cache/huggingface'],
            'files': ['config.json', 'tokenizer.json'],
            'config_files': ['config.json']
        }
    },
    'langchain-serve': {
        'package_names': ['langchain', 'langserve'],
        'github_url': 'https://github.com/langchain-ai/langserve',
        'category': 'llm-framework',
        'default_ports': [8000],
        'common_env_vars': ['LANGCHAIN_API_KEY', 'LANGSMITH_API_KEY'],
        'description': 'LangChain serving framework',
        'detection_patterns': {
            'files': ['langchain_serve.py', 'chain.py'],
            'directories': ['chains', 'agents'],
            'config_files': ['langchain.yaml']
        }
    },
    'llamaindex': {
        'package_names': ['llama-index', 'llama_index'],
        'github_url': 'https://github.com/run-llama/llama_index',
        'category': 'rag-framework',
        'default_ports': [],
        'common_env_vars': ['OPENAI_API_KEY', 'LLAMA_INDEX_CACHE_DIR'],
        'description': 'Data framework for LLM applications',
        'detection_patterns': {
            'directories': ['indices', 'storage'],
            'files': ['index.json', 'docstore.json'],
            'config_files': ['llamaindex.yaml']
        }
    },
    'chainlit': {
        'package_names': ['chainlit'],
        'github_url': 'https://github.com/Chainlit/chainlit',
        'category': 'chat-interface',
        'default_ports': [8000],
        'common_env_vars': ['CHAINLIT_AUTH_SECRET'],
        'description': 'Build Python LLM apps in minutes',
        'detection_patterns': {
            'files': ['app.py', 'chainlit.md'],
            'directories': ['.chainlit'],
            'config_files': ['chainlit.toml', '.chainlit/config.toml']
        }
    },
    'memgpt': {
        'package_names': ['memgpt', 'pymemgpt'],
        'github_url': 'https://github.com/cpacker/MemGPT',
        'category': 'memory-framework',
        'default_ports': [8283],
        'common_env_vars': ['MEMGPT_CONFIG_PATH', 'OPENAI_API_KEY'],
        'description': 'Create LLM agents with long-term memory',
        'detection_patterns': {
            'directories': ['.memgpt', 'memgpt_config'],
            'files': ['memgpt_config.yaml', 'agent_config.json'],
            'config_files': ['memgpt_config.yaml']
        }
    },
    'autogen-studio': {
        'package_names': ['autogen-studio'],
        'github_url': 'https://github.com/microsoft/autogen',
        'category': 'agent-framework',
        'default_ports': [8081],
        'common_env_vars': ['OPENAI_API_KEY'],
        'description': 'AutoGen Studio UI for multi-agent conversations',
        'detection_patterns': {
            'directories': ['autogen_studio', '.autogen'],
            'files': ['autogen_config.json'],
            'config_files': ['autogen_config.json']
        }
    },
    'semantic-kernel': {
        'package_names': ['semantic-kernel'],
        'github_url': 'https://github.com/microsoft/semantic-kernel',
        'category': 'agent-framework',
        'default_ports': [],
        'common_env_vars': ['AZURE_OPENAI_API_KEY', 'OPENAI_API_KEY'],
        'description': 'Microsoft Semantic Kernel SDK',
        'detection_patterns': {
            'directories': ['skills', 'plugins'],
            'files': ['kernel_config.json', 'skills.yaml'],
            'config_files': ['kernel_config.json']
        }
    }
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