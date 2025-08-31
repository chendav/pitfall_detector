"""Environment scanning for detecting installed AI tools and services."""

import os
import sys
import socket
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pkg_resources
import psutil
from .static_rules import KNOWN_AI_TOOLS
from .dynamic_agent_detector import DynamicAgentDetector


class EnvironmentScanner:
    """Scans the current environment for installed AI tools and services."""
    
    def __init__(self):
        self.known_tools = KNOWN_AI_TOOLS
        self.detected_tools = {}
        
    def scan_all(self, project_path: Optional[str] = None) -> Dict[str, any]:
        """
        Comprehensive environment scan for AI tools.
        
        Args:
            project_path: Optional path to specific project directory
            
        Returns:
            Dict containing all detected tools and services
        """
        results = {
            'python_packages': self._scan_python_packages(),
            'running_services': self._scan_running_services(),
            'project_files': self._scan_project_files(project_path) if project_path else {},
            'docker_containers': self._scan_docker_containers(),
            'conda_environments': self._scan_conda_environments(),
            'environment_variables': self._scan_environment_variables(),
            'detected_ai_tools': []
        }
        
        # Check for framework-specific directory structures (static)
        results['framework_detection'] = self._detect_frameworks(project_path) if project_path else {}
        
        # Dynamic AI Agent framework detection
        results['dynamic_agent_detection'] = self._detect_dynamic_agents(project_path) if project_path else []
        
        # Aggregate detected tools
        results['detected_ai_tools'] = self._aggregate_detected_tools(results)
        
        return results
    
    def _scan_python_packages(self) -> Dict[str, Dict]:
        """Scan installed Python packages for AI tools."""
        detected = {}
        
        try:
            # Get all installed packages
            installed_packages = {pkg.project_name.lower(): pkg for pkg in pkg_resources.working_set}
            
            for tool_name, tool_info in self.known_tools.items():
                # Check if any known package names match
                package_names = tool_info.get('package_names', [tool_name])
                for pkg_name in package_names:
                    if pkg_name.lower() in installed_packages:
                        pkg = installed_packages[pkg_name.lower()]
                        detected[tool_name] = {
                            'package_name': pkg.project_name,
                            'version': pkg.version,
                            'location': pkg.location,
                            'detection_method': 'pip_installed',
                            'tool_info': tool_info
                        }
                        break
            
        except Exception as e:
            print(f"Warning: Could not scan Python packages: {e}")
            
        return detected
    
    def _scan_running_services(self) -> Dict[str, Dict]:
        """Scan for running services on known AI tool ports."""
        detected = {}
        
        # Known AI tool ports
        known_ports = {
            8501: 'streamlit',
            7860: 'gradio', 
            8888: 'jupyter',
            8000: 'fastapi',
            5000: 'flask',
            3000: 'nodejs',
            8080: 'generic_web',
            9000: 'mlflow',
            6006: 'tensorboard',
            8501: 'streamlit_alternative'
        }
        
        for port, service_name in known_ports.items():
            if self._is_port_in_use(port):
                try:
                    # Try to get process info for the port
                    process_info = self._get_process_on_port(port)
                    detected[f"{service_name}_port_{port}"] = {
                        'port': port,
                        'service': service_name,
                        'process_info': process_info,
                        'detection_method': 'running_service',
                        'status': 'active'
                    }
                except Exception as e:
                    detected[f"{service_name}_port_{port}"] = {
                        'port': port,
                        'service': service_name,
                        'detection_method': 'port_scan',
                        'status': 'active',
                        'error': str(e)
                    }
        
        return detected
    
    def _scan_project_files(self, project_path: str) -> Dict[str, Dict]:
        """Scan project directory for AI tool configuration files."""
        detected = {}
        project_dir = Path(project_path)
        
        if not project_dir.exists():
            return detected
        
        # Files to look for
        config_files = {
            'requirements.txt': self._parse_requirements,
            'pyproject.toml': self._parse_pyproject,
            'environment.yml': self._parse_conda_env,
            'conda.yml': self._parse_conda_env,
            'package.json': self._parse_package_json,
            'Dockerfile': self._parse_dockerfile,
            'docker-compose.yml': self._parse_docker_compose,
            '.streamlit/config.toml': lambda x: {'streamlit': {'config_file': str(x)}},
            'gradio_interface.py': lambda x: {'gradio': {'interface_file': str(x)}},
            'app.py': self._analyze_app_file,
            'main.py': self._analyze_app_file,
        }
        
        for filename, parser in config_files.items():
            file_path = project_dir / filename
            if file_path.exists():
                try:
                    result = parser(file_path)
                    if result:
                        detected.update(result)
                except Exception as e:
                    detected[f"{filename}_error"] = {'error': str(e), 'file': str(file_path)}
        
        return detected
    
    def _scan_docker_containers(self) -> Dict[str, Dict]:
        """Scan for running Docker containers with AI tools."""
        detected = {}
        
        try:
            # Try to run docker ps
            result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}\t{{.Image}}\t{{.Ports}}'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            name, image, ports = parts[0], parts[1], parts[2]
                            
                            # Check if image contains known AI tools
                            for tool_name in self.known_tools.keys():
                                if tool_name in image.lower() or tool_name in name.lower():
                                    detected[f"docker_{name}"] = {
                                        'container_name': name,
                                        'image': image,
                                        'ports': ports,
                                        'tool': tool_name,
                                        'detection_method': 'docker_container',
                                        'status': 'running'
                                    }
                                    
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Docker not available
            pass
        except Exception as e:
            detected['docker_scan_error'] = {'error': str(e)}
            
        return detected
    
    def _scan_conda_environments(self) -> Dict[str, Dict]:
        """Scan conda environments for AI tools."""
        detected = {}
        
        try:
            # Try to get conda info
            result = subprocess.run(['conda', 'info', '--envs', '--json'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                conda_info = json.loads(result.stdout)
                envs = conda_info.get('envs', [])
                
                for env_path in envs:
                    env_name = Path(env_path).name
                    
                    # Check packages in each environment
                    try:
                        pkg_result = subprocess.run(['conda', 'list', '-p', env_path, '--json'], 
                                                  capture_output=True, text=True, timeout=10)
                        
                        if pkg_result.returncode == 0:
                            packages = json.loads(pkg_result.stdout)
                            
                            for pkg in packages:
                                pkg_name = pkg.get('name', '').lower()
                                for tool_name, tool_info in self.known_tools.items():
                                    package_names = tool_info.get('package_names', [tool_name])
                                    if any(pn.lower() == pkg_name for pn in package_names):
                                        detected[f"conda_{env_name}_{tool_name}"] = {
                                            'environment': env_name,
                                            'environment_path': env_path,
                                            'package_name': pkg.get('name'),
                                            'version': pkg.get('version'),
                                            'tool': tool_name,
                                            'detection_method': 'conda_env'
                                        }
                                        
                    except (subprocess.TimeoutExpired, json.JSONDecodeError):
                        continue
                        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            # Conda not available
            pass
        except Exception as e:
            detected['conda_scan_error'] = {'error': str(e)}
            
        return detected
    
    def _scan_environment_variables(self) -> Dict[str, str]:
        """Scan environment variables for AI tool API keys and configurations."""
        detected = {}
        
        # Known AI tool environment variables
        ai_env_vars = [
            'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'COHERE_API_KEY',
            'HUGGINGFACE_API_TOKEN', 'REPLICATE_API_TOKEN',
            'LANGCHAIN_API_KEY', 'LANGSMITH_API_KEY',
            'STREAMLIT_SERVER_PORT', 'GRADIO_SERVER_PORT',
            'JUPYTER_PORT', 'MLFLOW_TRACKING_URI',
            'WANDB_API_KEY', 'NEPTUNE_API_TOKEN'
        ]
        
        for var in ai_env_vars:
            value = os.getenv(var)
            if value:
                # Mask sensitive values
                if 'api_key' in var.lower() or 'token' in var.lower():
                    masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    detected[var] = masked
                else:
                    detected[var] = value
                    
        return detected
    
    def _detect_frameworks(self, project_path: str) -> Dict[str, Dict]:
        """Detect AI frameworks based on directory structure and special files."""
        detected = {}
        project_dir = Path(project_path)
        
        if not project_dir.exists():
            return detected
        
        # Check each known tool for framework detection patterns
        for tool_name, tool_info in self.known_tools.items():
            detection_patterns = tool_info.get('detection_patterns', {})
            if not detection_patterns:
                continue
            
            framework_indicators = {
                'directories_found': [],
                'files_found': [],
                'config_files_found': []
            }
            
            # Check for required directories
            required_dirs = detection_patterns.get('directories', [])
            for dir_name in required_dirs:
                dir_path = project_dir / dir_name
                if dir_path.exists() and dir_path.is_dir():
                    framework_indicators['directories_found'].append(dir_name)
            
            # Check for specific files within framework directories AND project root
            framework_files = detection_patterns.get('files', [])
            for file_pattern in framework_files:
                try:
                    # First check project root for framework files
                    # Clean the pattern to avoid invalid glob patterns
                    safe_pattern = file_pattern.replace('**', '*')
                    root_files = list(project_dir.glob(f"*{safe_pattern}*"))
                    if root_files:
                        framework_indicators['files_found'].extend([f.name for f in root_files])
                except ValueError as e:
                    print(f"Warning: Invalid glob pattern for {file_pattern}: {e}")
                    # Fallback to simple name check
                    for f in project_dir.iterdir():
                        if f.is_file() and file_pattern in f.name:
                            framework_indicators['files_found'].append(f.name)
                
                # Then check within framework directories
                for dir_name in framework_indicators['directories_found']:
                    framework_dir = project_dir / dir_name
                    # Look for files in subdirectories
                    for subdir in ['agents', 'checklists', 'tasks', 'workflows']:
                        search_dir = framework_dir / subdir
                        if search_dir.exists():
                            matching_files = list(search_dir.glob(f"*{file_pattern}*"))
                            if matching_files:
                                framework_indicators['files_found'].extend([f.name for f in matching_files])
            
            # Check for configuration files in project root AND framework directories
            config_files = detection_patterns.get('config_files', [])
            for config_file in config_files:
                # First check project root
                root_config = project_dir / config_file
                if root_config.exists():
                    framework_indicators['config_files_found'].append(config_file)
                
                # Then check framework directories
                for dir_name in framework_indicators['directories_found']:
                    config_path = project_dir / dir_name / config_file
                    if config_path.exists():
                        framework_indicators['config_files_found'].append(f"{dir_name}/{config_file}")
            
            # If we found framework indicators, mark this tool as detected
            if (framework_indicators['directories_found'] or 
                framework_indicators['files_found'] or 
                framework_indicators['config_files_found']):
                
                detected[f"framework_{tool_name}"] = {
                    'tool': tool_name,
                    'detection_method': 'framework_structure',
                    'framework_indicators': framework_indicators,
                    'description': tool_info.get('description', ''),
                    'github_url': tool_info.get('github_url', ''),
                    'project_path': str(project_path)
                }
        
        return detected
    
    def _detect_dynamic_agents(self, project_path: str) -> List[Dict]:
        """Detect AI Agent frameworks using dynamic pattern analysis."""
        detector = DynamicAgentDetector()
        return detector.detect_agent_frameworks(project_path)
    
    def _aggregate_detected_tools(self, scan_results: Dict) -> List[Dict]:
        """Aggregate all detected tools into a unified list."""
        tools = {}
        
        # From Python packages
        for tool_name, info in scan_results.get('python_packages', {}).items():
            if tool_name not in tools:
                tools[tool_name] = {
                    'name': tool_name,
                    'detection_methods': [],
                    'versions': [],
                    'locations': [],
                    'status': 'installed'
                }
            
            tools[tool_name]['detection_methods'].append(info.get('detection_method', 'unknown'))
            tools[tool_name]['versions'].append(info.get('version', 'unknown'))
            tools[tool_name]['locations'].append(info.get('location', 'unknown'))
        
        # From running services
        for service_key, info in scan_results.get('running_services', {}).items():
            service_name = info.get('service', service_key)
            # Map service names to tool names
            tool_name = self._map_service_to_tool(service_name)
            
            if tool_name not in tools:
                tools[tool_name] = {
                    'name': tool_name,
                    'detection_methods': [],
                    'versions': [],
                    'locations': [],
                    'status': 'running'
                }
            
            tools[tool_name]['detection_methods'].append('running_service')
            tools[tool_name]['ports'] = tools[tool_name].get('ports', []) + [info.get('port')]
        
        # From project files, docker, conda, framework detection, etc.
        for source in ['project_files', 'docker_containers', 'conda_environments', 'framework_detection']:
            for key, info in scan_results.get(source, {}).items():
                if 'tool' in info:
                    tool_name = info['tool']
                    if tool_name not in tools:
                        tools[tool_name] = {
                            'name': tool_name,
                            'detection_methods': [],
                            'versions': [],
                            'locations': [],
                            'status': 'detected'
                        }
                    
                    tools[tool_name]['detection_methods'].append(info.get('detection_method', source))
                    if 'version' in info:
                        tools[tool_name]['versions'].append(info['version'])
                    
                    # Add framework-specific information
                    if source == 'framework_detection':
                        tools[tool_name]['framework_indicators'] = info.get('framework_indicators', {})
                        tools[tool_name]['status'] = 'framework_detected'
        
        # From dynamic agent detection
        dynamic_agents = scan_results.get('dynamic_agent_detection', [])
        for agent_info in dynamic_agents:
            framework_name = agent_info.get('name')  # Changed from 'framework_name' to 'name'
            if framework_name and framework_name not in tools:
                tools[framework_name] = {
                    'name': framework_name,
                    'detection_methods': ['dynamic_agent_detection'],
                    'versions': [],
                    'locations': [agent_info.get('project_path', '')],
                    'status': 'agent_framework_detected',
                    'confidence_score': agent_info.get('confidence', 0),  # Changed from 'confidence_score' to 'confidence'
                    'agent_patterns': agent_info.get('evidence', {}),  # Changed from 'patterns_found' to 'evidence'
                    'framework_type': 'AI Agent Framework'
                }
            elif framework_name and framework_name in tools:
                # Add dynamic detection to existing tool
                if 'dynamic_agent_detection' not in tools[framework_name]['detection_methods']:
                    tools[framework_name]['detection_methods'].append('dynamic_agent_detection')
                    tools[framework_name]['confidence_score'] = agent_info.get('confidence', 0)  # Changed from 'confidence_score' to 'confidence'
                    tools[framework_name]['agent_patterns'] = agent_info.get('evidence', {})  # Changed from 'patterns_found' to 'evidence'
                    tools[framework_name]['framework_type'] = 'AI Agent Framework'  # Set framework type for existing tools too
        
        return list(tools.values())
    
    def _is_port_in_use(self, port: int) -> bool:
        """Check if a port is currently in use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                return result == 0
        except:
            return False
    
    def _get_process_on_port(self, port: int) -> Optional[Dict]:
        """Get process information for a specific port."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            return {
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                            }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass
        return None
    
    def _map_service_to_tool(self, service_name: str) -> str:
        """Map service names to standardized tool names."""
        mapping = {
            'streamlit': 'streamlit',
            'gradio': 'gradio',
            'jupyter': 'jupyter',
            'fastapi': 'fastapi',
            'flask': 'flask',
            'tensorboard': 'tensorboard',
            'mlflow': 'mlflow'
        }
        return mapping.get(service_name, service_name)
    
    def _parse_requirements(self, file_path: Path) -> Dict:
        """Parse requirements.txt for AI tools."""
        detected = {}
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Parse package name (handle version specifiers)
                        pkg_name = re.split(r'[>=<!]', line)[0].strip()
                        
                        for tool_name, tool_info in self.known_tools.items():
                            package_names = tool_info.get('package_names', [tool_name])
                            if pkg_name.lower() in [pn.lower() for pn in package_names]:
                                detected[f"requirements_{tool_name}"] = {
                                    'tool': tool_name,
                                    'package_spec': line,
                                    'file': str(file_path),
                                    'detection_method': 'requirements_txt'
                                }
        except Exception:
            pass
        return detected
    
    def _parse_pyproject(self, file_path: Path) -> Dict:
        """Parse pyproject.toml for AI tools."""
        detected = {}
        try:
            import toml
            with open(file_path, 'r') as f:
                data = toml.load(f)
            
            # Check dependencies
            deps = data.get('project', {}).get('dependencies', [])
            for dep in deps:
                pkg_name = re.split(r'[>=<!]', dep)[0].strip()
                for tool_name, tool_info in self.known_tools.items():
                    package_names = tool_info.get('package_names', [tool_name])
                    if pkg_name.lower() in [pn.lower() for pn in package_names]:
                        detected[f"pyproject_{tool_name}"] = {
                            'tool': tool_name,
                            'package_spec': dep,
                            'file': str(file_path),
                            'detection_method': 'pyproject_toml'
                        }
        except Exception:
            pass
        return detected
    
    def _parse_conda_env(self, file_path: Path) -> Dict:
        """Parse conda environment.yml for AI tools."""
        detected = {}
        try:
            import yaml
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check dependencies
            deps = data.get('dependencies', [])
            for dep in deps:
                if isinstance(dep, str):
                    pkg_name = re.split(r'[>=<!]', dep)[0].strip()
                    for tool_name, tool_info in self.known_tools.items():
                        package_names = tool_info.get('package_names', [tool_name])
                        if pkg_name.lower() in [pn.lower() for pn in package_names]:
                            detected[f"conda_env_{tool_name}"] = {
                                'tool': tool_name,
                                'package_spec': dep,
                                'file': str(file_path),
                                'detection_method': 'conda_environment_yml'
                            }
        except Exception:
            pass
        return detected
    
    def _parse_package_json(self, file_path: Path) -> Dict:
        """Parse package.json for Node.js AI tools."""
        detected = {}
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Check dependencies
            all_deps = {}
            all_deps.update(data.get('dependencies', {}))
            all_deps.update(data.get('devDependencies', {}))
            
            for pkg_name in all_deps.keys():
                # Check against known Node.js AI tools
                if 'langchain' in pkg_name.lower():
                    detected[f"npm_langchain"] = {
                        'tool': 'langchain',
                        'package_name': pkg_name,
                        'version': all_deps[pkg_name],
                        'file': str(file_path),
                        'detection_method': 'package_json'
                    }
        except Exception:
            pass
        return detected
    
    def _parse_dockerfile(self, file_path: Path) -> Dict:
        """Parse Dockerfile for AI tools."""
        detected = {}
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for AI tool installations
            for tool_name in self.known_tools.keys():
                if tool_name in content.lower():
                    detected[f"dockerfile_{tool_name}"] = {
                        'tool': tool_name,
                        'file': str(file_path),
                        'detection_method': 'dockerfile'
                    }
        except Exception:
            pass
        return detected
    
    def _parse_docker_compose(self, file_path: Path) -> Dict:
        """Parse docker-compose.yml for AI services."""
        detected = {}
        try:
            import yaml
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            services = data.get('services', {})
            for service_name, service_config in services.items():
                image = service_config.get('image', '')
                
                # Check if service uses AI tool images
                for tool_name in self.known_tools.keys():
                    if tool_name in image.lower() or tool_name in service_name.lower():
                        detected[f"docker_compose_{service_name}"] = {
                            'tool': tool_name,
                            'service_name': service_name,
                            'image': image,
                            'file': str(file_path),
                            'detection_method': 'docker_compose'
                        }
        except Exception:
            pass
        return detected
    
    def _analyze_app_file(self, file_path: Path) -> Dict:
        """Analyze app.py/main.py for AI tool imports."""
        detected = {}
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for common AI tool imports
            import_patterns = {
                'streamlit': r'import streamlit|from streamlit',
                'gradio': r'import gradio|from gradio',
                'langchain': r'import langchain|from langchain',
                'openai': r'import openai|from openai',
                'transformers': r'import transformers|from transformers',
                'torch': r'import torch|from torch',
                'tensorflow': r'import tensorflow|from tensorflow'
            }
            
            for tool_name, pattern in import_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    detected[f"app_import_{tool_name}"] = {
                        'tool': tool_name,
                        'file': str(file_path),
                        'detection_method': 'code_analysis'
                    }
        except Exception:
            pass
        return detected


def scan_current_environment() -> Dict:
    """Convenience function to scan current environment."""
    scanner = EnvironmentScanner()
    return scanner.scan_all(project_path=os.getcwd())