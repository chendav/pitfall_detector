# 🕳️ AI Pitfall Detector

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Don't step into the same pit twice - Detect conflicts between AI tools before installation**

*An intelligent CLI tool that analyzes potential conflicts between AI tools by examining their documentation and identifying common integration issues. Save hours of debugging by knowing what conflicts to expect before you install.*

[🚀 Quick Start](#-quick-start) • [✨ Features](#-features) • [📖 Documentation](#-usage) • [🎯 Examples](#-example-workflows)

</div>

---

## 🌟 **What Makes This Special**

AI Pitfall Detector revolutionizes how developers manage AI tool conflicts with:

- **🤖 Intelligent Auto-Discovery**: Automatically detects installed AI tools from your project environment
- **🧭 Guided Interactive Workflow**: Step-by-step process that requires zero configuration knowledge
- **🎯 Smart Conflict Prevention**: Distinguishes between installed vs. planned tools for targeted recommendations
- **📊 Actionable Reports**: Provides specific commands and installation order suggestions, not just warnings
- **⚡ Multiple Analysis Modes**: AI-powered deep analysis + static rules for comprehensive coverage

## 🚀 Quick Start

### 🌟 **Intelligent Interactive Mode (Recommended)**

Perfect for project setup or when adding new AI tools to existing projects:

```bash
# Install the tool
pip install ai-pitfall-detector

# Navigate to your AI project
cd /path/to/your-ai-project

# Launch the intelligent workflow
ai-pitfall interactive
# or use the intuitive alias
ai-pitfall smart-scan
```

**What happens next:**
1. 🔍 **Auto-scans** your project for installed AI tools (pip, conda, requirements files, running processes)
2. 🤝 **Shows findings** and lets you confirm or add missed tools
3. 🎯 **Collects** tools you plan to install
4. 🔑 **Optionally configures** API keys for enhanced AI analysis
5. 📊 **Generates** detailed conflict reports with specific solutions

### 📋 **Traditional Command-Line Mode**

For users who prefer explicit control:

```bash
# Configure API key (optional, for AI-enhanced analysis)
ai-pitfall config --provider openai --api-key your-key

# Add tools to analyze
ai-pitfall add https://github.com/joaomdmoura/crewAI
ai-pitfall add https://github.com/langchain-ai/langchain
ai-pitfall add https://github.com/streamlit/streamlit

# Generate conflict analysis
ai-pitfall analyze
```

---

## ✨ Features

<table>
<tr>
<td>

### 🌟 **Smart Interactive Analysis**
- **🤖 Auto-Discovery**: Detects tools from pip, conda, requirements files, processes, Docker
- **🧭 Guided Workflow**: Interactive step-by-step process with progress tracking
- **🎯 Smart Recommendations**: Tailored advice for installed vs. planned tools
- **💾 Session Memory**: Saves configuration and tool lists for future analysis
- **🌐 Multi-Language**: Supports Chinese and English interfaces

</td>
<td>

### 🔍 **Advanced Conflict Detection**
- **🧠 AI-Powered Analysis**: Uses LLMs to understand documentation and detect conflicts
- **⚡ Multi-Mode Detection**: Static rules + dynamic AI analysis
- **📊 Rich Conflict Types**: Ports, dependencies, functionality overlaps, resources
- **🎭 Confidence Scoring**: Reliability indicators for each detected conflict
- **📈 Severity Levels**: Prioritized conflict reporting (High/Medium/Low)

</td>
</tr>
<tr>
<td>

### 🛠️ **Developer Experience**
- **🔧 Zero Configuration**: Works out of the box, configure only what you need
- **📋 Flexible Workflows**: Interactive OR traditional command-line usage
- **⚡ Fast Analysis**: Get results in seconds, not hours
- **🌐 GitHub Integration**: Auto-fetches and analyzes tool documentation
- **💻 Cross-Platform**: Windows, macOS, and Linux support

</td>
<td>

### 🎯 **Professional Output**
- **📊 Actionable Reports**: Specific commands and solutions, not just warnings
- **🗂️ Multiple Formats**: Human-readable and JSON for automation
- **📁 Export Options**: Save reports for team sharing and CI/CD integration
- **🎨 Rich CLI**: Color-coded output with emojis and progress bars
- **📄 Detailed Logging**: Comprehensive analysis history and debugging info

</td>
</tr>
</table>

---

## 🛠️ Installation

### Requirements
- **Python 3.8+** (3.9+ recommended)
- **Internet connection** for GitHub API access
- **OpenAI or Anthropic API key** (optional, for AI-enhanced analysis)

### Install Methods

#### 📦 **From PyPI (Recommended)**
```bash
pip install ai-pitfall-detector
```

#### 🔧 **From Source (Latest Features)**
```bash
git clone https://github.com/yourusername/ai-pitfall-detector.git
cd ai-pitfall-detector
pip install -e .
```

#### 🐳 **Docker (Coming Soon)**
```bash
docker run -v $(pwd):/workspace ai-pitfall-detector interactive
```

---

## 📖 Usage

### 🌟 **Interactive Workflow (Recommended)**

The intelligent workflow provides a comprehensive, guided analysis experience:

```bash
ai-pitfall interactive [--project-path /path/to/project]
```

**Interactive Process Flow:**

<details>
<summary><b>📋 Click to expand detailed workflow steps</b></summary>

#### **Step 1: 🏠 Project Discovery**
- Analyzes project structure and detects previous configurations
- Shows project name, path, and last scan date if available
- Loads any previously saved tool lists

#### **Step 2: 🔍 Auto-Detection Scan**
Comprehensively scans for AI tools via:
- **Python Packages**: pip list, conda environments
- **Requirements Files**: requirements.txt, pyproject.toml, setup.py  
- **Running Processes**: Active services on known AI tool ports
- **Docker Containers**: AI/ML containers and their exposed ports
- **Project Files**: Configuration files, import statements
- **Dynamic Detection**: AI agent framework signatures and patterns

#### **Step 3: ✅ Confirmation & Supplementation**
- Displays detected tools with confidence scores and detection methods
- Interactive confirmation: "Are there any missing tools?"
- Bulk tool input support: `langchain, streamlit=https://github.com/streamlit/streamlit`
- Auto-resolves GitHub URLs for known tools
- Updates saved configuration

#### **Step 4: 🎯 Target Tools Collection**
- Collects tools you plan to install
- Distinguishes from already installed tools
- Auto-suggests GitHub URLs using intelligent search
- Saves target list for future reference

#### **Step 5: 🔑 API Configuration**
- Detects existing API keys (config file or environment variables)
- Choice of providers: OpenAI, Anthropic, or skip for static-only analysis
- Secure key input with validation
- Session-based key storage (not permanently saved unless requested)

#### **Step 6: 📊 Analysis & Reporting**
- Comprehensive conflict analysis of all tools (installed + planned)
- Real-time progress tracking with detailed status updates
- Intelligent report generation with:
  - **Installation Order Recommendations**
  - **Specific Mitigation Commands**  
  - **Conflict Severity Prioritization**
  - **Tool-Specific Configuration Advice**
- Auto-saves detailed JSON report for future reference

</details>

### 📋 **Traditional Command-Line Workflow**

For users who prefer explicit control or automation:

#### **Configuration**
```bash
# Set up API provider (optional)
ai-pitfall config --provider openai --api-key sk-...
ai-pitfall config --provider anthropic --api-key claude-...

# View current configuration
ai-pitfall config --show
```

#### **Tool Management**
```bash
# Add tools for analysis
ai-pitfall add https://github.com/joaomdmoura/crewAI
ai-pitfall add https://github.com/langchain-ai/langchain --force

# Batch add with file
echo "https://github.com/streamlit/streamlit" >> tools.txt
echo "https://github.com/gradio-app/gradio" >> tools.txt
ai-pitfall add --batch --file tools.txt

# List added tools
ai-pitfall list [--format json]

# Remove specific tools
ai-pitfall remove streamlit

# Clear all tools
ai-pitfall clear
```

#### **Analysis Commands**
```bash
# Analyze all added tools
ai-pitfall analyze [--format json] [--export report.json] [--no-colors]

# Quick one-time analysis (doesn't save tools)
ai-pitfall quick-analyze \
  https://github.com/joaomdmoura/crewAI \
  https://github.com/langchain-ai/langchain \
  https://github.com/streamlit/streamlit

# Environment scan only
ai-pitfall scan [--project-path /path] [--auto-add] [--format json]
```

### 🎛️ **Complete Command Reference**

| Command | Description | Use Case |
|---------|-------------|----------|
| `interactive` | 🌟 Smart guided workflow | **Recommended**: Project setup, comprehensive analysis |
| `smart-scan` | Alias for interactive | Same functionality, more intuitive name |
| `scan` | Auto-detect installed tools | Quick environment overview, CI/CD integration |
| `add <url>` | Add tool from GitHub URL | Traditional workflow, specific tool addition |
| `analyze` | Analyze all added tools | Generate conflict reports for saved tools |
| `quick-analyze <urls>` | One-shot analysis | Test tool combinations without persistence |
| `list` | Show added tools | View current tool registry |
| `config` | Configure API settings | Set up authentication, view settings |
| `init` | First-time setup wizard | Initial tool configuration |
| `clear` | Remove all tools | Reset tool registry |
| `remove <name>` | Remove specific tool | Clean up tool list |

---

## 🎯 Example Workflows

### 🌟 **Scenario 1: New AI Project Setup**

You're starting a new project and want to choose compatible AI tools:

```bash
# Create and enter project directory
mkdir my-ai-agent && cd my-ai-agent

# Launch intelligent analysis
ai-pitfall interactive

# Follow the guided process:
# 1. No tools detected (new project)
# 2. Add planned tools: "crewai, langchain, streamlit"
# 3. Configure OpenAI API key
# 4. Get detailed compatibility report with installation recommendations
```

**Expected Output:**
```
🎯 AI Tool Conflict Analysis Report
====================================================
📊 Analysis Summary:
   • Installed tools: 0
   • Target installation tools: 3
   • Conflicts detected: 1

💡 Recommended Installation Order:
1. Install langchain first (base framework)
2. Install streamlit, configure port to avoid conflicts
3. Finally install crewai, pay attention to environment variable configuration

⚠️ Important Notes:
- Potential port conflict between streamlit and system (8501)
- All tools will share the OPENAI_API_KEY environment variable
```

### 📊 **Scenario 2: Existing Project Analysis**

You have an existing AI project and want to add new tools safely:

```bash
# In your existing project directory
cd /existing/ai-project

ai-pitfall interactive

# The tool will:
# 1. Auto-detect: langchain, jupyter, pytorch (from your environment)
# 2. You add planned: "autogen=https://github.com/microsoft/autogen"
# 3. Analysis shows agent framework overlap between langchain and autogen
# 4. Recommends choosing one as primary, using other for specific features
```

### 🔄 **Scenario 3: CI/CD Integration**

Automated conflict checking in your deployment pipeline:

```bash
# In CI/CD script
ai-pitfall scan --format json --export scan-results.json
ai-pitfall quick-analyze \
  https://github.com/streamlit/streamlit \
  https://github.com/gradio-app/gradio \
  --format json --no-colors > conflict-report.json

# Parse results and fail build if high-severity conflicts found
python check-conflicts.py conflict-report.json
```

### 🧪 **Scenario 4: Research & Exploration**

Testing different tool combinations before committing:

```bash
# Test agent frameworks
ai-pitfall quick-analyze \
  https://github.com/joaomdmoura/crewAI \
  https://github.com/microsoft/autogen \
  https://github.com/deepset-ai/haystack

# Test web interfaces
ai-pitfall quick-analyze \
  https://github.com/streamlit/streamlit \
  https://github.com/gradio-app/gradio \
  https://github.com/zauberzeug/nicegui
```

---

## 📊 Example Output

### 🌟 **Interactive Workflow Report**

<details>
<summary><b>📋 Click to see full interactive workflow output</b></summary>

```
🚀 AI Pitfall Detector - Interactive Workflow
============================================================
📁 Current Project: ai-agent-project  
📂 Project Path: /Users/dev/ai-agent-project
📅 Last Scan: 2024-01-15 14:30:22

🔍 Scanning AI tools and frameworks in project...
Scanning Progress ████████████████████████████████████████ 100%

🎯 Detected 5 AI Tools/Frameworks:
--------------------------------------------------
 1. ✅ langchain
     Status: installed
     Detection Method: pip_installed, requirements_txt
     Version: 0.1.17
     Confidence: 1.0/1.0

 2. 🟢 streamlit
     Status: running  
     Detection Method: running_process, pip_installed
     Version: 1.28.2
     Port: 8501

 3. 🤖 crewai
     Status: agent_framework_detected
     Detection Method: dynamic_agent_detection
     Confidence: 9.2/10.0
     Type: AI Agent Framework

 4. ✅ jupyter
     Status: installed
     Detection Method: conda_env, running_process  
     Version: 1.0.0
     Port: 8888

 5. ✅ openai
     Status: installed
     Detection Method: pip_installed, import_detection
     Version: 1.3.7

🤔 Confirm Detection Results:
Are there any missing installed AI tools/frameworks? [y/N]: n

📋 Confirmed Tool List (5 total):
  1. langchain (🔍 Auto-detected)
  2. streamlit (🔍 Auto-detected)
  3. crewai (🔍 Auto-detected)  
  4. jupyter (🔍 Auto-detected)
  5. openai (🔍 Auto-detected)

🎯 Target Tool Configuration:
Please enter the AI tools/frameworks you plan to install

💾 Previously saved target tools (0 tools):

Please enter tools to install: autogen=https://github.com/microsoft/autogen, gradio

🔍 Searching for gradio's GitHub address...
🎯 Target Tool: autogen (https://github.com/microsoft/autogen)  
🎯 Target Tool: gradio (https://github.com/gradio-app/gradio)

📋 Total planned installations: 2 tools

🔑 API Key Configuration:
AI conflict analysis requires large model API support for more accurate analysis
✅ API key detected in environment variables

🔄 Starting conflict analysis...
Analysis Progress ████████████████████████████████████████ 100%

============================================================
🎯 AI Tool Conflict Analysis Report  
============================================================
📊 Analysis Summary:
   • Installed tools: 5
   • Target installation tools: 2
   • Conflicts detected: 4

⚠️ Important Conflict Alerts:

1. 🔴 HIGH - Port Conflict
   Affected Tools: streamlit ↔ gradio (planned installation)
   Issue: Both tools default to using ports in the 7860/8501 range
   Impact: Cannot run simultaneously, or will encounter port occupation errors
   ✅ Solution: Configure different ports
   Commands: 
   - streamlit run app.py --server.port 8502
   - gradio app.py --server-port 7861
   Confidence: high

2. 🟡 MEDIUM - Functionality Overlap  
   Affected Tools: crewai ↔ autogen (planned installation)
   Issue: Both are multi-agent collaboration frameworks with high core functionality overlap
   Impact: May lead to architectural confusion and increased learning costs
   ✅ Solution: Choose one as the primary framework
   Recommendation: CrewAI is better for task orchestration, AutoGen is better for conversational agents
   Confidence: high

3. 🟡 MEDIUM - Environment Variable Conflict
   Affected Tools: langchain ↔ crewai ↔ autogen ↔ openai
   Issue: All may use the OPENAI_API_KEY environment variable
   Impact: Need to ensure API key configuration consistency
   ✅ Solution: Unified environment variable management
   Recommendation: Use .env file to manage API keys uniformly
   Confidence: medium

4. 🟡 MEDIUM - Dependency Conflict Risk
   Affected Tools: jupyter ↔ streamlit ↔ gradio
   Issue: Potential numpy/pandas version dependency conflicts
   Impact: Installation process may encounter version compatibility issues
   ✅ Solution: Use virtual environment, specify dependency versions
   Recommendation: pip install --upgrade numpy pandas before installation
   Confidence: medium

💡 Recommended Installation Order:
1. First configure environment variables (.env file)
2. Install base tools: openai, langchain (already installed)  
3. Choose one primary framework between crewai and autogen
4. Install gradio, configure port to avoid conflicts with streamlit
5. Finally perform integration testing to verify all tools work properly

🔧 Specific Configuration Recommendations:
```bash
# .env file configuration
OPENAI_API_KEY=your_key_here
STREAMLIT_SERVER_PORT=8502
GRADIO_SERVER_PORT=7861

# Virtual environment setup
python -m venv ai-project-env
source ai-project-env/bin/activate  # Linux/Mac
# ai-project-env\Scripts\activate  # Windows

# Install in sequence
pip install --upgrade numpy pandas
pip install autogen  # or crewai, not recommended to install both
pip install gradio
```

📄 Detailed report saved to: ./ai-tools-conflict-report-2024-01-15-143045.json
📊 Tool configuration updated to: ~/.ai-pitfall-detector/project-configs.yaml

✅ Interactive workflow completed successfully!

🎉 Next Step Recommendations:
1. Review detailed JSON report for technical details
2. Configure tools according to installation order recommendations
3. If issues arise, re-run ai-pitfall interactive for latest analysis
```

</details>

### 📋 **Traditional Analysis Report**

<details>
<summary><b>📋 Click to see traditional command-line output</b></summary>

```bash
$ ai-pitfall analyze

🔍 AI Tool Conflict Analysis Report
==================================================
🔧 Tools Analyzed: 4
⚡ Conflicts Found: 3

Tools Analyzed:
  1. CrewAI (v0.1.55)
  2. LangChain (v0.1.17)  
  3. Streamlit (v1.28.2)
  4. AutoGen (planned)

⚡ Conflicts Detected:

1. 🔴 HIGH - Port Conflict
   Tools: Streamlit ↔ Jupyter (running)
   Issue: Both services competing for port 8501
   Impact: Cannot run simultaneously without manual configuration
   ✅ Solution: streamlit run --server.port 8502
   Confidence: high
   Source: static_rule + environment_scan

2. 🟡 MEDIUM - Functionality Overlap
   Tools: CrewAI ↔ AutoGen  
   Issue: Both are multi-agent orchestration frameworks
   Impact: Architectural complexity, potential resource conflicts
   ✅ Solution: Choose CrewAI for task-oriented workflows, AutoGen for conversational agents
   Confidence: high
   Source: ai_analysis + github_documentation

3. 🟡 MEDIUM - Environment Variable Conflict
   Tools: CrewAI ↔ LangChain ↔ AutoGen
   Issue: All tools may use OPENAI_API_KEY with different expectations
   Impact: Authentication inconsistencies, rate limiting issues
   ✅ Solution: Use dedicated API key management with proper scoping
   Confidence: medium
   Source: static_rule + documentation_analysis

📊 Summary Statistics:
   • Port Conflicts: 1 high-severity
   • Functionality Overlaps: 1 medium-severity  
   • Environment Issues: 1 medium-severity
   • Total Risk Score: 6.5/10

💡 Installation Recommendations:
   1. Configure Streamlit port before first run
   2. Choose primary agent framework (CrewAI OR AutoGen)
   3. Set up unified environment variable management
   4. Test integration in isolated environment

📄 Detailed report exported to: conflict-analysis-2024-01-15.json
```

</details>

---

## 🔍 Conflict Types Detected

<table>
<tr>
<th>Conflict Type</th>
<th>Description</th>
<th>Examples</th>
<th>Severity Range</th>
</tr>
<tr>
<td><strong>🚨 Port Conflicts</strong></td>
<td>Tools using same default ports</td>
<td>Streamlit + Gradio (8501), Jupyter + JupyterLab (8888)</td>
<td>High</td>
</tr>
<tr>
<td><strong>📦 Dependency Conflicts</strong></td>
<td>Version incompatibilities in packages</td>
<td>TensorFlow vs PyTorch CUDA, Different pandas versions</td>
<td>High to Medium</td>
</tr>
<tr>
<td><strong>🔄 Functionality Overlap</strong></td>
<td>Similar capabilities causing confusion</td>
<td>Multiple agent frameworks, Duplicate web interfaces</td>
<td>Medium to Low</td>
</tr>
<tr>
<td><strong>💾 Resource Competition</strong></td>
<td>Memory, GPU, or cache conflicts</td>
<td>Multiple model loading, Shared GPU memory</td>
<td>Medium to High</td>
</tr>
<tr>
<td><strong>🔑 Environment Conflicts</strong></td>
<td>Same environment variables used differently</td>
<td>API_KEY variables, Configuration paths</td>
<td>Medium</td>
</tr>
<tr>
<td><strong>⚙️ Configuration Conflicts</strong></td>
<td>Config files or directories that clash</td>
<td>Same config directory names, Conflicting settings</td>
<td>Low to Medium</td>
</tr>
</table>

---

## ⚙️ Configuration

### 📁 **Configuration Files**

AI Pitfall Detector stores configuration in `~/.ai-pitfall-detector/`:

```yaml
# config.yaml - Global settings
api:
  provider: openai          # openai, anthropic
  api_key_configured: true  # boolean flag (actual keys not stored)
  model: gpt-3.5-turbo     # model selection
  max_tokens: 2000         # response limit
  timeout: 30              # API timeout

github:
  token: null              # GitHub token for higher rate limits
  timeout: 30              # GitHub API timeout

output:
  format: human            # human, json
  colors: true             # colorized output
  verbose: false           # detailed logging

analysis:
  confidence_threshold: 0.7 # minimum confidence for reporting
  enable_static_rules: true
  enable_ai_analysis: true
  cache_duration: 3600     # seconds to cache analysis results
```

```yaml
# project-configs.yaml - Per-project tool lists
projects:
  "/path/to/project1":
    last_scan_date: "2024-01-15T14:30:22"
    installed_tools:
      langchain:
        display_name: "LangChain"
        github_url: "https://github.com/langchain-ai/langchain"
        detection_method: "pip_installed,requirements_txt"
        added_manually: false
        metadata:
          status: "installed"
          versions: ["0.1.17"]
          confidence_score: 1.0
    target_tools:
      autogen:
        display_name: "AutoGen"
        github_url: "https://github.com/microsoft/autogen"
        added_date: "2024-01-15T14:35:10"
```

### 🔑 **API Key Management**

Multiple secure options for API key configuration:

```bash
# Method 1: Environment variables (recommended for CI/CD)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="claude-..."

# Method 2: Interactive configuration
ai-pitfall config --provider openai --api-key sk-...

# Method 3: Direct environment detection
# Tool automatically detects keys from environment
```

### 🎛️ **Advanced Configuration**

```bash
# Custom model selection
ai-pitfall config --model gpt-4 --max-tokens 4000

# GitHub token for higher rate limits  
ai-pitfall config --github-token ghp_...

# Adjust confidence thresholds
ai-pitfall config --confidence-threshold 0.8

# Enable verbose logging
ai-pitfall config --verbose true
```

---

## 🧪 Testing Tool Combinations

### 🤖 **Popular AI Agent Frameworks**
```bash
ai-pitfall quick-analyze \
  https://github.com/joaomdmoura/crewAI \
  https://github.com/microsoft/autogen \
  https://github.com/deepset-ai/haystack \
  https://github.com/langchain-ai/langgraph
```

### 🌐 **Web Interface Tools**  
```bash
ai-pitfall quick-analyze \
  https://github.com/streamlit/streamlit \
  https://github.com/gradio-app/gradio \
  https://github.com/zauberzeug/nicegui \
  https://github.com/reflex-dev/reflex
```

### 🧠 **LLM and RAG Tools**
```bash
ai-pitfall quick-analyze \
  https://github.com/langchain-ai/langchain \
  https://github.com/run-llama/llama_index \
  https://github.com/chroma-core/chroma \
  https://github.com/pinecone-io/pinecone-python-client
```

### ⚡ **ML/AI Infrastructure**
```bash
ai-pitfall quick-analyze \
  https://github.com/mlflow/mlflow \
  https://github.com/wandb/wandb \
  https://github.com/huggingface/transformers \
  https://github.com/pytorch/pytorch
```

---

## 🚀 Advanced Usage

### 📊 **JSON API for Automation**

All commands support JSON output for programmatic usage:

```bash
# Get scan results as JSON
ai-pitfall scan --format json > environment.json

# Automated analysis with structured output
ai-pitfall analyze --format json --export analysis.json

# Parse results programmatically
python -c "
import json
with open('analysis.json') as f:
    data = json.load(f)
    high_conflicts = [c for c in data['conflicts'] if c['severity'] == 'high']
    print(f'High-severity conflicts: {len(high_conflicts)}')
    if high_conflicts:
        exit(1)  # Fail CI/CD pipeline
"
```

### 🔧 **Custom Integration Examples**

<details>
<summary><b>🐍 Python Integration</b></summary>

```python
import subprocess
import json

def check_ai_tool_conflicts(project_path):
    """Check for AI tool conflicts in a project."""
    result = subprocess.run([
        'ai-pitfall', 'scan', 
        '--project-path', project_path,
        '--format', 'json'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Scan failed: {result.stderr}")
    
    scan_data = json.loads(result.stdout)
    detected_tools = scan_data.get('detected_ai_tools', [])
    
    # Analyze only if tools found
    if len(detected_tools) >= 2:
        analysis_result = subprocess.run([
            'ai-pitfall', 'analyze',
            '--format', 'json'
        ], capture_output=True, text=True)
        
        analysis_data = json.loads(analysis_result.stdout)
        return analysis_data.get('conflicts', [])
    
    return []

# Usage
conflicts = check_ai_tool_conflicts('/path/to/project')
high_severity = [c for c in conflicts if c['severity'] == 'high']
if high_severity:
    print("⚠️ High-severity conflicts detected!")
    for conflict in high_severity:
        print(f"- {conflict['description']}")
```

</details>

<details>
<summary><b>🔄 GitHub Actions Workflow</b></summary>

```yaml
# .github/workflows/ai-conflict-check.yml
name: AI Tool Conflict Check

on:
  pull_request:
    paths:
      - 'requirements.txt'
      - 'pyproject.toml'
      - 'setup.py'
      - 'environment.yml'

jobs:
  conflict-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install AI Pitfall Detector
      run: pip install ai-pitfall-detector
      
    - name: Scan for AI tools
      run: |
        ai-pitfall scan --format json > scan-results.json
        echo "SCAN_RESULTS<<EOF" >> $GITHUB_ENV
        cat scan-results.json >> $GITHUB_ENV
        echo "EOF" >> $GITHUB_ENV
    
    - name: Check for conflicts
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        ai-pitfall analyze --format json --export conflict-report.json
        
        # Check if high-severity conflicts exist
        if jq -e '.conflicts[] | select(.severity == "high")' conflict-report.json > /dev/null; then
          echo "⚠️ High-severity AI tool conflicts detected!"
          jq '.conflicts[] | select(.severity == "high") | .description' conflict-report.json
          exit 1
        else
          echo "✅ No high-severity conflicts found"
        fi
    
    - name: Upload conflict report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: ai-conflict-report
        path: conflict-report.json
```

</details>

<details>
<summary><b>🐳 Docker Integration</b></summary>

```dockerfile
# Dockerfile for project with AI conflict checking
FROM python:3.9-slim

# Install AI Pitfall Detector
RUN pip install ai-pitfall-detector

WORKDIR /app
COPY requirements.txt .

# Check for conflicts before installing dependencies
RUN echo "Checking for AI tool conflicts..." && \
    ai-pitfall scan --format json > /tmp/scan.json && \
    if [ -s /tmp/scan.json ]; then \
        ai-pitfall analyze --format json --no-colors || \
        (echo "⚠️ Conflicts detected, review before deployment" && exit 1); \
    fi

RUN pip install -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

</details>

### 📈 **Performance Optimization**

```bash
# Cache GitHub API responses for faster repeated analysis
export AI_PITFALL_CACHE_GITHUB=true

# Use lightweight static-only analysis for CI/CD  
ai-pitfall analyze --no-ai-analysis --fast

# Parallel analysis for large tool sets
ai-pitfall analyze --parallel --max-workers 4

# Skip low-confidence conflicts in production
ai-pitfall config --confidence-threshold 0.8
```

---

## 🤝 Contributing

We welcome contributions from the community! Here's how to get started:

### 🛠️ **Development Setup**

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-pitfall-detector.git
cd ai-pitfall-detector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# Install development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### 🧪 **Running Tests**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pitfall_detector --cov-report=html

# Run specific test categories
pytest tests/test_analyzer.py -v
pytest tests/test_static_rules.py::TestStaticConflictDetector::test_detect_env_conflicts
```

### 📝 **Development Guidelines**

1. **Code Style**: We use `black` and `flake8` for code formatting
2. **Testing**: Maintain >90% test coverage for new features
3. **Documentation**: Update README and docstrings for new functionality
4. **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)
5. **Pull Requests**: Include tests, documentation, and detailed descriptions

### 🎯 **Contribution Areas**

- **🔍 Detection Rules**: Add support for new AI tools and frameworks
- **🌐 Integrations**: GitHub Actions, Docker, IDE plugins
- **🎨 UI/UX**: Improve CLI experience and output formatting
- **📊 Analysis**: Enhance conflict detection algorithms
- **📚 Documentation**: Examples, tutorials, use cases
- **🧪 Testing**: Edge cases, integration tests, performance tests

---

## 📚 Resources

### 📖 **Documentation & Guides**
- [📋 Installation Guide](docs/installation.md)
- [🚀 Quick Start Tutorial](docs/quickstart.md)  
- [⚙️ Configuration Reference](docs/configuration.md)
- [🔍 Conflict Types Explained](docs/conflict-types.md)
- [🧪 Testing Workflows](docs/testing.md)
- [🔧 API Reference](docs/api-reference.md)

### 🎥 **Video Tutorials** (Coming Soon)
- Setting up AI Pitfall Detector
- Interactive workflow walkthrough
- CI/CD integration examples
- Advanced configuration options

### 💬 **Community & Support**
- [🐛 Bug Reports](https://github.com/yourusername/ai-pitfall-detector/issues)
- [💡 Feature Requests](https://github.com/yourusername/ai-pitfall-detector/discussions)
- [💬 Community Discord](https://discord.gg/ai-pitfall-detector)
- [📧 Email Support](mailto:support@ai-pitfall-detector.com)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI & Anthropic** for providing the AI APIs that power intelligent analysis
- **The Python Community** for the amazing ecosystem of tools and libraries
- **Contributors** who help make this tool better every day
- **Early Adopters** who provided valuable feedback and bug reports

---

## 🗺️ Roadmap

### 🎯 **Version 2.0 (Q2 2024)**
- [ ] **🌐 Web Interface**: Browser-based analysis dashboard
- [ ] **🔌 IDE Plugins**: VS Code, PyCharm integration
- [ ] **📦 Package Manager Integration**: Direct pip, conda, npm conflict checking
- [ ] **🤖 Advanced AI Models**: Support for Claude-3, Gemini Pro
- [ ] **📊 Analytics Dashboard**: Historical analysis and trend tracking

### 🔮 **Version 3.0 (Q4 2024)**
- [ ] **🔧 Auto-Resolution**: Automatic conflict mitigation suggestions
- [ ] **🌍 Community Database**: Crowdsourced conflict patterns
- [ ] **📈 Performance Profiling**: Runtime performance impact analysis
- [ ] **🔗 Integration Recommendations**: Suggest compatible tool combinations
- [ ] **🎭 Multi-Language Support**: Node.js, Go, Rust ecosystem analysis

### 💡 **Future Ideas**
- Machine learning-based conflict prediction
- Integration with popular AI development platforms
- Real-time monitoring of tool conflicts in production
- Collaborative team conflict management
- Enterprise features and support

---

<div align="center">

**Made with ❤️ for the AI developer community**

*Tired of stepping into the same pits? Let's build better tools together.*

[⭐ Star us on GitHub](https://github.com/yourusername/ai-pitfall-detector) • [🤝 Contribute](CONTRIBUTING.md) • [📢 Share feedback](https://github.com/yourusername/ai-pitfall-detector/discussions)

</div>