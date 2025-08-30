"""Report formatting and output for conflict analysis results."""

import json
from typing import Dict, Any, List
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform colored output
init()


class ConflictReporter:
    """Formats and displays conflict analysis results."""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        
        # Color mappings
        self.colors = {
            'high': Fore.RED,
            'medium': Fore.YELLOW, 
            'low': Fore.BLUE,
            'success': Fore.GREEN,
            'info': Fore.CYAN,
            'reset': Style.RESET_ALL
        } if use_colors else {k: '' for k in ['high', 'medium', 'low', 'success', 'info', 'reset']}
        
        # Emoji mappings  
        self.emojis = {
            'high': '🚨',
            'medium': '⚠️',
            'low': '💡',
            'success': '✅',
            'conflict': '⚡',
            'tool': '🔧',
            'analysis': '🔍',
            'info': 'ℹ️'
        } if use_colors else {k: '' for k in ['high', 'medium', 'low', 'success', 'conflict', 'tool', 'analysis', 'info']}
    
    def generate_report(self, analysis_result: Dict[str, Any], format_type: str = 'human') -> str:
        """
        Generate a formatted report from analysis results.
        
        Args:
            analysis_result: Dict containing analysis results
            format_type: 'human' or 'json'
            
        Returns:
            Formatted report string
        """
        if format_type.lower() == 'json':
            return self._generate_json_report(analysis_result)
        else:
            return self._generate_human_report(analysis_result)
    
    def _generate_human_report(self, result: Dict[str, Any]) -> str:
        """Generate human-readable report."""
        report_lines = []
        
        # Header
        report_lines.append(self._format_header(result))
        report_lines.append("")
        
        # Tools analyzed
        report_lines.append(self._format_tools_section(result))
        report_lines.append("")
        
        # Conflicts section
        conflicts = result.get('conflicts', [])
        if conflicts:
            report_lines.append(self._format_conflicts_section(conflicts))
        else:
            report_lines.append(f"{self.emojis['success']} {self.colors['success']}No conflicts detected!{self.colors['reset']}")
        
        report_lines.append("")
        
        # Compatible combinations
        if result.get('compatible_combinations'):
            report_lines.append(self._format_compatible_section(result['compatible_combinations']))
            report_lines.append("")
        
        # Recommendations
        if result.get('recommendations'):
            report_lines.append(self._format_recommendations_section(result['recommendations']))
            report_lines.append("")
        
        # Overall assessment
        if result.get('overall_assessment'):
            report_lines.append(self._format_assessment_section(result['overall_assessment']))
        
        # Error handling
        if result.get('error'):
            report_lines.append(f"\n{self.colors['high']}⚠️ Analysis Error: {result['error']}{self.colors['reset']}")
        
        return "\n".join(report_lines)
    
    def _format_header(self, result: Dict[str, Any]) -> str:
        """Format the report header."""
        tool_count = result.get('tool_count', 0)
        conflict_count = len(result.get('conflicts', []))
        analysis_type = result.get('analysis_type', 'unknown')
        
        header = f"AI Tool Conflict Analysis Report"
        header += "\n" + "=" * 50
        header += f"\nTools Analyzed: {tool_count}"
        header += f"\nConflicts Found: {conflict_count}"
        
        # Show analysis type information
        if analysis_type == 'static_only':
            header += f"\nAnalysis Type: Static Rules Only (no API key)"
        elif analysis_type == 'hybrid':
            static_count = result.get('static_conflicts_count', 0)
            ai_count = result.get('ai_conflicts_count', 0)
            header += f"\nAnalysis Type: Hybrid (Static: {static_count}, AI: {ai_count})"
        elif analysis_type == 'static_fallback':
            header += f"\nAnalysis Type: Static Rules (AI analysis failed)"
        
        return header
    
    def _format_tools_section(self, result: Dict[str, Any]) -> str:
        """Format the tools analyzed section."""
        tools = result.get('tools_analyzed', [])
        if not tools:
            return ""
        
        section = f"{self.colors['info']}Tools Analyzed:{self.colors['reset']}"
        for i, tool in enumerate(tools, 1):
            section += f"\n  {i}. {tool}"
        
        return section
    
    def _format_conflicts_section(self, conflicts: List[Dict[str, Any]]) -> str:
        """Format the conflicts section."""
        if not conflicts:
            return ""
        
        section = f"{self.colors['info']}Conflicts Detected:{self.colors['reset']}\n"
        
        for i, conflict in enumerate(conflicts, 1):
            section += self._format_single_conflict(conflict, i)
            section += "\n"
        
        return section.rstrip()
    
    def _format_single_conflict(self, conflict: Dict[str, Any], index: int) -> str:
        """Format a single conflict."""
        severity = conflict.get('severity', 'medium').lower()
        conflict_type = conflict.get('type', 'unknown')
        tools_involved = conflict.get('tools_involved', [])
        description = conflict.get('description', 'No description available')
        mitigation = conflict.get('mitigation', 'No mitigation suggested')
        confidence = conflict.get('confidence', 'medium')
        
        # Get appropriate color
        color = self.colors.get(severity, self.colors['info'])
        
        conflict_text = f"\n{index}. {color}{severity.upper()} - {conflict_type.replace('_', ' ').title()}{self.colors['reset']}"
        
        if tools_involved:
            conflict_text += f"\n   Tools: {' <-> '.join(tools_involved)}"
        
        conflict_text += f"\n   Issue: {description}"
        
        if conflict.get('potential_issues'):
            conflict_text += f"\n   Impact: {conflict['potential_issues']}"
        
        conflict_text += f"\n   {self.colors['success']}Solution: {mitigation}{self.colors['reset']}"
        conflict_text += f"\n   Confidence: {confidence}"
        
        return conflict_text
    
    def _format_compatible_section(self, compatible: List[Dict[str, Any]]) -> str:
        """Format compatible combinations section."""
        if not compatible:
            return ""
        
        section = f"{self.colors['success']}Compatible Combinations:{self.colors['reset']}\n"
        
        for combo in compatible:
            tools = combo.get('tools', [])
            reason = combo.get('reason', 'No reason provided')
            section += f"\n  • {' + '.join(tools)}"
            section += f"\n    {reason}"
        
        return section
    
    def _format_recommendations_section(self, recommendations: List[str]) -> str:
        """Format recommendations section."""
        if not recommendations:
            return ""
        
        section = f"{self.colors['info']}Recommendations:{self.colors['reset']}\n"
        
        for i, recommendation in enumerate(recommendations, 1):
            section += f"\n  {i}. {recommendation}"
        
        return section
    
    def _format_assessment_section(self, assessment: str) -> str:
        """Format overall assessment section."""
        return f"{self.colors['info']}Overall Assessment:{self.colors['reset']}\n{assessment}"
    
    def _generate_json_report(self, result: Dict[str, Any]) -> str:
        """Generate JSON formatted report."""
        # Clean up the result for JSON output
        json_result = result.copy()
        
        # Remove any non-serializable fields
        if 'analysis_timestamp' not in json_result:
            from datetime import datetime
            json_result['analysis_timestamp'] = datetime.now().isoformat()
        
        return json.dumps(json_result, indent=2, ensure_ascii=False)
    
    def print_summary(self, analysis_result: Dict[str, Any]):
        """Print a quick summary of the analysis."""
        conflicts = analysis_result.get('conflicts', [])
        tool_count = analysis_result.get('tool_count', 0)
        
        if not conflicts:
            print(f"{self.colors['success']}Great! No conflicts detected between {tool_count} tools.{self.colors['reset']}")
        else:
            high_conflicts = len([c for c in conflicts if c.get('severity') == 'high'])
            medium_conflicts = len([c for c in conflicts if c.get('severity') == 'medium'])
            low_conflicts = len([c for c in conflicts if c.get('severity') == 'low'])
            
            print(f"Found {len(conflicts)} potential conflicts:")
            if high_conflicts:
                print(f"  {self.colors['high']}HIGH: {high_conflicts} conflicts{self.colors['reset']}")
            if medium_conflicts:
                print(f"  {self.colors['medium']}MEDIUM: {medium_conflicts} conflicts{self.colors['reset']}")
            if low_conflicts:
                print(f"  {self.colors['low']}LOW: {low_conflicts} conflicts{self.colors['reset']}")
    
    def export_to_file(self, analysis_result: Dict[str, Any], filename: str, format_type: str = 'human'):
        """Export report to a file."""
        try:
            report = self.generate_report(analysis_result, format_type)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"Report exported to {filename}")
            
        except Exception as e:
            print(f"{self.colors['high']}Error exporting report: {e}{self.colors['reset']}")


def format_conflict_summary(conflicts: List[Dict[str, Any]]) -> str:
    """Create a brief summary of conflicts."""
    if not conflicts:
        return "No conflicts detected"
    
    severity_counts = {}
    for conflict in conflicts:
        severity = conflict.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    summary_parts = []
    for severity in ['high', 'medium', 'low']:
        count = severity_counts.get(severity, 0)
        if count > 0:
            summary_parts.append(f"{count} {severity}")
    
    return f"{len(conflicts)} conflicts ({', '.join(summary_parts)})"