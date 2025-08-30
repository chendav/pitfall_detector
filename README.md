# 🕳️ AI Pitfall Detector

> Don't step into the same pit twice - Detect conflicts between AI tools before installation

AI Pitfall Detector is a CLI tool that analyzes potential conflicts between AI tools by examining their documentation and identifying common integration issues. Save hours of debugging by knowing what conflicts to expect before you install.

## 🚀 Quick Start

```bash
# Install
pip install ai-pitfall-detector

# Configure with your OpenAI API key
ai-pitfall config --api-key your-openai-key

# Add some tools
ai-pitfall add https://github.com/joaomdmoura/crewAI
ai-pitfall add https://github.com/langchain-ai/langchain

# Analyze conflicts
ai-pitfall analyze
```

## ✨ Features

- **🔍 AI-Powered Analysis**: Uses LLM to understand tool documentation and detect conflicts
- **⚡ Quick Analysis**: Analyze tool combinations in seconds, not hours
- **🎯 Conflict Categories**: Detects port conflicts, dependency issues, resource competition, and more
- **📊 Clear Reports**: Human-readable reports with severity levels and mitigation suggestions
- **🔧 Easy Integration**: Simple CLI with JSON export for automation
- **🌐 GitHub Integration**: Automatically fetches and analyzes README documentation

## 🛠️ Installation

### From PyPI (Recommended)

```bash
pip install ai-pitfall-detector
```

### From Source

```bash
git clone https://github.com/chendav/pitfall_detector.git
cd pitfall_detector
pip install -e .
```

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (or Anthropic API key)
- Internet connection for GitHub API access

## 🎮 Usage

### Configuration

First, set up your AI provider:

```bash
# Configure OpenAI (recommended)
ai-pitfall config --provider openai --api-key your-key

# Or configure Anthropic
ai-pitfall config --provider anthropic --api-key your-key

# Show current config
ai-pitfall config --show
```

### Adding Tools

Add AI tools from GitHub repositories:

```bash
# Add individual tools
ai-pitfall add https://github.com/joaomdmoura/crewAI
ai-pitfall add https://github.com/microsoft/autogen
ai-pitfall add https://github.com/streamlit/streamlit

# List added tools
ai-pitfall list
```

### Analyzing Conflicts

```bash
# Analyze all added tools
ai-pitfall analyze

# Export results to JSON
ai-pitfall analyze --format json --export results.json

# Disable colors for CI/automation
ai-pitfall analyze --no-colors
```

### Quick Analysis

Analyze tools without adding them permanently:

```bash
ai-pitfall quick-analyze \
  https://github.com/joaomdmoura/crewAI \
  https://github.com/langchain-ai/langchain \
  https://github.com/streamlit/streamlit
```

### Tool Management

```bash
# Remove a tool
ai-pitfall remove crewAI

# Clear all tools
ai-pitfall clear

# List tools in JSON format
ai-pitfall list --format json
```

## 📊 Example Output

```
🔍 AI Tool Conflict Analysis Report
==================================================
🔧 Tools Analyzed: 3
⚡ Conflicts Found: 2

Tools Analyzed:
  1. crewAI
  2. langchain
  3. streamlit

⚡ Conflicts Detected:

1. ⚠️ MEDIUM - Functionality Overlap
   Tools: crewAI ↔ langchain
   Issue: Both provide agent orchestration capabilities
   Impact: May compete for same resources and cause confusion
   ✅ Solution: Choose one as primary framework, use the other for specific features
   Confidence: high

2. 🚨 HIGH - Port Conflict  
   Tools: streamlit ↔ existing-service
   Issue: Both default to port 8501
   Impact: Cannot run simultaneously without configuration
   ✅ Solution: Configure streamlit to use different port: streamlit run --server.port 8502
   Confidence: high
```

## 🔍 Conflict Types Detected

| Type | Description | Examples |
|------|-------------|----------|
| **Port Conflicts** | Tools using same default ports | Streamlit + Gradio (both use 8501) |
| **Dependency Conflicts** | Version conflicts in packages | Different pandas versions required |
| **Functionality Overlap** | Similar capabilities that interfere | Multiple agent frameworks |
| **Resource Competition** | Memory, GPU, or cache conflicts | Model loading conflicts |
| **Environment Conflicts** | Same environment variables | API_KEY variables with different purposes |
| **Configuration Conflicts** | Config files or directories that clash | Same config directory names |

## ⚙️ Configuration

Configuration is stored in `~/.ai-pitfall-detector/config.yaml`:

```yaml
api:
  provider: openai
  api_key: your-key-here
  model: gpt-3.5-turbo
  max_tokens: 2000
github:
  token: null  # Optional, for higher rate limits
  timeout: 30
output:
  format: human
  colors: true
  verbose: false
```

## 🧪 Example Tool Combinations

Here are some interesting combinations to try:

### Agent Frameworks
```bash
ai-pitfall quick-analyze \
  https://github.com/joaomdmoura/crewAI \
  https://github.com/microsoft/autogen \
  https://github.com/deepset-ai/haystack
```

### Web Interfaces  
```bash
ai-pitfall quick-analyze \
  https://github.com/streamlit/streamlit \
  https://github.com/gradio-app/gradio \
  https://github.com/zauberzeug/nicegui
```

### LLM Tools
```bash
ai-pitfall quick-analyze \
  https://github.com/langchain-ai/langchain \
  https://github.com/run-llama/llama_index \
  https://github.com/chroma-core/chroma
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Run the tests: `pytest`
6. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports

Found a bug? Please create an issue on [GitHub Issues](https://github.com/chendav/pitfall_detector/issues).

## 🗺️ Roadmap

- [ ] Support for more AI providers (Claude, Gemini)
- [ ] Integration with package managers (conda, npm)
- [ ] Web interface for analysis
- [ ] Conflict resolution automation
- [ ] Community conflict database
- [ ] Plugin system for custom analyzers

## 🙏 Acknowledgments

- Built with ❤️ for the AI engineering community
- Inspired by the countless hours spent debugging tool conflicts
- Powered by OpenAI's GPT models for intelligent analysis

---

**Made with 🤖 by developers who got tired of stepping into the same pits**