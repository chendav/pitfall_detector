"""Command-line interface for AI Pitfall Detector."""

import click
import sys
from typing import List, Dict, Any
from pathlib import Path

from .config import config
from .github import GitHubClient, ToolExtractor
from .analyzer import ConflictAnalyzer
from .reporter import ConflictReporter


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


if __name__ == '__main__':
    cli()