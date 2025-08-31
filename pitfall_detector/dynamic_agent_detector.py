"""Dynamic AI Agent Framework Detection System."""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict, Counter
import ast


class AgentFrameworkSignature:
    """Represents the signature patterns of an AI Agent framework."""
    
    def __init__(self, name: str):
        self.name = name
        self.directory_patterns = set()
        self.file_patterns = set()
        self.code_patterns = set()
        self.config_patterns = set()
        self.import_patterns = set()
        self.class_patterns = set()
        self.function_patterns = set()
        self.keyword_patterns = set()
        self.confidence_score = 0.0
        
    def calculate_confidence(self, matches: Dict[str, int]) -> float:
        """Calculate confidence score based on pattern matches."""
        total_patterns = (
            len(self.directory_patterns) + len(self.file_patterns) + 
            len(self.code_patterns) + len(self.import_patterns) +
            len(self.class_patterns) + len(self.function_patterns)
        )
        
        if total_patterns == 0:
            return 0.0
            
        total_matches = sum(matches.values())
        return min(total_matches / max(total_patterns, 1), 1.0)


class DynamicAgentDetector:
    """Dynamically detects AI Agent frameworks based on learned patterns."""
    
    def __init__(self):
        self.agent_keywords = {
            'agent', 'agents', 'multi-agent', 'autonomous', 'llm-agent',
            'ai-agent', 'chatbot', 'assistant', 'crew', 'team', 'orchestrat',
            'workflow', 'task', 'planner', 'executor', 'coordinator',
            'conversation', 'dialogue', 'chat', 'prompt', 'completion',
            'reasoning', 'decision', 'action', 'tool', 'function-call',
            'memory', 'context', 'state', 'session', 'thread'
        }
        
        self.framework_indicators = {
            'config_files': [
                'agent_config', 'agents.yaml', 'agents.json', 'crew.yaml',
                'workflow.yaml', 'tasks.yaml', 'prompts.yaml', 'tools.yaml',
                'memory.json', 'state.json', 'session.json'
            ],
            'directory_names': [
                'agents', 'agent', 'crew', 'team', 'workflows', 'tasks',
                'prompts', 'templates', 'tools', 'skills', 'actions',
                'memory', 'state', 'sessions', 'conversations', 'dialogues'
            ],
            'file_patterns': [
                r'.*agent.*\.(py|js|ts|yaml|json|md)$',
                r'.*crew.*\.(py|js|ts|yaml|json|md)$',
                r'.*workflow.*\.(py|js|ts|yaml|json|md)$',
                r'.*task.*\.(py|js|ts|yaml|json|md)$',
                r'.*prompt.*\.(py|js|ts|yaml|json|md)$',
                r'.*chat.*\.(py|js|ts|yaml|json|md)$',
                r'.*conversation.*\.(py|js|ts|yaml|json|md)$',
                r'.*tool.*\.(py|js|ts|yaml|json|md)$'
            ]
        }
    
    def detect_agent_frameworks(self, project_path: str) -> List[Dict[str, Any]]:
        """
        Dynamically detect AI Agent frameworks in the project.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            List of detected framework information
        """
        project_dir = Path(project_path)
        if not project_dir.exists():
            return []
        
        # Analyze project structure
        structure_analysis = self._analyze_project_structure(project_dir)
        
        # Analyze code content
        code_analysis = self._analyze_code_content(project_dir)
        
        # Analyze configuration files
        config_analysis = self._analyze_config_files(project_dir)
        
        # Detect frameworks based on combined analysis
        detected_frameworks = self._identify_frameworks(
            structure_analysis, code_analysis, config_analysis, project_dir
        )
        
        return detected_frameworks
    
    def _analyze_project_structure(self, project_dir: Path) -> Dict[str, Any]:
        """Analyze project directory structure for agent framework patterns."""
        analysis = {
            'agent_directories': [],
            'agent_files': [],
            'config_files': [],
            'structure_score': 0.0
        }
        
        try:
            # Walk through directory structure
            for root, dirs, files in os.walk(project_dir):
                root_path = Path(root)
                relative_root = root_path.relative_to(project_dir)
                
                # Check directory names for agent patterns
                for dir_name in dirs:
                    if self._is_agent_related_name(dir_name):
                        analysis['agent_directories'].append(str(relative_root / dir_name))
                
                # Check file names for agent patterns
                for file_name in files:
                    file_path = relative_root / file_name
                    
                    if self._is_agent_related_file(file_name):
                        analysis['agent_files'].append(str(file_path))
                    
                    if self._is_config_file(file_name):
                        analysis['config_files'].append(str(file_path))
            
            # Calculate structure score
            analysis['structure_score'] = self._calculate_structure_score(analysis)
            
        except Exception as e:
            print(f"Error analyzing project structure: {e}")
        
        return analysis
    
    def _analyze_code_content(self, project_dir: Path) -> Dict[str, Any]:
        """Analyze Python code content for agent framework patterns."""
        analysis = {
            'agent_imports': [],
            'agent_classes': [],
            'agent_functions': [],
            'agent_keywords': [],
            'code_score': 0.0
        }
        
        try:
            # Find Python files
            python_files = list(project_dir.rglob("*.py"))
            
            for py_file in python_files[:50]:  # Limit to avoid performance issues
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Analyze imports
                    imports = self._extract_imports(content)
                    agent_imports = [imp for imp in imports if self._is_agent_related_import(imp)]
                    analysis['agent_imports'].extend(agent_imports)
                    
                    # Analyze classes
                    classes = self._extract_classes(content)
                    agent_classes = [cls for cls in classes if self._is_agent_related_name(cls)]
                    analysis['agent_classes'].extend(agent_classes)
                    
                    # Analyze functions
                    functions = self._extract_functions(content)
                    agent_functions = [func for func in functions if self._is_agent_related_name(func)]
                    analysis['agent_functions'].extend(agent_functions)
                    
                    # Count agent-related keywords
                    keywords = self._count_agent_keywords(content)
                    analysis['agent_keywords'].extend(keywords)
                    
                except Exception as e:
                    continue
            
            # Calculate code score
            analysis['code_score'] = self._calculate_code_score(analysis)
            
        except Exception as e:
            print(f"Error analyzing code content: {e}")
        
        return analysis
    
    def _analyze_config_files(self, project_dir: Path) -> Dict[str, Any]:
        """Analyze configuration files for agent framework patterns."""
        analysis = {
            'agent_configs': [],
            'framework_hints': [],
            'config_score': 0.0
        }
        
        try:
            # Look for various config file types
            config_extensions = ['*.yaml', '*.yml', '*.json', '*.toml', '*.ini']
            config_files = []
            
            for ext in config_extensions:
                config_files.extend(project_dir.rglob(ext))
            
            for config_file in config_files[:30]:  # Limit to avoid performance issues
                try:
                    content = config_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Check for agent-related configuration
                    if self._contains_agent_config(content):
                        analysis['agent_configs'].append(str(config_file.relative_to(project_dir)))
                    
                    # Extract framework hints
                    hints = self._extract_framework_hints(content)
                    analysis['framework_hints'].extend(hints)
                    
                except Exception:
                    continue
            
            # Calculate config score
            analysis['config_score'] = self._calculate_config_score(analysis)
            
        except Exception as e:
            print(f"Error analyzing config files: {e}")
        
        return analysis
    
    def _identify_frameworks(self, structure: Dict, code: Dict, config: Dict, project_dir: Path) -> List[Dict[str, Any]]:
        """Identify specific agent frameworks based on analysis results."""
        frameworks = []
        
        # Calculate overall confidence
        total_score = (structure['structure_score'] + code['code_score'] + config['config_score']) / 3
        
        if total_score < 0.1:  # Too low confidence to suggest it's an agent framework
            return frameworks
        
        # Try to identify specific frameworks
        framework_name = self._infer_framework_name(structure, code, config, project_dir)
        
        # Create framework detection result
        framework_info = {
            'name': framework_name,
            'type': 'ai-agent-framework',
            'confidence': total_score,
            'detection_method': 'dynamic_analysis',
            'evidence': {
                'structure': structure,
                'code': code,
                'config': config
            },
            'description': self._generate_description(framework_name, structure, code, config),
            'suggested_github_search': self._generate_github_search_terms(framework_name, structure, code)
        }
        
        frameworks.append(framework_info)
        
        return frameworks
    
    def _is_agent_related_name(self, name: str) -> bool:
        """Check if a name is related to AI agents."""
        name_lower = name.lower()
        return any(keyword in name_lower for keyword in self.agent_keywords)
    
    def _is_agent_related_file(self, filename: str) -> bool:
        """Check if a filename suggests agent-related content."""
        for pattern in self.framework_indicators['file_patterns']:
            if re.match(pattern, filename.lower()):
                return True
        return False
    
    def _is_config_file(self, filename: str) -> bool:
        """Check if a file is a configuration file."""
        config_extensions = {'.yaml', '.yml', '.json', '.toml', '.ini', '.conf', '.config'}
        return Path(filename).suffix.lower() in config_extensions
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            # Fallback to regex if AST parsing fails
            import_patterns = [
                r'from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import',
                r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
            ]
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                imports.extend(matches)
        
        return imports
    
    def _is_agent_related_import(self, import_name: str) -> bool:
        """Check if an import suggests agent framework usage."""
        agent_import_keywords = {
            'agent', 'crew', 'autogen', 'langchain', 'llama', 'openai',
            'anthropic', 'huggingface', 'transformers', 'semantic_kernel',
            'chainlit', 'gradio', 'streamlit'
        }
        
        import_lower = import_name.lower()
        return any(keyword in import_lower for keyword in agent_import_keywords)
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from Python code."""
        classes = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except:
            # Fallback to regex
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            matches = re.findall(class_pattern, content)
            classes.extend(matches)
        
        return classes
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from Python code."""
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
        except:
            # Fallback to regex
            func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            matches = re.findall(func_pattern, content)
            functions.extend(matches)
        
        return functions
    
    def _count_agent_keywords(self, content: str) -> List[str]:
        """Count occurrences of agent-related keywords in content."""
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in self.agent_keywords:
            if keyword in content_lower:
                count = content_lower.count(keyword)
                if count > 0:
                    found_keywords.extend([keyword] * min(count, 10))  # Cap to avoid skewing
        
        return found_keywords
    
    def _contains_agent_config(self, content: str) -> bool:
        """Check if configuration content suggests agent framework."""
        content_lower = content.lower()
        config_keywords = {
            'agent', 'agents', 'crew', 'task', 'workflow', 'prompt',
            'llm', 'model', 'api_key', 'tools', 'functions', 'memory'
        }
        
        return any(keyword in content_lower for keyword in config_keywords)
    
    def _extract_framework_hints(self, content: str) -> List[str]:
        """Extract hints about specific frameworks from config content."""
        hints = []
        content_lower = content.lower()
        
        framework_hints = {
            'crewai': ['crew', 'crewai'],
            'autogen': ['autogen', 'microsoft'],
            'langchain': ['langchain', 'langsmith'],
            'semantic-kernel': ['semantic', 'kernel', 'microsoft'],
            'chainlit': ['chainlit'],
            'bmad': ['bmad', 'breakthrough']
        }
        
        for framework, keywords in framework_hints.items():
            if any(keyword in content_lower for keyword in keywords):
                hints.append(framework)
        
        return hints
    
    def _calculate_structure_score(self, analysis: Dict) -> float:
        """Calculate confidence score based on project structure."""
        score = 0.0
        
        # Score based on agent directories
        score += len(analysis['agent_directories']) * 0.3
        
        # Score based on agent files
        score += len(analysis['agent_files']) * 0.2
        
        # Score based on config files
        score += len(analysis['config_files']) * 0.1
        
        return min(score, 1.0)
    
    def _calculate_code_score(self, analysis: Dict) -> float:
        """Calculate confidence score based on code analysis."""
        score = 0.0
        
        # Score based on imports
        score += len(set(analysis['agent_imports'])) * 0.2
        
        # Score based on classes
        score += len(set(analysis['agent_classes'])) * 0.3
        
        # Score based on functions
        score += len(set(analysis['agent_functions'])) * 0.2
        
        # Score based on keywords
        keyword_count = len(set(analysis['agent_keywords']))
        score += min(keyword_count * 0.05, 0.3)
        
        return min(score, 1.0)
    
    def _calculate_config_score(self, analysis: Dict) -> float:
        """Calculate confidence score based on configuration analysis."""
        score = 0.0
        
        # Score based on agent configs
        score += len(analysis['agent_configs']) * 0.4
        
        # Score based on framework hints
        score += len(set(analysis['framework_hints'])) * 0.3
        
        return min(score, 1.0)
    
    def _infer_framework_name(self, structure: Dict, code: Dict, config: Dict, project_dir: Path) -> str:
        """Infer the most likely framework name based on analysis."""
        
        # Check for specific framework indicators
        framework_hints = config['framework_hints']
        if framework_hints:
            # Return the most common hint
            hint_counts = Counter(framework_hints)
            most_common = hint_counts.most_common(1)
            if most_common:
                return most_common[0][0]
        
        # Check imports for known frameworks
        imports = code['agent_imports']
        if imports:
            for imp in imports:
                if 'crewai' in imp.lower():
                    return 'crewai'
                elif 'autogen' in imp.lower():
                    return 'autogen'
                elif 'langchain' in imp.lower():
                    return 'langchain'
                elif 'semantic' in imp.lower():
                    return 'semantic-kernel'
        
        # Check directory names
        directories = structure['agent_directories']
        if directories:
            for dir_path in directories:
                dir_name = Path(dir_path).name.lower()
                if 'crew' in dir_name:
                    return 'crewai-like'
                elif 'agent' in dir_name:
                    return 'multi-agent-framework'
        
        # Default to generic name based on project directory
        project_name = project_dir.name.lower()
        if any(keyword in project_name for keyword in ['agent', 'crew', 'ai']):
            return f"custom-agent-framework-{project_name}"
        
        return "unknown-agent-framework"
    
    def _generate_description(self, framework_name: str, structure: Dict, code: Dict, config: Dict) -> str:
        """Generate a description of the detected framework."""
        
        features = []
        
        if structure['agent_directories']:
            features.append(f"{len(structure['agent_directories'])} agent directories")
        
        if code['agent_classes']:
            features.append(f"{len(set(code['agent_classes']))} agent classes")
        
        if code['agent_functions']:
            features.append(f"{len(set(code['agent_functions']))} agent functions")
        
        if config['agent_configs']:
            features.append("configuration files")
        
        if features:
            feature_text = ", ".join(features)
            return f"AI agent framework with {feature_text}"
        else:
            return "Detected AI agent framework"
    
    def _generate_github_search_terms(self, framework_name: str, structure: Dict, code: Dict) -> List[str]:
        """Generate GitHub search terms to find similar frameworks."""
        search_terms = []
        
        # Add framework name variations
        if framework_name != "unknown-agent-framework":
            search_terms.append(framework_name)
            search_terms.append(f"{framework_name} ai agent")
        
        # Add terms based on detected patterns
        if any('crew' in d.lower() for d in structure['agent_directories']):
            search_terms.append("crew ai agent framework")
        
        if any('workflow' in d.lower() for d in structure['agent_directories']):
            search_terms.append("ai workflow agent framework")
        
        # Add generic terms
        search_terms.extend([
            "multi agent framework",
            "ai agent orchestration",
            "llm agent framework"
        ])
        
        return list(set(search_terms))


def scan_for_agent_frameworks(project_path: str) -> List[Dict[str, Any]]:
    """Convenience function to scan for agent frameworks in a project."""
    detector = DynamicAgentDetector()
    return detector.detect_agent_frameworks(project_path)