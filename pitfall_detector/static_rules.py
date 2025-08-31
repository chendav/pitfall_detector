"""Static rules for AI tool conflict detection - Database-driven version."""

from typing import Dict, List, Set
from .tools_database_loader import get_tools_database


# Load tools from the external database
def _load_known_tools() -> Dict[str, Dict]:
    """Load known AI tools from the external database."""
    try:
        db = get_tools_database()
        return db.get_all_tools()
    except Exception as e:
        print(f"Warning: Failed to load tools database: {e}")
        return {}


# Known AI tools - loaded from external database  
KNOWN_AI_TOOLS = _load_known_tools()

# Load port and environment conflicts from database
def _load_conflict_data():
    """Load conflict data from database."""
    try:
        db = get_tools_database()
        return {
            'port_conflicts': db.get_port_conflicts(),
            'env_conflicts': db.get_env_conflicts(),
            'conflict_patterns': db.get_conflict_patterns()
        }
    except Exception as e:
        print(f"Warning: Failed to load conflict data: {e}")
        return {'port_conflicts': {}, 'env_conflicts': {}, 'conflict_patterns': {}}

# Load conflict data
_conflict_data = _load_conflict_data()

# Known default ports for popular AI tools - from database
KNOWN_TOOL_PORTS = {}
for tool_name, tool_info in KNOWN_AI_TOOLS.items():
    ports = tool_info.get('default_ports', [])
    if ports:
        KNOWN_TOOL_PORTS[tool_name] = ports

# Known environment variable conflicts - from database
KNOWN_ENV_CONFLICTS = {}
tools_by_env = {}
for tool_name, tool_info in KNOWN_AI_TOOLS.items():
    env_vars = tool_info.get('common_env_vars', [])
    for env_var in env_vars:
        if env_var not in tools_by_env:
            tools_by_env[env_var] = []
        tools_by_env[env_var].append(tool_name)

# Only include env vars used by multiple tools (potential conflicts)
KNOWN_ENV_CONFLICTS = {
    env_var: tools for env_var, tools in tools_by_env.items()
    if len(tools) > 1
}

# Known dependency conflicts - loaded from database conflict patterns
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

# Functional overlaps - generated from database categories
FUNCTIONAL_OVERLAPS = {}
db = get_tools_database()
categories = {}

# Group tools by category
for tool_name, tool_info in KNOWN_AI_TOOLS.items():
    category = tool_info.get('category')
    if category:
        if category not in categories:
            categories[category] = []
        categories[category].append(tool_name)

# Create functional overlaps for categories with multiple tools
for category, tools in categories.items():
    if len(tools) > 1:
        # Determine conflict level based on category
        if category in ['web-interface', 'api-framework']:
            conflict_level = 'high'
            description = 'Web interfaces typically conflict on default ports'
        elif category == 'agent-framework':
            conflict_level = 'medium'
            description = 'Multiple agent frameworks may compete for resources'
        else:
            conflict_level = 'low'
            description = f'Multiple {category} tools may cause configuration confusion'
        
        FUNCTIONAL_OVERLAPS[category] = {
            'tools': tools,
            'conflict_level': conflict_level,
            'description': description
        }


# Database helper functions
def get_tool_info(tool_name: str) -> Dict:
    """Get tool information from database."""
    return KNOWN_AI_TOOLS.get(tool_name.lower(), {})

def get_tools_by_category(category: str) -> Dict[str, Dict]:
    """Get all tools in a specific category."""
    db = get_tools_database()
    return db.get_tools_by_category(category)

def search_tools(query: str) -> List[tuple[str, Dict]]:
    """Search tools in the database."""
    db = get_tools_database()
    return db.search_tools(query)

def get_database_info() -> Dict:
    """Get database metadata."""
    db = get_tools_database()
    return db.get_database_info()

def reload_tools_database():
    """Reload the tools database."""
    global KNOWN_AI_TOOLS, KNOWN_TOOL_PORTS, KNOWN_ENV_CONFLICTS, FUNCTIONAL_OVERLAPS
    from .tools_database_loader import reload_database
    
    reload_database()
    
    # Reload all derived data
    KNOWN_AI_TOOLS = _load_known_tools()
    
    # Reload port data
    KNOWN_TOOL_PORTS = {}
    for tool_name, tool_info in KNOWN_AI_TOOLS.items():
        ports = tool_info.get('default_ports', [])
        if ports:
            KNOWN_TOOL_PORTS[tool_name] = ports
    
    # Reload env conflicts
    tools_by_env = {}
    for tool_name, tool_info in KNOWN_AI_TOOLS.items():
        env_vars = tool_info.get('common_env_vars', [])
        for env_var in env_vars:
            if env_var not in tools_by_env:
                tools_by_env[env_var] = []
            tools_by_env[env_var].append(tool_name)
    
    KNOWN_ENV_CONFLICTS = {
        env_var: tools for env_var, tools in tools_by_env.items()
        if len(tools) > 1
    }
    
    print("Tools database reloaded successfully")


class StaticConflictDetector:
    """Detects conflicts using database rules for AI tools."""
    
    def detect_port_conflicts(self, tools: List[Dict[str, any]]) -> List[Dict[str, any]]:
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
    
    def detect_env_conflicts(self, tools: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Detect environment variable conflicts."""
        conflicts = []
        
        for env_var, related_tools in KNOWN_ENV_CONFLICTS.items():
            matching_tools = []
            
            for tool in tools:
                tool_name = tool.get('name', '').lower()
                extracted_envs = tool.get('metadata', {}).get('environment_vars', [])
                
                # Check if tool uses this env var (either extracted or known)
                if (env_var in extracted_envs or 
                    any(tool_name in related_tool or related_tool in tool_name for related_tool in related_tools)):
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
    
    def detect_functional_overlaps(self, tools: List[Dict[str, any]]) -> List[Dict[str, any]]:
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
    
    def detect_all_static_conflicts(self, tools: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """Run all static conflict detection methods."""
        all_conflicts = []
        
        all_conflicts.extend(self.detect_port_conflicts(tools))
        all_conflicts.extend(self.detect_env_conflicts(tools))
        all_conflicts.extend(self.detect_functional_overlaps(tools))
        
        return all_conflicts