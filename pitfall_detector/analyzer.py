"""AI-powered conflict analysis for AI tools."""

import json
import openai
from typing import Dict, List, Any, Optional
from .config import config
from .static_rules import StaticConflictDetector


class ConflictAnalyzer:
    """Analyzes potential conflicts between AI tools using LLM analysis."""
    
    def __init__(self):
        self.client = None
        self.api_key = config.get_api_key()
        self.provider = config.get('api.provider', 'openai')
        self.model = config.get('api.model', 'gpt-3.5-turbo')
        self.max_tokens = config.get('api.max_tokens', 2000)
        
        # Initialize static rule detector
        self.static_detector = StaticConflictDetector()
        
        # Initialize OpenAI client only if API key is available
        if self.api_key:
            if self.provider == 'openai':
                self.client = openai.OpenAI(api_key=self.api_key)
            else:
                raise Exception(f"Unsupported AI provider: {self.provider}")
        else:
            self.client = None  # Will fall back to static rules only
    
    def analyze_tool_conflicts(self, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze potential conflicts between multiple AI tools.
        
        Args:
            tools: List of tool dictionaries containing name, description, readme, etc.
            
        Returns:
            Dict containing conflict analysis results
        """
        if len(tools) < 2:
            return {
                'conflicts': [],
                'summary': 'Need at least 2 tools to analyze conflicts',
                'tool_count': len(tools)
            }
        
        # First, run static rule-based detection
        static_conflicts = self.static_detector.detect_all_static_conflicts(tools)
        
        # If no API key is available, return static results only
        if not self.client:
            return {
                'conflicts': static_conflicts,
                'summary': f'Static analysis completed. {len(static_conflicts)} conflicts detected using built-in rules.',
                'tool_count': len(tools),
                'tools_analyzed': [tool.get('name', 'Unknown') for tool in tools],
                'analysis_timestamp': self._get_timestamp(),
                'analysis_type': 'static_only',
                'static_conflicts_count': len(static_conflicts),
                'ai_conflicts_count': 0,
                'recommendations': ['Consider setting up an API key for more comprehensive AI-powered analysis'],
                'overall_assessment': 'Basic conflict detection completed using static rules'
            }
        
        # If API key is available, combine static and AI analysis
        try:
            # Prepare tool information for AI analysis
            tool_summaries = []
            for tool in tools:
                summary = self._create_tool_summary(tool)
                tool_summaries.append(summary)
            
            # Generate analysis prompt
            prompt = self._create_analysis_prompt(tool_summaries)
            
            # Call LLM for analysis
            ai_analysis_result = self._call_llm(prompt)
            
            # Parse and structure the AI result
            ai_result = self._parse_analysis_result(ai_analysis_result, tools)
            
            # Combine static and AI-detected conflicts
            all_conflicts = static_conflicts + ai_result.get('conflicts', [])
            
            # Remove duplicates (basic deduplication by type and tools involved)
            unique_conflicts = self._deduplicate_conflicts(all_conflicts)
            
            # Update the result with combined conflicts
            ai_result['conflicts'] = unique_conflicts
            ai_result['static_conflicts_count'] = len(static_conflicts)
            ai_result['ai_conflicts_count'] = len(ai_result.get('conflicts', [])) - len(static_conflicts)
            ai_result['analysis_type'] = 'hybrid'
            
            return ai_result
            
        except Exception as e:
            # If AI analysis fails, fall back to static analysis only
            return {
                'conflicts': static_conflicts,
                'summary': f'AI analysis failed, using static rules only. {len(static_conflicts)} conflicts detected.',
                'tool_count': len(tools),
                'tools_analyzed': [tool.get('name', 'Unknown') for tool in tools],
                'analysis_timestamp': self._get_timestamp(),
                'analysis_type': 'static_fallback',
                'static_conflicts_count': len(static_conflicts),
                'ai_conflicts_count': 0,
                'error': str(e),
                'recommendations': ['Static analysis completed. Set up API key for enhanced analysis'],
                'overall_assessment': 'Basic conflict detection completed with static rules due to AI analysis error'
            }
    
    def _create_tool_summary(self, tool: Dict[str, Any]) -> str:
        """Create a concise summary of a tool for analysis."""
        name = tool.get('name', 'Unknown')
        description = tool.get('description', '')
        metadata = tool.get('metadata', {})
        readme_excerpt = self._extract_readme_excerpt(tool.get('readme', ''))
        
        summary = f"""
Tool: {name}
Description: {description}
Categories: {', '.join(metadata.get('categories', []))}
Installation Methods: {', '.join(metadata.get('installation_methods', []))}
Default Ports: {metadata.get('ports', [])}
Environment Variables: {metadata.get('environment_vars', [])}
Key Documentation Excerpt:
{readme_excerpt}
"""
        return summary.strip()
    
    def _extract_readme_excerpt(self, readme: str, max_chars: int = 1000) -> str:
        """Extract relevant excerpt from README for analysis."""
        if not readme:
            return "No documentation available"
        
        # Look for installation, configuration, or usage sections
        important_sections = []
        lines = readme.split('\n')
        
        capture_next = 0
        for line in lines:
            # Check for important section headers
            if any(keyword in line.lower() for keyword in 
                   ['install', 'setup', 'config', 'usage', 'quick', 'start', 'port', 'environment']):
                capture_next = 10  # Capture next 10 lines
                important_sections.append(line)
            elif capture_next > 0:
                important_sections.append(line)
                capture_next -= 1
        
        # If no specific sections found, take the first part
        if not important_sections:
            important_sections = lines[:20]  # First 20 lines
        
        excerpt = '\n'.join(important_sections)
        
        # Truncate if too long
        if len(excerpt) > max_chars:
            excerpt = excerpt[:max_chars] + "..."
        
        return excerpt
    
    def _create_analysis_prompt(self, tool_summaries: List[str]) -> str:
        """Create the analysis prompt for the LLM."""
        tools_text = "\n\n".join([f"=== TOOL {i+1} ===\n{summary}" 
                                  for i, summary in enumerate(tool_summaries)])
        
        prompt = f"""
You are an expert AI engineer analyzing potential conflicts between AI tools. 
Analyze the following tools and identify potential conflicts when used together.

{tools_text}

Please analyze these tools for potential conflicts and provide a JSON response with the following structure:

{{
    "conflicts": [
        {{
            "type": "port_conflict|dependency_conflict|functionality_overlap|resource_competition|environment_conflict|config_conflict",
            "severity": "high|medium|low",
            "tools_involved": ["tool1", "tool2"],
            "description": "Clear description of the conflict",
            "potential_issues": "What could go wrong",
            "mitigation": "Suggested solution or workaround",
            "confidence": "high|medium|low"
        }}
    ],
    "compatible_combinations": [
        {{
            "tools": ["tool1", "tool2"],
            "reason": "Why these work well together"
        }}
    ],
    "recommendations": [
        "General recommendations for using these tools together"
    ],
    "overall_assessment": "Summary assessment of the tool combination"
}}

Focus on these types of conflicts:
1. **Port Conflicts**: Tools using same default ports
2. **Dependency Conflicts**: Version conflicts in Python packages or system dependencies  
3. **Functionality Overlap**: Tools doing similar things that might interfere
4. **Resource Competition**: Memory, GPU, or model cache conflicts
5. **Environment Conflicts**: Same environment variables used differently
6. **Configuration Conflicts**: Config files or directories that clash

Be practical and specific. Only report conflicts that would actually cause problems for users.
If tools are compatible, mention that too. Provide actionable mitigation strategies.
"""
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM API for analysis."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI engineer specializing in tool integration and conflict analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Failed to get analysis from {self.provider}: {e}")
    
    def _parse_analysis_result(self, analysis_text: str, original_tools: List[Dict]) -> Dict[str, Any]:
        """Parse and validate the LLM analysis result."""
        try:
            # Try to extract JSON from the response
            json_start = analysis_text.find('{')
            json_end = analysis_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = analysis_text[json_start:json_end]
                result = json.loads(json_text)
            else:
                # If no JSON found, create a structured response from text
                result = self._create_fallback_result(analysis_text)
            
            # Add metadata
            result['tool_count'] = len(original_tools)
            result['tools_analyzed'] = [tool.get('name', 'Unknown') for tool in original_tools]
            result['analysis_timestamp'] = self._get_timestamp()
            
            # Validate and clean up the result
            return self._validate_result(result)
            
        except json.JSONDecodeError:
            # Fallback to text-based parsing
            return self._create_fallback_result(analysis_text)
        except Exception as e:
            return {
                'conflicts': [],
                'error': f"Failed to parse analysis result: {e}",
                'raw_response': analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text,
                'tool_count': len(original_tools),
                'tools_analyzed': [tool.get('name', 'Unknown') for tool in original_tools]
            }
    
    def _create_fallback_result(self, analysis_text: str) -> Dict[str, Any]:
        """Create a fallback result when JSON parsing fails."""
        return {
            'conflicts': [
                {
                    'type': 'analysis_error',
                    'severity': 'low',
                    'tools_involved': ['all'],
                    'description': 'Could not parse detailed analysis',
                    'potential_issues': 'Analysis format error',
                    'mitigation': 'Review tools manually for conflicts',
                    'confidence': 'low'
                }
            ],
            'compatible_combinations': [],
            'recommendations': ['Manual review recommended due to parsing error'],
            'overall_assessment': 'Analysis parsing failed - manual review needed',
            'raw_response': analysis_text[:1000] + "..." if len(analysis_text) > 1000 else analysis_text
        }
    
    def _validate_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean up the analysis result."""
        # Ensure required fields exist
        if 'conflicts' not in result:
            result['conflicts'] = []
        if 'recommendations' not in result:
            result['recommendations'] = []
        if 'overall_assessment' not in result:
            result['overall_assessment'] = 'Analysis completed'
        
        # Validate conflict objects
        valid_conflicts = []
        for conflict in result.get('conflicts', []):
            if isinstance(conflict, dict) and 'type' in conflict:
                # Set defaults for missing fields
                conflict.setdefault('severity', 'medium')
                conflict.setdefault('tools_involved', [])
                conflict.setdefault('description', 'Conflict detected')
                conflict.setdefault('confidence', 'medium')
                valid_conflicts.append(conflict)
        
        result['conflicts'] = valid_conflicts
        return result
    
    def _deduplicate_conflicts(self, conflicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate conflicts based on type and tools involved."""
        seen_conflicts = set()
        unique_conflicts = []
        
        for conflict in conflicts:
            # Create a signature for this conflict
            conflict_type = conflict.get('type', '')
            tools_involved = tuple(sorted(conflict.get('tools_involved', [])))
            signature = (conflict_type, tools_involved)
            
            if signature not in seen_conflicts:
                seen_conflicts.add(signature)
                unique_conflicts.append(conflict)
            else:
                # If we see a duplicate, prefer the one with higher confidence or from static rules
                for i, existing in enumerate(unique_conflicts):
                    existing_sig = (existing.get('type', ''), tuple(sorted(existing.get('tools_involved', []))))
                    if existing_sig == signature:
                        # Prefer static rules or higher confidence
                        if (conflict.get('source') == 'static_rule' or 
                            conflict.get('confidence') == 'high'):
                            unique_conflicts[i] = conflict
                        break
        
        return unique_conflicts
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis metadata."""
        from datetime import datetime
        return datetime.now().isoformat()


class ConflictTypes:
    """Enumeration of conflict types."""
    
    PORT_CONFLICT = "port_conflict"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    FUNCTIONALITY_OVERLAP = "functionality_overlap"
    RESOURCE_COMPETITION = "resource_competition"
    ENVIRONMENT_CONFLICT = "environment_conflict"
    CONFIG_CONFLICT = "config_conflict"


class Severity:
    """Enumeration of conflict severity levels."""
    
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"