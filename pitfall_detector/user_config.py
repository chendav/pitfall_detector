"""User configuration management for AI Pitfall Detector."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class UserConfigManager:
    """Manages user configuration and preferences."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize config manager."""
        if config_dir is None:
            # Use user's home directory for config
            config_dir = Path.home() / '.ai-pitfall-detector'
        
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / 'user_config.json'
        self.projects_file = self.config_dir / 'projects.json'
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config = self._load_config()
        self._projects = self._load_projects()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load user configuration."""
        if not self.config_file.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load user config: {e}")
            return self._get_default_config()
    
    def _load_projects(self) -> Dict[str, Any]:
        """Load project-specific configurations."""
        if not self.projects_file.exists():
            return {}
        
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load projects config: {e}")
            return {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default user configuration."""
        return {
            'version': '1.0',
            'user_preferences': {
                'default_output_format': 'human',
                'auto_save_reports': True,
                'verbose_mode': False,
                'report_directory': str(Path.home() / 'ai-pitfall-reports')
            },
            'api_keys': {
                # Store encrypted or hashed versions in real implementation
                'openai_api_key_set': False,
                'anthropic_api_key_set': False
            },
            'last_updated': datetime.now().isoformat(),
            'workflow_preferences': {
                'skip_confirmation': False,
                'auto_detect_missing': True,
                'suggest_similar_tools': False  # For future implementation
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            self._config['last_updated'] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save user config: {e}")
    
    def save_projects(self):
        """Save projects configuration to file."""
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(self._projects, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save projects config: {e}")
    
    def get_project_config(self, project_path: str) -> Dict[str, Any]:
        """Get configuration for a specific project."""
        project_key = str(Path(project_path).resolve())
        return self._projects.get(project_key, self._get_default_project_config(project_path))
    
    def save_project_config(self, project_path: str, config: Dict[str, Any]):
        """Save configuration for a specific project."""
        project_key = str(Path(project_path).resolve())
        config['last_updated'] = datetime.now().isoformat()
        self._projects[project_key] = config
        self.save_projects()
    
    def _get_default_project_config(self, project_path: str) -> Dict[str, Any]:
        """Get default configuration for a new project."""
        return {
            'project_path': project_path,
            'project_name': Path(project_path).name,
            'installed_tools': [],
            'manually_added_tools': [],
            'last_scan_date': None,
            'confirmed_tools': [],
            'target_tools': [],  # Tools user wants to install
            'excluded_tools': [],  # Tools user wants to ignore
            'scan_history': [],
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
    
    def add_installed_tool(self, project_path: str, tool_name: str, tool_info: Dict[str, Any]):
        """Add a tool to the project's installed tools list."""
        project_config = self.get_project_config(project_path)
        
        # Remove if already exists to avoid duplicates
        project_config['installed_tools'] = [
            t for t in project_config['installed_tools'] 
            if t.get('name', '').lower() != tool_name.lower()
        ]
        
        # Add the tool
        tool_entry = {
            'name': tool_name.lower(),
            'display_name': tool_info.get('display_name', tool_name),
            'github_url': tool_info.get('github_url', ''),
            'added_date': datetime.now().isoformat(),
            'added_manually': tool_info.get('added_manually', False),
            'detection_method': tool_info.get('detection_method', 'manual'),
            'metadata': tool_info.get('metadata', {})
        }
        
        project_config['installed_tools'].append(tool_entry)
        self.save_project_config(project_path, project_config)
    
    def add_target_tool(self, project_path: str, tool_name: str, github_url: str = ''):
        """Add a tool to the target installation list."""
        project_config = self.get_project_config(project_path)
        
        # Remove if already exists
        project_config['target_tools'] = [
            t for t in project_config['target_tools']
            if t.get('name', '').lower() != tool_name.lower()
        ]
        
        # Add the target tool
        target_tool = {
            'name': tool_name.lower(),
            'display_name': tool_name,
            'github_url': github_url,
            'added_date': datetime.now().isoformat()
        }
        
        project_config['target_tools'].append(target_tool)
        self.save_project_config(project_path, project_config)
    
    def get_installed_tools(self, project_path: str) -> List[Dict[str, Any]]:
        """Get list of installed tools for a project."""
        project_config = self.get_project_config(project_path)
        return project_config.get('installed_tools', [])
    
    def get_target_tools(self, project_path: str) -> List[Dict[str, Any]]:
        """Get list of target tools for a project."""
        project_config = self.get_project_config(project_path)
        return project_config.get('target_tools', [])
    
    def update_scan_history(self, project_path: str, scan_results: Dict[str, Any]):
        """Update the scan history for a project."""
        project_config = self.get_project_config(project_path)
        
        scan_entry = {
            'scan_date': datetime.now().isoformat(),
            'tools_detected': len(scan_results.get('detected_ai_tools', [])),
            'detection_methods': list(set([
                method for tool in scan_results.get('detected_ai_tools', [])
                for method in tool.get('detection_methods', [])
            ])),
            'scan_summary': {
                'python_packages': len(scan_results.get('python_packages', {})),
                'conda_packages': len(scan_results.get('conda_environments', {})),
                'running_services': len(scan_results.get('running_services', {})),
                'framework_detections': len(scan_results.get('framework_detection', {})),
                'dynamic_detections': len(scan_results.get('dynamic_agent_detection', []))
            }
        }
        
        # Keep only last 10 scan entries
        scan_history = project_config.get('scan_history', [])
        scan_history.append(scan_entry)
        project_config['scan_history'] = scan_history[-10:]
        project_config['last_scan_date'] = scan_entry['scan_date']
        
        self.save_project_config(project_path, project_config)
    
    def set_api_key_status(self, api_key_type: str, is_set: bool):
        """Update API key status (don't store actual keys)."""
        self._config['api_keys'][f'{api_key_type}_api_key_set'] = is_set
        self.save_config()
    
    def get_api_key_status(self, api_key_type: str) -> bool:
        """Check if API key is set."""
        return self._config['api_keys'].get(f'{api_key_type}_api_key_set', False)
    
    def get_report_directory(self) -> str:
        """Get the directory where reports should be saved."""
        report_dir = self._config['user_preferences'].get(
            'report_directory', 
            str(Path.home() / 'ai-pitfall-reports')
        )
        
        # Ensure directory exists
        Path(report_dir).mkdir(parents=True, exist_ok=True)
        return report_dir
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference value."""
        return self._config['user_preferences'].get(key, default)
    
    def set_user_preference(self, key: str, value: Any):
        """Set a user preference value."""
        self._config['user_preferences'][key] = value
        self.save_config()
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all configured projects."""
        projects = []
        for project_path, config in self._projects.items():
            projects.append({
                'project_path': project_path,
                'project_name': config.get('project_name', Path(project_path).name),
                'last_scan': config.get('last_scan_date'),
                'installed_tools_count': len(config.get('installed_tools', [])),
                'target_tools_count': len(config.get('target_tools', []))
            })
        
        return sorted(projects, key=lambda x: x.get('last_scan') or '', reverse=True)
    
    def cleanup_old_projects(self, max_projects: int = 20):
        """Remove old project configurations to keep config file manageable."""
        if len(self._projects) <= max_projects:
            return
        
        # Sort by last updated date and keep only the most recent
        sorted_projects = sorted(
            self._projects.items(),
            key=lambda x: x[1].get('last_updated', ''),
            reverse=True
        )
        
        # Keep only the most recent projects
        self._projects = dict(sorted_projects[:max_projects])
        self.save_projects()


# Global config manager instance
_config_manager = None

def get_user_config() -> UserConfigManager:
    """Get the global user config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = UserConfigManager()
    return _config_manager