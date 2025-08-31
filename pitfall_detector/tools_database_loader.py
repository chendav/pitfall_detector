"""Tools Database Loader - Interface for the static AI tools database."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


class ToolsDatabaseLoader:
    """Loads and provides access to the static AI tools database."""
    
    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize the database loader.
        
        Args:
            database_path: Path to the tools database YAML file
        """
        if database_path is None:
            # Default to tools_database.yaml in the same directory as this script
            current_dir = Path(__file__).parent.parent
            database_path = current_dir / "tools_database.yaml"
        
        self.database_path = Path(database_path)
        self._database = None
        self._load_database()
    
    def _load_database(self):
        """Load the tools database from YAML file."""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                self._database = yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load tools database from {self.database_path}: {e}")
    
    def get_all_tools(self) -> Dict[str, Dict]:
        """Get all tools from the database."""
        return self._database.get('tools', {})
    
    def get_tool(self, tool_name: str) -> Optional[Dict]:
        """Get specific tool information."""
        tools = self.get_all_tools()
        return tools.get(tool_name.lower())
    
    def get_tool_by_package(self, package_name: str) -> Optional[tuple[str, Dict]]:
        """Find tool by package name."""
        tools = self.get_all_tools()
        package_lower = package_name.lower()
        
        for tool_name, tool_info in tools.items():
            package_names = tool_info.get('package_names', [])
            if any(pkg.lower() == package_lower for pkg in package_names):
                return tool_name, tool_info
        
        return None
    
    def get_tools_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all tools in a specific category."""
        tools = self.get_all_tools()
        return {
            name: info for name, info in tools.items()
            if info.get('category') == category
        }
    
    def get_port_conflicts(self) -> Dict[str, List[int]]:
        """Get port conflict groups."""
        return self._database.get('port_conflicts', {})
    
    def get_env_conflicts(self) -> Dict[str, List[str]]:
        """Get environment variable conflict groups."""
        return self._database.get('env_conflicts', {})
    
    def get_detection_signatures(self) -> Dict[str, Dict]:
        """Get detection signatures for dynamic analysis."""
        return self._database.get('detection_signatures', {})
    
    def get_conflict_patterns(self) -> Dict[str, Dict]:
        """Get conflict pattern definitions."""
        return self._database.get('conflict_patterns', {})
    
    def get_compatibility_matrix(self) -> Dict[str, Dict]:
        """Get version compatibility information."""
        return self._database.get('compatibility_matrix', {})
    
    def get_installation_command(self, tool_name: str) -> Optional[str]:
        """Get installation command for a tool."""
        commands = self._database.get('installation_commands', {})
        return commands.get(tool_name.lower())
    
    def get_documentation_url(self, tool_name: str) -> Optional[str]:
        """Get documentation URL for a tool."""
        docs = self._database.get('documentation', {})
        return docs.get(tool_name.lower())
    
    def search_tools(self, query: str) -> List[tuple[str, Dict]]:
        """Search tools by name, description, or category."""
        query_lower = query.lower()
        results = []
        
        tools = self.get_all_tools()
        for tool_name, tool_info in tools.items():
            # Search in name
            if query_lower in tool_name.lower():
                results.append((tool_name, tool_info))
                continue
            
            # Search in description
            description = tool_info.get('description', '').lower()
            if query_lower in description:
                results.append((tool_name, tool_info))
                continue
            
            # Search in category
            category = tool_info.get('category', '').lower()
            if query_lower in category:
                results.append((tool_name, tool_info))
                continue
        
        return results
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database metadata."""
        return {
            'version': self._database.get('version'),
            'last_updated': self._database.get('last_updated'),
            'description': self._database.get('description'),
            'total_tools': len(self.get_all_tools()),
            'categories': list(self._database.get('categories', {}).keys()),
            'database_path': str(self.database_path)
        }
    
    def validate_database(self) -> List[str]:
        """Validate database structure and return any issues."""
        issues = []
        
        if not self._database:
            return ["Database not loaded"]
        
        # Check required sections
        required_sections = ['tools', 'categories']
        for section in required_sections:
            if section not in self._database:
                issues.append(f"Missing required section: {section}")
        
        # Validate tools
        tools = self.get_all_tools()
        for tool_name, tool_info in tools.items():
            # Check required fields
            required_fields = ['name', 'description', 'category']
            for field in required_fields:
                if field not in tool_info:
                    issues.append(f"Tool '{tool_name}' missing required field: {field}")
            
            # Check category validity
            categories = self._database.get('categories', {})
            tool_category = tool_info.get('category')
            if tool_category and tool_category not in categories:
                issues.append(f"Tool '{tool_name}' has invalid category: {tool_category}")
        
        return issues


# Global database instance
_db_instance = None

def get_tools_database() -> ToolsDatabaseLoader:
    """Get the global tools database instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = ToolsDatabaseLoader()
    return _db_instance

def reload_database():
    """Reload the database (useful for testing or after updates)."""
    global _db_instance
    _db_instance = None
    return get_tools_database()