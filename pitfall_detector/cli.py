"""Command-line interface for AI Pitfall Detector."""

import click
import sys
import os
from typing import List, Dict, Any
from pathlib import Path

from .config import config
from .github import GitHubClient, ToolExtractor
from .analyzer import ConflictAnalyzer
from .reporter import ConflictReporter
from .environment_scanner import EnvironmentScanner
from .interactive_workflow import InteractiveWorkflow


def safe_str(text, max_length=None):
    """Safely encode string for console output, handling Unicode issues."""
    if not text:
        return "N/A"
    
    # Remove or replace problematic Unicode characters
    safe_text = text.encode('ascii', errors='ignore').decode('ascii')
    
    if max_length and len(safe_text) > max_length:
        safe_text = safe_text[:max_length] + "..."
    
    return safe_text


class ToolManager:
    """Manages the list of tools for analysis."""
    
    def __init__(self):
        self.tools = config.load_tools()
    
    def add_tool(self, url: str) -> Dict[str, Any]:
        """Add a tool from GitHub URL."""
        github_client = GitHubClient()
        extractor = ToolExtractor(github_client)
        
        # Validate URL first
        is_valid, error_msg = github_client.validate_url(url)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Extract tool information
        tool_info = extractor.extract_tool_info(url)
        tool_name = tool_info['name']
        
        # Store tool info
        self.tools[tool_name] = tool_info
        config.save_tools(self.tools)
        
        return tool_info
    
    def remove_tool(self, name: str) -> bool:
        """Remove a tool by name."""
        if name in self.tools:
            del self.tools[name]
            config.save_tools(self.tools)
            return True
        return False
    
    def list_tools(self) -> Dict[str, Any]:
        """List all added tools."""
        return self.tools.copy()
    
    def clear_tools(self):
        """Clear all tools."""
        self.tools = {}
        config.save_tools(self.tools)
    
    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get tools as a list for analysis."""
        return list(self.tools.values())


# Global tool manager
tool_manager = ToolManager()


def show_getting_started():
    """Show getting started guide for new users."""
    click.echo("AI Pitfall Detector")
    click.echo("Don't step into the same pit twice - Detect conflicts between AI tools\n")
    
    # Check if user has any tools or API key configured
    tools = tool_manager.list_tools()
    api_key = config.get_api_key()
    
    if not api_key and len(tools) == 0:
        # First time user
        click.echo("Welcome! Looks like this is your first time using AI Pitfall Detector.")
        click.echo("Let's get you set up:")
        click.echo()
        click.echo("Quick Setup:")
        click.echo("  1. ai-pitfall init     # Set up API key (optional)")
        click.echo("  2. ai-pitfall add      # Add AI tools to analyze")
        click.echo("  3. ai-pitfall analyze  # Check for conflicts")
        click.echo()
        
        if click.confirm("Would you like to start the setup now?", default=True):
            click.echo()
            import sys
            sys.argv = ['ai-pitfall', 'init']
            from . import cli
            cli.cli.main(standalone_mode=False)
    
    elif not api_key:
        # Has tools but no API key
        click.echo(f"You have {len(tools)} tools configured")
        click.echo("Consider setting up an API key for enhanced AI-powered analysis:")
        click.echo("   ai-pitfall init")
        click.echo()
        click.echo("Or analyze with static rules only:")
        click.echo("   ai-pitfall analyze")
    
    elif len(tools) == 0:
        # Has API key but no tools
        click.echo("API key configured")
        click.echo("Ready to add tools for analysis:")
        click.echo("   ai-pitfall add")
    
    else:
        # Everything set up
        click.echo(f"Setup complete! {len(tools)} tools ready for analysis")
        click.echo()
        click.echo("Available commands:")
        click.echo("   ai-pitfall add      # Add more tools")
        click.echo("   ai-pitfall analyze  # Analyze conflicts")
        click.echo("   ai-pitfall list     # Show added tools")
        click.echo("   ai-pitfall --help   # Full help")
    
    click.echo()
    click.echo("Example tools to try:")
    click.echo("   - streamlit/streamlit")
    click.echo("   - gradio-app/gradio")
    click.echo("   - langchain-ai/langchain")


@click.group(invoke_without_command=True)
@click.version_option(version="0.1.0", prog_name="ai-pitfall")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose):
    """AI Pitfall Detector - Analyze conflicts between AI tools before installation."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    config.set('output.verbose', verbose)
    
    # If no command provided, show getting started guide
    if ctx.invoked_subcommand is None:
        show_getting_started()


@cli.command()
@click.argument('github_url', required=False)
@click.option('--force', '-f', is_flag=True, help='Force add even if tool already exists')
@click.option('--batch', '-b', is_flag=True, help='Batch mode - add multiple tools at once')
@click.pass_context
def add(ctx, github_url, force, batch):
    """Add AI tool(s) from GitHub URL for analysis."""
    verbose = ctx.obj.get('verbose', False)
    
    # Interactive mode when no URL provided
    if not github_url:
        click.echo("Add AI Tools for Analysis")
        click.echo("You can add tools one by one or in batch mode.\n")
        
        if batch:
            click.echo("Batch Mode - Enter multiple GitHub URLs")
            click.echo("Press Enter on empty line when done.\n")
            urls = []
            while True:
                url = click.prompt(f"GitHub URL #{len(urls)+1} (or press Enter to finish)", default="", show_default=False)
                if not url:
                    break
                urls.append(url)
            
            if not urls:
                click.echo("No URLs provided. Exiting.")
                return
                
            # Process all URLs
            for i, url in enumerate(urls, 1):
                click.echo(f"\n[{i}/{len(urls)}] Processing {url}...")
                try:
                    _add_single_tool(url, force, verbose)
                except Exception as e:
                    click.echo(f"Failed to add {url}: {e}", err=True)
                    
        else:
            # Single tool mode
            click.echo("Examples:")
            click.echo("  - https://github.com/streamlit/streamlit")
            click.echo("  - https://github.com/gradio-app/gradio")
            click.echo("  - github.com/langchain-ai/langchain (also works)\n")
            
            github_url = click.prompt('Enter GitHub URL of the AI tool', type=str)
            _add_single_tool(github_url, force, verbose)
    else:
        # Direct URL provided
        _add_single_tool(github_url, force, verbose)


def _add_single_tool(github_url: str, force: bool, verbose: bool):
    """Helper function to add a single tool."""
    try:
        if verbose:
            click.echo("   Validating GitHub URL...")
        
        tool_info = tool_manager.add_tool(github_url)
        
        click.echo(f"Added {tool_info['name']}")
        if verbose:
            click.echo(f"   Description: {tool_info.get('description', 'No description')}")
            click.echo(f"   Stars: {tool_info.get('stars', 0)}")
            click.echo(f"   Language: {tool_info.get('language', 'Unknown')}")
            
        # Show current tool count
        total_tools = len(tool_manager.list_tools())
        click.echo(f"Total tools: {total_tools}")
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        raise


@cli.command()
@click.argument('tool_name')
def remove(tool_name):
    """Remove a tool by name."""
    if tool_manager.remove_tool(tool_name):
        click.echo(f"Removed {tool_name}")
        total_tools = len(tool_manager.list_tools())
        click.echo(f"Total tools: {total_tools}")
    else:
        click.echo(f"Tool '{tool_name}' not found")
        sys.exit(1)


@cli.command(name='list')
@click.option('--format', 'output_format', type=click.Choice(['human', 'json']), 
              default='human', help='Output format')
def list_tools(output_format):
    """List all added tools."""
    tools = tool_manager.list_tools()
    
    if not tools:
        click.echo("No tools added yet. Use 'ai-pitfall add <github-url>' to add tools.")
        return
    
    if output_format == 'json':
        import json
        click.echo(json.dumps(tools, indent=2))
    else:
        click.echo(f"Added Tools ({len(tools)}):")
        click.echo("=" * 40)
        
        for name, tool_info in tools.items():
            click.echo(f"\n{name}")
            click.echo(f"   URL: {tool_info.get('url', 'N/A')}")
            click.echo(f"   Description: {safe_str(tool_info.get('description', 'No description'), 100)}")
            if tool_info.get('stars'):
                click.echo(f"   Stars: {tool_info['stars']}")
            
            # Show categories if available
            categories = tool_info.get('metadata', {}).get('categories', [])
            if categories:
                click.echo(f"   Categories: {', '.join(categories)}")


@cli.command()
@click.option('--format', 'output_format', type=click.Choice(['human', 'json']), 
              default='human', help='Output format')
@click.option('--export', type=click.Path(), help='Export report to file')
@click.option('--no-colors', is_flag=True, help='Disable colored output')
@click.pass_context
def analyze(ctx, output_format, export, no_colors):
    """Analyze conflicts between added tools."""
    verbose = ctx.obj.get('verbose', False)
    
    tools_list = tool_manager.get_tools_list()
    
    if len(tools_list) < 2:
        click.echo("Need at least 2 tools to analyze conflicts.")
        click.echo()
        
        current_count = len(tools_list)
        needed = 2 - current_count
        
        if current_count == 0:
            click.echo("No tools added yet. Let's add some tools first!")
            if click.confirm("Would you like to add tools now?", default=True):
                ctx.invoke(add)
                # Re-check after adding
                tools_list = tool_manager.get_tools_list()
                if len(tools_list) < 2:
                    click.echo(f"Still need {2 - len(tools_list)} more tools for analysis.")
                    return
            else:
                click.echo("   Use 'ai-pitfall add' to add tools, then run 'ai-pitfall analyze'")
                return
        else:
            click.echo(f"Current tools: {current_count}")
            click.echo(f"Need {needed} more tool(s) for analysis.")
            if click.confirm("Would you like to add more tools now?", default=True):
                ctx.invoke(add)
                # Re-check after adding
                tools_list = tool_manager.get_tools_list()
                if len(tools_list) < 2:
                    click.echo(f"Still need {2 - len(tools_list)} more tools for analysis.")
                    return
            else:
                click.echo("   Use 'ai-pitfall add' to add more tools.")
                return
    
    try:
        click.echo(f"Analyzing conflicts between {len(tools_list)} tools...")
        
        if verbose:
            tool_names = [tool['name'] for tool in tools_list]
            click.echo(f"Tools: {', '.join(tool_names)}")
        
        # Initialize analyzer
        analyzer = ConflictAnalyzer()
        
        if verbose:
            click.echo("Sending to AI for analysis...")
        
        # Perform analysis
        analysis_result = analyzer.analyze_tool_conflicts(tools_list)
        
        # Format and display results
        use_colors = not no_colors and output_format == 'human'
        reporter = ConflictReporter(use_colors=use_colors)
        
        if verbose:
            click.echo("Analysis complete. Generating report...")
        
        # Generate report
        report = reporter.generate_report(analysis_result, output_format)
        
        # Display report
        click.echo("\n" + report)
        
        # Export if requested
        if export:
            reporter.export_to_file(analysis_result, export, output_format)
        
        # Print summary
        if output_format == 'human':
            click.echo("\n" + "="*50)
            reporter.print_summary(analysis_result)
        
    except Exception as e:
        click.echo(f"Analysis failed: {safe_str(str(e))}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt='Are you sure you want to clear all tools?')
def clear():
    """Clear all added tools."""
    tool_manager.clear_tools()
    click.echo("All tools cleared")


@cli.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), 
              help='Specific project directory to scan (default: current directory)')
@click.option('--format', 'output_format', type=click.Choice(['human', 'json']), 
              default='human', help='Output format')
@click.option('--auto-add', is_flag=True, 
              help='Automatically add detected tools to the analysis list')
@click.pass_context
def scan(ctx, project_path, output_format, auto_add):
    """Scan current environment for installed AI tools and services."""
    verbose = ctx.obj.get('verbose', False)
    
    if not project_path:
        import os
        project_path = os.getcwd()
    
    try:
        click.echo("Scanning environment for AI tools...")
        if verbose:
            click.echo(f"Scanning project directory: {project_path}")
        
        # Initialize scanner
        scanner = EnvironmentScanner()
        
        # Perform comprehensive scan
        scan_results = scanner.scan_all(project_path=project_path)
        
        # Display results
        if output_format == 'json':
            import json
            click.echo(json.dumps(scan_results, indent=2))
        else:
            _display_scan_results(scan_results, verbose)
        
        # Auto-add detected tools if requested
        if auto_add and scan_results.get('detected_ai_tools'):
            _auto_add_detected_tools(scan_results['detected_ai_tools'])
            
    except Exception as e:
        click.echo(f"Environment scan failed: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
def init():
    """Interactive setup wizard for first-time users."""
    click.echo("Welcome to AI Pitfall Detector!")
    click.echo("Let's set up your environment for conflict analysis.\n")
    
    # Check if already configured
    current_key = config.get_api_key()
    if current_key:
        if click.confirm(f"API key already configured. Reconfigure?", default=False):
            pass
        else:
            click.echo("Setup already complete. Use 'ai-pitfall add' to start adding tools.")
            return
    
    # API Provider selection
    click.echo("Step 1: Choose your AI provider")
    click.echo("1. OpenAI (recommended)")
    click.echo("2. Skip AI analysis (use static rules only)")
    
    choice = click.prompt("Select option", type=click.IntRange(1, 2), default=1)
    
    if choice == 1:
        # OpenAI setup
        click.echo("\nOpenAI API Key Setup")
        click.echo("You can get your API key from: https://platform.openai.com/api-keys")
        
        api_key = click.prompt("Enter your OpenAI API key", hide_input=True)
        
        # Validate API key format
        if not api_key.startswith('sk-'):
            click.echo("Warning: API key doesn't look like OpenAI format (should start with 'sk-')")
            if not click.confirm("Continue anyway?", default=False):
                return
        
        config.set('api.provider', 'openai')
        config.set('api.api_key', api_key)
        config.set('api.model', 'gpt-3.5-turbo')
        
        click.echo("OpenAI API configured successfully!")
    else:
        click.echo("Configured for static analysis only (no API key required)")
    
    click.echo("\nSetup complete! Next steps:")
    click.echo("  - Add tools: ai-pitfall add")
    click.echo("  - Analyze conflicts: ai-pitfall analyze")
    click.echo("  - Quick help: ai-pitfall --help")


@cli.command()
@click.option('--provider', type=click.Choice(['openai', 'anthropic']), 
              help='AI provider (openai or anthropic)')
@click.option('--api-key', help='API key for the AI provider')
@click.option('--model', help='Model to use (e.g., gpt-3.5-turbo)')
@click.option('--show', is_flag=True, help='Show current configuration')
def config_cmd(provider, api_key, model, show):
    """Configure AI Pitfall Detector settings."""
    
    if show:
        click.echo("Current Configuration:")
        click.echo(f"   AI Provider: {config.get('api.provider', 'openai')}")
        click.echo(f"   Model: {config.get('api.model', 'gpt-3.5-turbo')}")
        
        # Don't show full API key for security
        current_key = config.get_api_key()
        if current_key:
            masked_key = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "***"
            click.echo(f"   API Key: {masked_key}")
        else:
            click.echo("   API Key: Not set")
        
        click.echo(f"   Config Location: {config.config_file}")
        return
    
    # Update configuration
    if provider:
        config.set('api.provider', provider)
        click.echo(f"Set AI provider to {provider}")
    
    if api_key:
        config.set('api.api_key', api_key)
        click.echo("API key updated")
    
    if model:
        config.set('api.model', model)
        click.echo(f"Set model to {model}")
    
    if not any([provider, api_key, model]):
        click.echo("No configuration changes specified. Use --help for options.")


@cli.command()
@click.argument('github_urls', nargs=-1, required=True)
@click.option('--format', 'output_format', type=click.Choice(['human', 'json']), 
              default='human', help='Output format')
@click.pass_context
def quick_analyze(ctx, github_urls, output_format):
    """Quick analysis of tools without adding them permanently."""
    verbose = ctx.obj.get('verbose', False)
    
    if len(github_urls) < 2:
        click.echo("Need at least 2 GitHub URLs for analysis.")
        sys.exit(1)
    
    try:
        click.echo(f"Quick analysis of {len(github_urls)} tools...")
        
        # Extract tool information
        github_client = GitHubClient()
        extractor = ToolExtractor(github_client)
        tools_list = []
        
        for url in github_urls:
            if verbose:
                click.echo(f"   Processing {url}...")
            
            tool_info = extractor.extract_tool_info(url)
            tools_list.append(tool_info)
        
        # Perform analysis
        analyzer = ConflictAnalyzer()
        analysis_result = analyzer.analyze_tool_conflicts(tools_list)
        
        # Display results
        reporter = ConflictReporter(use_colors=(output_format == 'human'))
        report = reporter.generate_report(analysis_result, output_format)
        
        click.echo("\n" + report)
        
        if output_format == 'human':
            click.echo("\n" + "="*50)
            reporter.print_summary(analysis_result)
        
    except Exception as e:
        click.echo(f"Quick analysis failed: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _display_scan_results(scan_results: Dict, verbose: bool):
    """Display scan results in human-readable format."""
    click.echo("\nEnvironment Scan Results")
    click.echo("=" * 50)
    
    # Detected AI Tools Summary
    detected_tools = scan_results.get('detected_ai_tools', [])
    click.echo(f"\nDetected AI Tools: {len(detected_tools)}")
    if detected_tools:
        for tool in detected_tools:
            click.echo(f"\n  {tool['name']}")
            click.echo(f"    Status: {tool.get('status', 'unknown')}")
            if tool.get('versions'):
                versions = list(set(tool['versions']))  # Remove duplicates
                versions = [v for v in versions if v != 'unknown']
                if versions:
                    click.echo(f"    Version(s): {', '.join(versions)}")
            
            methods = list(set(tool.get('detection_methods', [])))
            click.echo(f"    Detected via: {', '.join(methods)}")
            
            if tool.get('ports'):
                ports = [str(p) for p in tool['ports'] if p]
                if ports:
                    click.echo(f"    Ports: {', '.join(ports)}")
            
            # Show confidence score for dynamic agent detection
            if 'dynamic_agent_detection' in methods and tool.get('confidence_score'):
                click.echo(f"    Confidence: {tool['confidence_score']:.1f}/10.0")
            
            # Show framework type for agent frameworks
            if tool.get('framework_type') == 'AI Agent Framework':
                click.echo(f"    Type: {tool['framework_type']}")
    
    # Python Packages
    python_packages = scan_results.get('python_packages', {})
    if python_packages:
        click.echo(f"\nInstalled Python AI Packages: {len(python_packages)}")
        if verbose:
            for name, info in python_packages.items():
                click.echo(f"  {name} v{info.get('version', 'unknown')}")
    
    # Running Services
    running_services = scan_results.get('running_services', {})
    if running_services:
        click.echo(f"\nRunning AI Services: {len(running_services)}")
        if verbose:
            for name, info in running_services.items():
                port = info.get('port')
                service = info.get('service', 'unknown')
                click.echo(f"  {service} on port {port}")
    
    # Project Files
    project_files = scan_results.get('project_files', {})
    if project_files:
        file_count = sum(1 for info in project_files.values() if 'tool' in info)
        if file_count > 0:
            click.echo(f"\nProject Configuration Files: {file_count}")
            if verbose:
                for key, info in project_files.items():
                    if 'tool' in info:
                        method = info.get('detection_method', 'file').replace('_', ' ')
                        click.echo(f"  {info['tool']} (found in {method})")
    
    # Docker Containers
    docker_containers = scan_results.get('docker_containers', {})
    if docker_containers and not any('error' in key for key in docker_containers.keys()):
        click.echo(f"\nDocker AI Containers: {len(docker_containers)}")
        if verbose:
            for name, info in docker_containers.items():
                if 'tool' in info:
                    click.echo(f"  {info['tool']} ({info.get('container_name', 'unknown')})")
    
    # Environment Variables
    env_vars = scan_results.get('environment_variables', {})
    if env_vars:
        click.echo(f"\nAI-related Environment Variables: {len(env_vars)}")
        if verbose:
            for var, value in env_vars.items():
                click.echo(f"  {var}: {value}")
    
    # Conda Environments
    conda_envs = scan_results.get('conda_environments', {})
    if conda_envs and not any('error' in key for key in conda_envs.keys()):
        click.echo(f"\nConda AI Packages: {len(conda_envs)}")
        if verbose:
            for key, info in conda_envs.items():
                if 'tool' in info:
                    env_name = info.get('environment', 'unknown')
                    click.echo(f"  {info['tool']} in {env_name}")
    
    # Framework Detection
    frameworks = scan_results.get('framework_detection', {})
    if frameworks:
        click.echo(f"\nDetected AI Frameworks: {len(frameworks)}")
        if verbose:
            for key, info in frameworks.items():
                if 'tool' in info:
                    click.echo(f"  {info['tool']} - {info.get('description', 'AI Framework')}")
                    indicators = info.get('framework_indicators', {})
                    if indicators.get('directories_found'):
                        click.echo(f"    Directories: {', '.join(indicators['directories_found'])}")
                    if indicators.get('files_found'):
                        files = indicators['files_found'][:3]  # Show first 3 files
                        click.echo(f"    Key files: {', '.join(files)}")
                        if len(indicators['files_found']) > 3:
                            click.echo(f"    ... and {len(indicators['files_found']) - 3} more files")
    
    # Dynamic Agent Detection
    dynamic_agents = scan_results.get('dynamic_agent_detection', [])
    if dynamic_agents:
        click.echo(f"\nDynamic AI Agent Frameworks: {len(dynamic_agents)}")
        for agent_info in dynamic_agents:
            framework_name = agent_info.get('name', 'Unknown Framework')
            confidence = agent_info.get('confidence', 0)
            click.echo(f"  {framework_name} (confidence: {confidence:.1f}/1.0)")
            
            if verbose:
                evidence = agent_info.get('evidence', {})
                
                # Display structure evidence
                structure = evidence.get('structure', {})
                if structure.get('agent_directories'):
                    dirs = structure['agent_directories'][:3]
                    click.echo(f"    Agent directories: {', '.join(dirs)}")
                    if len(structure['agent_directories']) > 3:
                        click.echo(f"    ... and {len(structure['agent_directories']) - 3} more")
                
                if structure.get('agent_files'):
                    files = [os.path.basename(f) for f in structure['agent_files'][:3]]
                    click.echo(f"    Agent files: {', '.join(files)}")
                    if len(structure['agent_files']) > 3:
                        click.echo(f"    ... and {len(structure['agent_files']) - 3} more")
                
                # Display code evidence
                code = evidence.get('code', {})
                if code.get('agent_classes'):
                    class_count = len(code['agent_classes'])
                    click.echo(f"    Agent classes: {class_count} detected")
                
                if code.get('agent_functions'):
                    func_count = len(code['agent_functions'])
                    click.echo(f"    Agent functions: {func_count} detected")
                
                # Display config evidence
                config_evidence = evidence.get('config', {})
                if config_evidence.get('agent_configs'):
                    config_count = len(config_evidence['agent_configs'])
                    click.echo(f"    Configuration files: {config_count} detected")
                
                # Show suggested GitHub searches
                suggested_searches = agent_info.get('suggested_github_search', [])
                if suggested_searches:
                    search_terms = suggested_searches[:2]
                    click.echo(f"    Similar frameworks: {', '.join(search_terms)}")


def _auto_add_detected_tools(detected_tools: List[Dict]):
    """Automatically add detected tools to the analysis list."""
    added_count = 0
    skipped_count = 0
    
    click.echo(f"\nAuto-adding {len(detected_tools)} detected tools...")
    
    for tool in detected_tools:
        tool_name = tool['name']
        
        # Step 1: Check static rules first
        from .static_rules import KNOWN_AI_TOOLS
        github_url = None
        
        if tool_name in KNOWN_AI_TOOLS:
            github_url = KNOWN_AI_TOOLS[tool_name].get('github_url')
            if github_url:
                click.echo(f"  Found {tool_name} in static rules")
        
        # Step 2: If not in static rules, try dynamic GitHub resolution for agent frameworks
        if not github_url and tool.get('framework_type') == 'AI Agent Framework':
            click.echo(f"  Searching GitHub for {tool_name} using AI keywords...")
            from .dynamic_github_resolver import resolve_dynamic_framework_url
            github_url = resolve_dynamic_framework_url(tool)
            if github_url:
                # Extract URL from potential list/dict structure
                if isinstance(github_url, list) and github_url:
                    actual_url = github_url[0].get('html_url', str(github_url[0])) if isinstance(github_url[0], dict) else str(github_url[0])
                elif isinstance(github_url, dict):
                    actual_url = github_url.get('html_url', str(github_url))
                else:
                    actual_url = str(github_url)
                click.echo(f"  Found via dynamic search: {actual_url}")
                github_url = actual_url  # Use the cleaned URL
            else:
                click.echo(f"  No GitHub URL found via dynamic search")
        
        # Step 3: Add tool if we have a GitHub URL
        if github_url:
            try:
                # Check if already added
                existing_tools = tool_manager.list_tools()
                tool_key = None
                # Find the actual key used in storage (could be different from name)
                for key in existing_tools.keys():
                    if key.lower() == tool_name.lower() or tool_name.lower() in key.lower():
                        tool_key = key
                        break
                
                if not tool_key:
                    tool_info = tool_manager.add_tool(github_url)
                    click.echo(f"  Added {tool_name}")
                    added_count += 1
                else:
                    click.echo(f"  Skipped {tool_name} (already in list as {tool_key})")
                    skipped_count += 1
            except Exception as e:
                click.echo(f"  Failed to add {tool_name}: {e}", err=True)
                skipped_count += 1
        else:
            if tool.get('framework_type') == 'AI Agent Framework':
                click.echo(f"  Skipped {tool_name} (dynamic framework, no GitHub URL found)")
            else:
                click.echo(f"  Skipped {tool_name} (no GitHub URL available)")
            skipped_count += 1
    
    click.echo(f"\nAuto-add complete: {added_count} added, {skipped_count} skipped")
    
    # Suggest analysis if tools were added
    if added_count > 0:
        total_tools = len(tool_manager.list_tools())
        click.echo(f"Total tools in list: {total_tools}")
        if total_tools >= 2:
            click.echo("\nReady for analysis! Run: ai-pitfall analyze")


@cli.command()
@click.option('--project-path', '-p', type=click.Path(exists=True), 
              help='Project directory to analyze (default: current directory)')
def interactive(project_path):
    """Launch interactive workflow for comprehensive AI tool conflict analysis.
    
    This command provides a step-by-step guided process:
    1. Automatically detect installed AI tools in your project
    2. Allow you to confirm and supplement the detected tools
    3. Let you specify tools you plan to install  
    4. Configure API keys for enhanced analysis
    5. Generate detailed conflict analysis and recommendations
    
    Perfect for project setup or when adding new AI tools to existing projects.
    """
    project_path = project_path or os.getcwd()
    
    try:
        # Launch interactive workflow
        workflow = InteractiveWorkflow(project_path)
        workflow.run()
        
    except KeyboardInterrupt:
        click.echo("\n\n⚠️ Interactive workflow interrupted. Your progress has been saved.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Interactive workflow failed: {e}", err=True)
        sys.exit(1)


@cli.command()  
@click.option('--project-path', '-p', type=click.Path(exists=True),
              help='Project directory to analyze (default: current directory)')
def smart_scan(project_path):
    """Smart scan: Detect tools and launch interactive workflow.
    
    This is an alias for the interactive command, providing the same
    comprehensive workflow with a more intuitive name.
    """
    project_path = project_path or os.getcwd()
    
    try:
        workflow = InteractiveWorkflow(project_path)
        workflow.run()
        
    except KeyboardInterrupt:
        click.echo("\n\n⚠️ Smart scan interrupted. Your progress has been saved.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Smart scan failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()