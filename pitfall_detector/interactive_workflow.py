"""Interactive workflow for AI Pitfall Detector."""

import os
import sys

# Ensure UTF-8 encoding on Windows
if sys.platform.startswith('win'):
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except (AttributeError, UnicodeEncodeError):
        # Fallback for environments that don't support UTF-8
        pass

import click

def safe_print(text: str) -> None:
    """Print text with fallback for encoding issues."""
    try:
        click.echo(text)
    except UnicodeEncodeError:
        # Remove emojis and problematic Unicode characters
        import re
        ascii_text = re.sub(r'[^\x00-\x7F]', '?', text)
        click.echo(ascii_text)
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

from .user_config import get_user_config
from .environment_scanner import EnvironmentScanner
from .analyzer import ConflictAnalyzer
from .reporter import ConflictReporter
from .dynamic_github_resolver import resolve_dynamic_framework_url


class InteractiveWorkflow:
    """Interactive workflow manager for complete conflict analysis."""
    
    def __init__(self, project_path: str):
        self.project_path = str(Path(project_path).resolve())
        self.config_manager = get_user_config()
        self.scanner = EnvironmentScanner()
        self.current_step = 0
        self.total_steps = 10
        
    def run(self):
        """Run the complete interactive workflow."""
        safe_print("🚀 AI Pitfall Detector - Interactive Workflow")
        safe_print("=" * 60)
        
        try:
            # Step 1: Welcome and setup
            self._step1_welcome()
            
            # Step 2-3: Scan and display detected tools
            detected_tools = self._step2_3_scan_and_display()
            
            # Step 4-6: Interactive confirmation and supplementation
            confirmed_tools = self._step4_6_confirm_and_supplement(detected_tools)
            
            # Step 7: Get target tools to install
            target_tools = self._step7_get_target_tools()
            
            # Step 8: API key configuration
            api_key = self._step8_configure_api_key()
            
            # Step 9-10: Analyze and report
            self._step9_10_analyze_and_report(confirmed_tools, target_tools, api_key)
            
            safe_print("\n✅ Interactive workflow completed successfully!")
            
        except KeyboardInterrupt:
            safe_print("\n\n⚠️  Workflow interrupted by user. Progress has been saved.")
        except Exception as e:
            safe_print(f"\n❌ Workflow failed: {e}")
            raise
    
    def _show_progress(self, step_name: str):
        """Show current progress."""
        self.current_step += 1
        progress = "█" * (self.current_step * 20 // self.total_steps)
        remaining = "░" * (20 - len(progress))
        safe_print(f"\n📊 Progress: [{progress}{remaining}] Step {self.current_step}/{self.total_steps}: {step_name}")
    
    def _step1_welcome(self):
        """Step 1: Welcome and project setup."""
        self._show_progress("Project Initialization")
        
        project_name = Path(self.project_path).name
        safe_print(f"📁 Current Project: {project_name}")
        safe_print(f"📂 Project Path: {self.project_path}")
        
        # Check if this project has been analyzed before
        project_config = self.config_manager.get_project_config(self.project_path)
        last_scan = project_config.get('last_scan_date')
        
        if last_scan:
            safe_print(f"📅 Last Scan: {last_scan[:19].replace('T', ' ')}")
            installed_count = len(project_config.get('installed_tools', []))
            if installed_count > 0:
                safe_print(f"🔧 Saved {installed_count} installed tool configurations")
        
        safe_print("\nPreparing to start scan analysis...")
    
    def _step2_3_scan_and_display(self) -> List[Dict[str, Any]]:
        """Steps 2-3: Scan project and display detected tools."""
        self._show_progress("Scanning Installed Tools")
        
        safe_print("🔍 Scanning AI tools and frameworks in your project...")
        
        with click.progressbar(length=100, label='Scan Progress') as bar:
            # Simulate progress updates
            bar.update(20)
            scan_results = self.scanner.scan_all(self.project_path)
            bar.update(50)
            
            # Update scan history
            self.config_manager.update_scan_history(self.project_path, scan_results)
            bar.update(30)
        
        detected_tools = scan_results.get('detected_ai_tools', [])
        
        self._show_progress("Displaying Detection Results")
        
        safe_print(f"\n🎯 Detected {len(detected_tools)} AI tools/frameworks:")
        safe_print("-" * 50)
        
        if not detected_tools:
            safe_print("❌ No AI tools detected")
            return []
        
        for i, tool in enumerate(detected_tools, 1):
            tool_name = tool.get('name', 'Unknown')
            status = tool.get('status', 'unknown')
            methods = ', '.join(tool.get('detection_methods', []))
            
            # Status emoji
            status_emoji = {
                'installed': '✅',
                'running': '🟢', 
                'detected': '🔍',
                'framework_detected': '🏗️',
                'agent_framework_detected': '🤖'
            }.get(status, '❓')
            
            safe_print(f"{i:2d}. {status_emoji} {tool_name}")
            safe_print(f"     Status: {status}")
            safe_print(f"     Detection method: {methods}")
            
            # Show additional info for certain tools
            if tool.get('confidence_score'):
                safe_print(f"     Confidence: {tool['confidence_score']:.1f}/1.0")
            
            versions = [v for v in tool.get('versions', []) if v != 'unknown']
            if versions:
                safe_print(f"     Version: {', '.join(versions)}")
            
            safe_print()
        
        return detected_tools
    
    def _step4_6_confirm_and_supplement(self, detected_tools: List[Dict]) -> List[Dict]:
        """Steps 4-6: Interactive confirmation and supplementation loop."""
        self._show_progress("Confirming Detection Results")
        
        # First, save detected tools to config
        for tool in detected_tools:
            tool_info = {
                'display_name': tool.get('name', 'Unknown'),
                'detection_method': ', '.join(tool.get('detection_methods', [])),
                'added_manually': False,
                'metadata': {
                    'status': tool.get('status'),
                    'versions': tool.get('versions', []),
                    'confidence_score': tool.get('confidence_score')
                }
            }
            self.config_manager.add_installed_tool(
                self.project_path, 
                tool.get('name', 'unknown'), 
                tool_info
            )
        
        confirmed_tools = detected_tools.copy()
        
        # Confirmation loop
        while True:
            safe_print("\n🤔 Confirm detection results:")
            missing = click.confirm("Are there any missing installed AI tools/frameworks?", default=False)
            
            if not missing:
                self._show_progress("Tool List Confirmation Complete")
                break
            
            # Get additional tools
            additional_tools = self._get_additional_tools()
            confirmed_tools.extend(additional_tools)
            
            # Show updated list
            safe_print(f"\n📋 Confirmed tool list ({len(confirmed_tools)} tools):")
            for i, tool in enumerate(confirmed_tools, 1):
                name = tool.get('name', 'Unknown')
                manual = "✋ Manually added" if tool.get('manually_added', False) else "🔍 Auto-detected"
                safe_print(f"  {i}. {name} ({manual})")
        
        return confirmed_tools
    
    def _get_additional_tools(self) -> List[Dict]:
        """Get additional tools from user input."""
        self._show_progress("Adding Missing Tools")
        
        additional_tools = []
        
        safe_print("\n📝 Please enter missing tool information:")
        safe_print("Tip: You can enter multiple tools separated by commas")
        safe_print("Format: tool_name[=GitHub_URL], tool_name2[=GitHub_URL2], ...")
        safe_print("Example: langchain=https://github.com/langchain-ai/langchain, streamlit")
        
        tools_input = click.prompt("\nEnter tools", type=str).strip()
        
        if not tools_input:
            return additional_tools
        
        # Parse multiple tools
        tools_list = [t.strip() for t in tools_input.split(',') if t.strip()]
        
        for tool_entry in tools_list:
            if '=' in tool_entry:
                tool_name, github_url = tool_entry.split('=', 1)
                tool_name = tool_name.strip()
                github_url = github_url.strip()
            else:
                tool_name = tool_entry.strip()
                github_url = ''
            
            if tool_name:
                # Try to resolve GitHub URL if not provided
                if not github_url:
                    safe_print(f"🔍 Searching for {tool_name}'s GitHub address...")
                    github_url = self._try_resolve_github_url(tool_name)
                
                tool_info = {
                    'name': tool_name.lower(),
                    'display_name': tool_name,
                    'github_url': github_url,
                    'manually_added': True,
                    'detection_methods': ['manual'],
                    'status': 'manually_added',
                    'added_date': datetime.now().isoformat()
                }
                
                additional_tools.append(tool_info)
                
                # Save to config
                config_tool_info = {
                    'display_name': tool_name,
                    'github_url': github_url,
                    'added_manually': True,
                    'detection_method': 'manual'
                }
                self.config_manager.add_installed_tool(self.project_path, tool_name, config_tool_info)
                
                if github_url:
                    safe_print(f"✅ Added: {tool_name} ({github_url})")
                else:
                    safe_print(f"✅ Added: {tool_name} (GitHub URL not found)")
        
        return additional_tools
    
    def _try_resolve_github_url(self, tool_name: str) -> str:
        """Try to resolve GitHub URL for a tool."""
        try:
            # Create a mock framework info for dynamic resolution
            framework_info = {
                'name': tool_name,
                'suggested_github_search': [
                    tool_name,
                    f"{tool_name} python",
                    f"{tool_name} ai tool",
                    f"{tool_name} framework"
                ]
            }
            
            url = resolve_dynamic_framework_url(framework_info)
            return url if url else ''
        except Exception:
            return ''
    
    def _step7_get_target_tools(self) -> List[Dict]:
        """Step 7: Get tools user wants to install."""
        self._show_progress("Getting Target Installation Tools")
        
        safe_print("\n🎯 Target Tools Configuration:")
        safe_print("Please enter AI tools/frameworks you plan to install")
        
        # Check saved target tools
        saved_targets = self.config_manager.get_target_tools(self.project_path)
        if saved_targets:
            safe_print(f"\n💾 Previously saved target tools ({len(saved_targets)} tools):")
            for i, tool in enumerate(saved_targets, 1):
                safe_print(f"  {i}. {tool.get('display_name', tool.get('name'))}")
            
            use_saved = click.confirm("Use saved target tool list?", default=True)
            if use_saved:
                # Ask if user wants to add more
                add_more = click.confirm("Add more target tools?", default=False)
                if not add_more:
                    return saved_targets
        
        target_tools = saved_targets.copy() if saved_targets else []
        
        safe_print("\n📝 Please enter tools you plan to install:")
        safe_print("Format: tool_name[=GitHub_URL], tool_name2[=GitHub_URL2], ...")
        safe_print("Example: CrewAI=https://github.com/joaomdmoura/crewAI, autogen")
        safe_print("Press Enter to skip this step")
        
        tools_input = click.prompt("Target tools", default='', show_default=False).strip()
        
        if tools_input:
            tools_list = [t.strip() for t in tools_input.split(',') if t.strip()]
            
            for tool_entry in tools_list:
                if '=' in tool_entry:
                    tool_name, github_url = tool_entry.split('=', 1)
                    tool_name = tool_name.strip()
                    github_url = github_url.strip()
                else:
                    tool_name = tool_entry.strip()
                    github_url = ''
                
                if tool_name:
                    # Try to resolve GitHub URL if not provided
                    if not github_url:
                        safe_print(f"🔍 Searching for {tool_name} GitHub URL...")
                        github_url = self._try_resolve_github_url(tool_name)
                    
                    # Save target tool
                    self.config_manager.add_target_tool(self.project_path, tool_name, github_url)
                    
                    target_tool = {
                        'name': tool_name.lower(),
                        'display_name': tool_name,
                        'github_url': github_url,
                        'added_date': datetime.now().isoformat()
                    }
                    
                    target_tools.append(target_tool)
                    
                    if github_url:
                        safe_print(f"🎯 Target tool: {tool_name} ({github_url})")
                    else:
                        safe_print(f"🎯 Target tool: {tool_name} (GitHub URL not found)")
        
        if target_tools:
            safe_print(f"\n📋 Total {len(target_tools)} tools planned for installation")
        else:
            safe_print("ℹ️  Skipped target tool configuration, will analyze conflicts between existing tools only")
        
        return target_tools
    
    def _step8_configure_api_key(self) -> Optional[str]:
        """Step 8: Configure API key for analysis."""
        self._show_progress("Configuring API Key")
        
        safe_print("\n🔑 API Key Configuration:")
        safe_print("AI conflict analysis requires LLM API support for more accurate analysis")
        
        # Check if API key is already configured
        openai_set = self.config_manager.get_api_key_status('openai')
        anthropic_set = self.config_manager.get_api_key_status('anthropic')
        
        if openai_set or anthropic_set:
            safe_print("✅ Detected configured API key")
            use_existing = click.confirm("Use existing API key?", default=True)
            if use_existing:
                return "configured"
        
        # Check environment variables
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if openai_key or anthropic_key:
            safe_print("✅ Detected API key in environment variables")
            return "environment"
        
        safe_print("\nChoose API key configuration method:")
        safe_print("1. Enter OpenAI API key")
        safe_print("2. Enter Anthropic Claude API key") 
        safe_print("3. Skip (use static rules analysis only)")
        
        choice = click.prompt("Please choose", type=click.Choice(['1', '2', '3']), default='3')
        
        if choice == '1':
            api_key = click.prompt("OpenAI API key", hide_input=True)
            if api_key.strip():
                # Set environment variable for this session
                os.environ['OPENAI_API_KEY'] = api_key.strip()
                self.config_manager.set_api_key_status('openai', True)
                safe_print("✅ OpenAI API key configured")
                return api_key.strip()
        elif choice == '2':
            api_key = click.prompt("Anthropic API key", hide_input=True)
            if api_key.strip():
                os.environ['ANTHROPIC_API_KEY'] = api_key.strip()
                self.config_manager.set_api_key_status('anthropic', True)
                safe_print("✅ Anthropic API key configured")
                return api_key.strip()
        
        safe_print("ℹ️  Skipped API key configuration, will use static rules for analysis")
        return None
    
    def _step9_10_analyze_and_report(self, confirmed_tools: List[Dict], target_tools: List[Dict], api_key: Optional[str]):
        """Steps 9-10: Analyze conflicts and generate report."""
        self._show_progress("Analyzing Potential Conflicts")
        
        safe_print("\n🔬 Starting conflict analysis...")
        
        # Combine all tools for analysis
        all_tools = confirmed_tools + target_tools
        
        if not all_tools:
            safe_print("⚠️  No tools to analyze")
            return
        
        # Create analyzer
        analyzer = ConflictAnalyzer()
        
        with click.progressbar(length=100, label='Analysis Progress') as bar:
            bar.update(25)
            
            # Analyze conflicts
            conflicts = analyzer.analyze_tools(all_tools)
            bar.update(50)
            
            # Generate report
            reporter = ConflictReporter()
            
            self._show_progress("Generating Analysis Report")
            
            # Interactive report display
            self._display_interactive_report(conflicts, confirmed_tools, target_tools)
            bar.update(25)
        
        # Generate static report file
        self._generate_static_report(conflicts, confirmed_tools, target_tools, analyzer)
    
    def _display_interactive_report(self, conflicts: List[Dict], installed_tools: List[Dict], target_tools: List[Dict]):
        """Display interactive conflict report."""
        safe_print("\n" + "=" * 60)
        safe_print("🎯 AI Tool Conflict Analysis Report")
        safe_print("=" * 60)
        
        # Summary
        safe_print(f"📊 Analysis Summary:")
        safe_print(f"   • Installed tools: {len(installed_tools)} tools")
        safe_print(f"   • Target installation tools: {len(target_tools)} tools")
        safe_print(f"   • Conflicts found: {len(conflicts)} conflicts")
        
        if not conflicts:
            safe_print("\n🎉 Congratulations! No potential conflicts found")
            safe_print("✅ Your tool configuration looks safe")
            return
        
        # Group conflicts by severity
        high_conflicts = [c for c in conflicts if c.get('severity') == 'high']
        medium_conflicts = [c for c in conflicts if c.get('severity') == 'medium'] 
        low_conflicts = [c for c in conflicts if c.get('severity') == 'low']
        
        # Display high severity conflicts first
        if high_conflicts:
            safe_print(f"\n🔴 High-Risk Conflicts ({len(high_conflicts)} conflicts):")
            for i, conflict in enumerate(high_conflicts, 1):
                safe_print(f"\n{i}. {conflict.get('description', 'Unknown conflict')}")
                safe_print(f"   Tools: {', '.join(conflict.get('tools_involved', []))}")
                safe_print(f"   Impact: {conflict.get('potential_issues', 'Unknown impact')}")
                safe_print(f"   Recommendation: {conflict.get('mitigation', 'No recommendation')}")
                
                if click.confirm("   View details?", default=False):
                    self._show_conflict_details(conflict)
        
        if medium_conflicts:
            safe_print(f"\n🟡 Medium-Risk Conflicts ({len(medium_conflicts)} conflicts):")
            for i, conflict in enumerate(medium_conflicts, 1):
                safe_print(f"\n{i}. {conflict.get('description', 'Unknown conflict')}")
                safe_print(f"   Tools: {', '.join(conflict.get('tools_involved', []))}")
                safe_print(f"   Recommendation: {conflict.get('mitigation', 'No recommendation')}")
        
        if low_conflicts:
            if click.confirm(f"\n🟢 Show low-risk conflicts ({len(low_conflicts)} conflicts)?", default=False):
                for i, conflict in enumerate(low_conflicts, 1):
                    safe_print(f"\n{i}. {conflict.get('description', 'Unknown conflict')}")
                    safe_print(f"   Tools: {', '.join(conflict.get('tools_involved', []))}")
        
        # Overall recommendation
        if high_conflicts:
            safe_print("\n⚠️  Recommendation: Please resolve high-risk conflicts first before installation")
        elif medium_conflicts:
            safe_print("\n💡 Recommendation: Pay attention to medium conflicts, be careful during configuration")
        else:
            safe_print("\n✅ Overall Assessment: Low conflict risk, safe to install")
    
    def _show_conflict_details(self, conflict: Dict):
        """Show detailed conflict information."""
        safe_print("   📋 Detailed Information:")
        safe_print(f"      Type: {conflict.get('type', 'Unknown')}")
        safe_print(f"      Confidence: {conflict.get('confidence', 'Unknown')}")
        safe_print(f"      Source: {conflict.get('source', 'Unknown')}")
        
        if 'additional_info' in conflict:
            safe_print(f"      Additional Info: {conflict['additional_info']}")
    
    def _generate_static_report(self, conflicts: List[Dict], installed_tools: List[Dict], target_tools: List[Dict], analyzer):
        """Generate static report file."""
        try:
            report_dir = Path(self.config_manager.get_report_directory())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = Path(self.project_path).name
            report_file = report_dir / f"conflict_report_{project_name}_{timestamp}.txt"
            
            reporter = ConflictReporter()
            
            # Generate detailed text report
            report_content = self._generate_report_content(conflicts, installed_tools, target_tools)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            safe_print(f"\n💾 Detailed report saved: {report_file}")
            
            if click.confirm("Open report file now?", default=False):
                try:
                    import webbrowser
                    webbrowser.open(str(report_file))
                except Exception:
                    safe_print(f"Please open manually: {report_file}")
        
        except Exception as e:
            safe_print(f"⚠️  Failed to save report: {e}")
    
    def _generate_report_content(self, conflicts: List[Dict], installed_tools: List[Dict], target_tools: List[Dict]) -> str:
        """Generate detailed report content."""
        lines = []
        lines.append("=" * 80)
        lines.append("AI Tool Conflict Analysis Report")
        lines.append("=" * 80)
        lines.append(f"Project Path: {self.project_path}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Analysis Tool: AI Pitfall Detector")
        lines.append("")
        
        # Summary section
        lines.append("📊 Analysis Summary")
        lines.append("-" * 40)
        lines.append(f"Installed Tools Count: {len(installed_tools)}")
        lines.append(f"Target Installation Tools Count: {len(target_tools)}")
        lines.append(f"Conflicts Detected: {len(conflicts)}")
        lines.append("")
        
        # Installed tools
        if installed_tools:
            lines.append("🔧 Installed Tools List")
            lines.append("-" * 40)
            for i, tool in enumerate(installed_tools, 1):
                name = tool.get('name', 'Unknown')
                status = tool.get('status', 'unknown')
                methods = ', '.join(tool.get('detection_methods', []))
                lines.append(f"{i:2d}. {name}")
                lines.append(f"    Status: {status}")
                lines.append(f"    Detection Method: {methods}")
                if tool.get('github_url'):
                    lines.append(f"    GitHub: {tool['github_url']}")
                lines.append("")
        
        # Target tools
        if target_tools:
            lines.append("🎯 Target Installation Tools List")
            lines.append("-" * 40)
            for i, tool in enumerate(target_tools, 1):
                name = tool.get('display_name', tool.get('name', 'Unknown'))
                lines.append(f"{i:2d}. {name}")
                if tool.get('github_url'):
                    lines.append(f"    GitHub: {tool['github_url']}")
                lines.append("")
        
        # Conflicts
        if conflicts:
            lines.append("⚠️  Conflict Analysis Results")
            lines.append("-" * 40)
            
            # Group by severity
            for severity, emoji in [('high', '🔴'), ('medium', '🟡'), ('low', '🟢')]:
                severity_conflicts = [c for c in conflicts if c.get('severity') == severity]
                if severity_conflicts:
                    lines.append(f"\n{emoji} {severity.upper()} SEVERITY CONFLICTS ({len(severity_conflicts)} found):")
                    lines.append("")
                    
                    for i, conflict in enumerate(severity_conflicts, 1):
                        lines.append(f"{i}. {conflict.get('description', 'Unknown conflict')}")
                        lines.append(f"   Type: {conflict.get('type', 'Unknown')}")
                        lines.append(f"   Affected Tools: {', '.join(conflict.get('tools_involved', []))}")
                        lines.append(f"   Potential Impact: {conflict.get('potential_issues', 'Unknown impact')}")
                        lines.append(f"   Mitigation: {conflict.get('mitigation', 'No recommendation')}")
                        lines.append(f"   Confidence: {conflict.get('confidence', 'Unknown')}")
                        lines.append(f"   Detection Source: {conflict.get('source', 'Unknown')}")
                        lines.append("")
        else:
            lines.append("🎉 Conflict Analysis Results")
            lines.append("-" * 40)
            lines.append("Congratulations! No potential conflicts detected.")
            lines.append("Your tool configuration appears safe for installation and use.")
            lines.append("")
        
        # Footer
        lines.append("-" * 80)
        lines.append("Report Notes:")
        lines.append("• This report is generated based on static rules and dynamic analysis")
        lines.append("• Please carefully read conflict descriptions and mitigation suggestions before installation")
        lines.append("• If you have questions, please refer to each tool's official documentation")
        lines.append("-" * 80)
        
        return "\n".join(lines)