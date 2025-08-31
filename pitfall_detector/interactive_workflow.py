"""Interactive workflow for AI Pitfall Detector."""

import os
import click
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
        click.echo("🚀 AI Pitfall Detector - Interactive Workflow")
        click.echo("=" * 60)
        
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
            
            click.echo("\n✅ Interactive workflow completed successfully!")
            
        except KeyboardInterrupt:
            click.echo("\n\n⚠️  Workflow interrupted by user. Progress has been saved.")
        except Exception as e:
            click.echo(f"\n❌ Workflow failed: {e}")
            raise
    
    def _show_progress(self, step_name: str):
        """Show current progress."""
        self.current_step += 1
        progress = "█" * (self.current_step * 20 // self.total_steps)
        remaining = "░" * (20 - len(progress))
        click.echo(f"\n📊 Progress: [{progress}{remaining}] Step {self.current_step}/{self.total_steps}: {step_name}")
    
    def _step1_welcome(self):
        """Step 1: Welcome and project setup."""
        self._show_progress("项目初始化")
        
        project_name = Path(self.project_path).name
        click.echo(f"📁 当前项目: {project_name}")
        click.echo(f"📂 项目路径: {self.project_path}")
        
        # Check if this project has been analyzed before
        project_config = self.config_manager.get_project_config(self.project_path)
        last_scan = project_config.get('last_scan_date')
        
        if last_scan:
            click.echo(f"📅 上次扫描: {last_scan[:19].replace('T', ' ')}")
            installed_count = len(project_config.get('installed_tools', []))
            if installed_count > 0:
                click.echo(f"🔧 已保存 {installed_count} 个已安装工具配置")
        
        click.echo("\n准备开始扫描分析...")
    
    def _step2_3_scan_and_display(self) -> List[Dict[str, Any]]:
        """Steps 2-3: Scan project and display detected tools."""
        self._show_progress("扫描已安装工具")
        
        click.echo("🔍 正在扫描项目中的AI工具和框架...")
        
        with click.progressbar(length=100, label='扫描进度') as bar:
            # Simulate progress updates
            bar.update(20)
            scan_results = self.scanner.scan_all(self.project_path)
            bar.update(50)
            
            # Update scan history
            self.config_manager.update_scan_history(self.project_path, scan_results)
            bar.update(30)
        
        detected_tools = scan_results.get('detected_ai_tools', [])
        
        self._show_progress("展示检测结果")
        
        click.echo(f"\n🎯 检测到 {len(detected_tools)} 个AI工具/框架:")
        click.echo("-" * 50)
        
        if not detected_tools:
            click.echo("❌ 未检测到任何AI工具")
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
            
            click.echo(f"{i:2d}. {status_emoji} {tool_name}")
            click.echo(f"     状态: {status}")
            click.echo(f"     检测方式: {methods}")
            
            # Show additional info for certain tools
            if tool.get('confidence_score'):
                click.echo(f"     置信度: {tool['confidence_score']:.1f}/1.0")
            
            versions = [v for v in tool.get('versions', []) if v != 'unknown']
            if versions:
                click.echo(f"     版本: {', '.join(versions)}")
            
            click.echo()
        
        return detected_tools
    
    def _step4_6_confirm_and_supplement(self, detected_tools: List[Dict]) -> List[Dict]:
        """Steps 4-6: Interactive confirmation and supplementation loop."""
        self._show_progress("确认检测结果")
        
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
            click.echo("\n🤔 确认检测结果:")
            missing = click.confirm("是否有遗漏的已安装AI工具/框架?", default=False)
            
            if not missing:
                self._show_progress("工具列表确认完成")
                break
            
            # Get additional tools
            additional_tools = self._get_additional_tools()
            confirmed_tools.extend(additional_tools)
            
            # Show updated list
            click.echo(f"\n📋 已确认工具列表 (共{len(confirmed_tools)}个):")
            for i, tool in enumerate(confirmed_tools, 1):
                name = tool.get('name', 'Unknown')
                manual = "✋ 手动添加" if tool.get('manually_added', False) else "🔍 自动检测"
                click.echo(f"  {i}. {name} ({manual})")
        
        return confirmed_tools
    
    def _get_additional_tools(self) -> List[Dict]:
        """Get additional tools from user input."""
        self._show_progress("添加遗漏工具")
        
        additional_tools = []
        
        click.echo("\n📝 请输入遗漏的工具信息:")
        click.echo("提示: 可以一次性输入多个工具，用逗号分隔")
        click.echo("格式: 工具名称[=GitHub地址], 工具名称2[=GitHub地址2], ...")
        click.echo("示例: langchain=https://github.com/langchain-ai/langchain, streamlit")
        
        tools_input = click.prompt("\n请输入工具", type=str).strip()
        
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
                    click.echo(f"🔍 正在搜索 {tool_name} 的GitHub地址...")
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
                    click.echo(f"✅ 已添加: {tool_name} ({github_url})")
                else:
                    click.echo(f"✅ 已添加: {tool_name} (未找到GitHub地址)")
        
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
        self._show_progress("获取目标安装工具")
        
        click.echo("\n🎯 目标工具配置:")
        click.echo("请输入您计划安装的AI工具/框架")
        
        # Check saved target tools
        saved_targets = self.config_manager.get_target_tools(self.project_path)
        if saved_targets:
            click.echo(f"\n💾 上次保存的目标工具 ({len(saved_targets)}个):")
            for i, tool in enumerate(saved_targets, 1):
                click.echo(f"  {i}. {tool.get('display_name', tool.get('name'))}")
            
            use_saved = click.confirm("是否使用已保存的目标工具列表?", default=True)
            if use_saved:
                # Ask if user wants to add more
                add_more = click.confirm("是否要添加更多目标工具?", default=False)
                if not add_more:
                    return saved_targets
        
        target_tools = saved_targets.copy() if saved_targets else []
        
        click.echo("\n📝 请输入计划安装的工具:")
        click.echo("格式: 工具名称[=GitHub地址], 工具名称2[=GitHub地址2], ...")
        click.echo("示例: CrewAI=https://github.com/joaomdmoura/crewAI, autogen")
        click.echo("留空回车跳过此步骤")
        
        tools_input = click.prompt("目标工具", default='', show_default=False).strip()
        
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
                        click.echo(f"🔍 正在搜索 {tool_name} 的GitHub地址...")
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
                        click.echo(f"🎯 目标工具: {tool_name} ({github_url})")
                    else:
                        click.echo(f"🎯 目标工具: {tool_name} (未找到GitHub地址)")
        
        if target_tools:
            click.echo(f"\n📋 共计划安装 {len(target_tools)} 个工具")
        else:
            click.echo("ℹ️  跳过目标工具配置，将仅分析现有工具间的冲突")
        
        return target_tools
    
    def _step8_configure_api_key(self) -> Optional[str]:
        """Step 8: Configure API key for analysis."""
        self._show_progress("配置API密钥")
        
        click.echo("\n🔑 API密钥配置:")
        click.echo("AI冲突分析需要大模型API支持更准确的分析")
        
        # Check if API key is already configured
        openai_set = self.config_manager.get_api_key_status('openai')
        anthropic_set = self.config_manager.get_api_key_status('anthropic')
        
        if openai_set or anthropic_set:
            click.echo("✅ 检测到已配置的API密钥")
            use_existing = click.confirm("使用已有的API密钥?", default=True)
            if use_existing:
                return "configured"
        
        # Check environment variables
        openai_key = os.getenv('OPENAI_API_KEY')
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        
        if openai_key or anthropic_key:
            click.echo("✅ 检测到环境变量中的API密钥")
            return "environment"
        
        click.echo("\n选择API密钥配置方式:")
        click.echo("1. 输入OpenAI API密钥")
        click.echo("2. 输入Anthropic Claude API密钥") 
        click.echo("3. 跳过 (仅使用静态规则分析)")
        
        choice = click.prompt("请选择", type=click.Choice(['1', '2', '3']), default='3')
        
        if choice == '1':
            api_key = click.prompt("OpenAI API密钥", hide_input=True)
            if api_key.strip():
                # Set environment variable for this session
                os.environ['OPENAI_API_KEY'] = api_key.strip()
                self.config_manager.set_api_key_status('openai', True)
                click.echo("✅ OpenAI API密钥已配置")
                return api_key.strip()
        elif choice == '2':
            api_key = click.prompt("Anthropic API密钥", hide_input=True)
            if api_key.strip():
                os.environ['ANTHROPIC_API_KEY'] = api_key.strip()
                self.config_manager.set_api_key_status('anthropic', True)
                click.echo("✅ Anthropic API密钥已配置")
                return api_key.strip()
        
        click.echo("ℹ️  跳过API密钥配置，将使用静态规则进行分析")
        return None
    
    def _step9_10_analyze_and_report(self, confirmed_tools: List[Dict], target_tools: List[Dict], api_key: Optional[str]):
        """Steps 9-10: Analyze conflicts and generate report."""
        self._show_progress("分析潜在冲突")
        
        click.echo("\n🔬 开始冲突分析...")
        
        # Combine all tools for analysis
        all_tools = confirmed_tools + target_tools
        
        if not all_tools:
            click.echo("⚠️  没有工具需要分析")
            return
        
        # Create analyzer
        analyzer = ConflictAnalyzer()
        
        with click.progressbar(length=100, label='分析进度') as bar:
            bar.update(25)
            
            # Analyze conflicts
            conflicts = analyzer.analyze_tools(all_tools)
            bar.update(50)
            
            # Generate report
            reporter = ConflictReporter()
            
            self._show_progress("生成分析报告")
            
            # Interactive report display
            self._display_interactive_report(conflicts, confirmed_tools, target_tools)
            bar.update(25)
        
        # Generate static report file
        self._generate_static_report(conflicts, confirmed_tools, target_tools, analyzer)
    
    def _display_interactive_report(self, conflicts: List[Dict], installed_tools: List[Dict], target_tools: List[Dict]):
        """Display interactive conflict report."""
        click.echo("\n" + "=" * 60)
        click.echo("🎯 AI工具冲突分析报告")
        click.echo("=" * 60)
        
        # Summary
        click.echo(f"📊 分析摘要:")
        click.echo(f"   • 已安装工具: {len(installed_tools)} 个")
        click.echo(f"   • 目标安装工具: {len(target_tools)} 个")
        click.echo(f"   • 发现的冲突: {len(conflicts)} 个")
        
        if not conflicts:
            click.echo("\n🎉 恭喜! 没有发现潜在冲突")
            click.echo("✅ 您的工具配置看起来很安全")
            return
        
        # Group conflicts by severity
        high_conflicts = [c for c in conflicts if c.get('severity') == 'high']
        medium_conflicts = [c for c in conflicts if c.get('severity') == 'medium'] 
        low_conflicts = [c for c in conflicts if c.get('severity') == 'low']
        
        # Display high severity conflicts first
        if high_conflicts:
            click.echo(f"\n🔴 高危冲突 ({len(high_conflicts)} 个):")
            for i, conflict in enumerate(high_conflicts, 1):
                click.echo(f"\n{i}. {conflict.get('description', 'Unknown conflict')}")
                click.echo(f"   工具: {', '.join(conflict.get('tools_involved', []))}")
                click.echo(f"   影响: {conflict.get('potential_issues', 'Unknown impact')}")
                click.echo(f"   建议: {conflict.get('mitigation', 'No recommendation')}")
                
                if click.confirm("   查看详细信息?", default=False):
                    self._show_conflict_details(conflict)
        
        if medium_conflicts:
            click.echo(f"\n🟡 中等冲突 ({len(medium_conflicts)} 个):")
            for i, conflict in enumerate(medium_conflicts, 1):
                click.echo(f"\n{i}. {conflict.get('description', 'Unknown conflict')}")
                click.echo(f"   工具: {', '.join(conflict.get('tools_involved', []))}")
                click.echo(f"   建议: {conflict.get('mitigation', 'No recommendation')}")
        
        if low_conflicts:
            if click.confirm(f"\n🟢 显示低危冲突 ({len(low_conflicts)} 个)?", default=False):
                for i, conflict in enumerate(low_conflicts, 1):
                    click.echo(f"\n{i}. {conflict.get('description', 'Unknown conflict')}")
                    click.echo(f"   工具: {', '.join(conflict.get('tools_involved', []))}")
        
        # Overall recommendation
        if high_conflicts:
            click.echo("\n⚠️  建议: 请优先解决高危冲突后再进行安装")
        elif medium_conflicts:
            click.echo("\n💡 建议: 注意中等冲突，建议配置时多加小心")
        else:
            click.echo("\n✅ 总体评估: 冲突风险较低，可以安全安装")
    
    def _show_conflict_details(self, conflict: Dict):
        """Show detailed conflict information."""
        click.echo("   📋 详细信息:")
        click.echo(f"      类型: {conflict.get('type', 'Unknown')}")
        click.echo(f"      置信度: {conflict.get('confidence', 'Unknown')}")
        click.echo(f"      来源: {conflict.get('source', 'Unknown')}")
        
        if 'additional_info' in conflict:
            click.echo(f"      额外信息: {conflict['additional_info']}")
    
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
            
            click.echo(f"\n💾 详细报告已保存: {report_file}")
            
            if click.confirm("现在打开报告文件?", default=False):
                try:
                    import webbrowser
                    webbrowser.open(str(report_file))
                except Exception:
                    click.echo(f"请手动打开: {report_file}")
        
        except Exception as e:
            click.echo(f"⚠️  保存报告失败: {e}")
    
    def _generate_report_content(self, conflicts: List[Dict], installed_tools: List[Dict], target_tools: List[Dict]) -> str:
        """Generate detailed report content."""
        lines = []
        lines.append("=" * 80)
        lines.append("AI工具冲突分析报告")
        lines.append("=" * 80)
        lines.append(f"项目路径: {self.project_path}")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"分析工具: AI Pitfall Detector")
        lines.append("")
        
        # Summary section
        lines.append("📊 分析摘要")
        lines.append("-" * 40)
        lines.append(f"已安装工具数量: {len(installed_tools)}")
        lines.append(f"目标安装工具数量: {len(target_tools)}")
        lines.append(f"检测到的冲突数量: {len(conflicts)}")
        lines.append("")
        
        # Installed tools
        if installed_tools:
            lines.append("🔧 已安装工具列表")
            lines.append("-" * 40)
            for i, tool in enumerate(installed_tools, 1):
                name = tool.get('name', 'Unknown')
                status = tool.get('status', 'unknown')
                methods = ', '.join(tool.get('detection_methods', []))
                lines.append(f"{i:2d}. {name}")
                lines.append(f"    状态: {status}")
                lines.append(f"    检测方式: {methods}")
                if tool.get('github_url'):
                    lines.append(f"    GitHub: {tool['github_url']}")
                lines.append("")
        
        # Target tools
        if target_tools:
            lines.append("🎯 目标安装工具列表")
            lines.append("-" * 40)
            for i, tool in enumerate(target_tools, 1):
                name = tool.get('display_name', tool.get('name', 'Unknown'))
                lines.append(f"{i:2d}. {name}")
                if tool.get('github_url'):
                    lines.append(f"    GitHub: {tool['github_url']}")
                lines.append("")
        
        # Conflicts
        if conflicts:
            lines.append("⚠️  冲突分析结果")
            lines.append("-" * 40)
            
            # Group by severity
            for severity, emoji in [('high', '🔴'), ('medium', '🟡'), ('low', '🟢')]:
                severity_conflicts = [c for c in conflicts if c.get('severity') == severity]
                if severity_conflicts:
                    lines.append(f"\n{emoji} {severity.upper()}严重度冲突 ({len(severity_conflicts)} 个):")
                    lines.append("")
                    
                    for i, conflict in enumerate(severity_conflicts, 1):
                        lines.append(f"{i}. {conflict.get('description', 'Unknown conflict')}")
                        lines.append(f"   类型: {conflict.get('type', 'Unknown')}")
                        lines.append(f"   涉及工具: {', '.join(conflict.get('tools_involved', []))}")
                        lines.append(f"   潜在影响: {conflict.get('potential_issues', 'Unknown impact')}")
                        lines.append(f"   解决建议: {conflict.get('mitigation', 'No recommendation')}")
                        lines.append(f"   置信度: {conflict.get('confidence', 'Unknown')}")
                        lines.append(f"   检测来源: {conflict.get('source', 'Unknown')}")
                        lines.append("")
        else:
            lines.append("🎉 冲突分析结果")
            lines.append("-" * 40)
            lines.append("恭喜! 没有检测到潜在冲突。")
            lines.append("您的工具配置看起来很安全，可以放心安装和使用。")
            lines.append("")
        
        # Footer
        lines.append("-" * 80)
        lines.append("报告说明:")
        lines.append("• 此报告基于静态规则和动态分析生成")
        lines.append("• 建议在实际安装前仔细阅读冲突描述和解决建议")
        lines.append("• 如有疑问，请参考各工具的官方文档")
        lines.append("-" * 80)
        
        return "\n".join(lines)