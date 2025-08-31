# Contributing to AI Pitfall Detector

Thank you for your interest in contributing to AI Pitfall Detector! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

We welcome contributions in many forms:

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new functionality
- 🔍 **Tool Detection**: Add support for new AI tools and frameworks
- 📝 **Documentation**: Improve guides, examples, and explanations
- 🧪 **Testing**: Add test cases and improve coverage
- 🎨 **UI/UX**: Enhance the command-line interface experience
- 🌐 **Integrations**: Create plugins for IDEs, CI/CD systems, etc.

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+ (3.9+ recommended)
- Git
- pip or conda

### Local Development Environment

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/yourusername/ai-pitfall-detector.git
cd ai-pitfall-detector

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate    # Windows

# 4. Install in development mode with dev dependencies
pip install -e .[dev]

# 5. Install pre-commit hooks (optional but recommended)
pre-commit install

# 6. Verify installation
ai-pitfall --help
```

### Development Dependencies

The `[dev]` extra includes:
- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Type checking
- **pre-commit**: Git hook framework

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=pitfall_detector --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py -v

# Run specific test
pytest tests/test_static_rules.py::TestStaticConflictDetector::test_detect_env_conflicts -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Test files should be named `test_*.py`
- Test functions should be named `test_*`
- Aim for >90% test coverage for new code
- Include both unit and integration tests

Example test structure:
```python
import pytest
from pitfall_detector.your_module import YourClass

class TestYourClass:
    def setup_method(self):
        """Setup for each test method."""
        self.instance = YourClass()
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = self.instance.your_method()
        assert result == expected_value
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            self.instance.your_method(invalid_input)
```

## 📝 Code Style

### Formatting Standards

We use automated tools to maintain consistent code style:

```bash
# Format code with black
black pitfall_detector/ tests/

# Check with flake8
flake8 pitfall_detector/ tests/

# Type checking with mypy
mypy pitfall_detector/
```

### Style Guidelines

1. **Code Formatting**: Use `black` with default settings
2. **Line Length**: 88 characters (black default)
3. **Imports**: Use `isort` for import sorting
4. **Type Hints**: Include type hints for all public functions
5. **Docstrings**: Use Google-style docstrings
6. **Variable Names**: Use descriptive names, prefer `snake_case`

Example function with proper style:
```python
from typing import List, Dict, Optional

def analyze_tool_conflicts(
    tools: List[Dict[str, Any]], 
    confidence_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Analyze conflicts between AI tools.
    
    Args:
        tools: List of tool information dictionaries
        confidence_threshold: Minimum confidence for reporting conflicts
        
    Returns:
        List of detected conflicts with metadata
        
    Raises:
        ValueError: If tools list is empty
    """
    if not tools:
        raise ValueError("Tools list cannot be empty")
    
    conflicts = []
    # Implementation here...
    return conflicts
```

## 🔍 Adding New Tool Detection

One of the most valuable contributions is adding support for new AI tools. Here's how:

### 1. Update Tools Database

Add your tool to `tools_database.yaml`:

```yaml
your_tool_name:
  name: "Your Tool Name"
  package_names: ["your-tool-package", "alternative-package"]
  github_url: "https://github.com/author/your-tool"
  category: "web-interface"  # or agent-framework, rag-tool, etc.
  default_ports: [8080, 8081]
  common_env_vars: ["YOUR_TOOL_API_KEY", "YOUR_TOOL_CONFIG"]
  description: "Brief description of what this tool does"
  detection_patterns:
    imports: ["your_tool", "from your_tool"]
    classes: ["YourMainClass", "YourSecondaryClass"]
    files: ["your_tool_config.yaml"]
    functions: ["your_tool_main"]
```

### 2. Add Static Conflict Rules

If your tool has known conflicts, add them to the static rules system.

### 3. Test Your Addition

```bash
# Test detection
ai-pitfall scan --project-path /path/to/project/with/your-tool

# Test conflict analysis
ai-pitfall quick-analyze \
  https://github.com/author/your-tool \
  https://github.com/streamlit/streamlit
```

### 4. Add Tests

Create tests to verify your tool is detected correctly:

```python
def test_detect_your_tool(self):
    """Test detection of your tool."""
    # Test implementation
    pass
```

## 📚 Documentation Guidelines

### README Updates

When adding significant features:
1. Update the main README.md
2. Add examples of your feature
3. Update the command reference table
4. Include any new configuration options

### Docstring Standards

Use Google-style docstrings:

```python
def your_function(param1: str, param2: int = 10) -> List[str]:
    """Brief description of the function.
    
    Longer description if needed. Explain the purpose and any
    important details about the function's behavior.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default
        
    Returns:
        Description of what the function returns
        
    Raises:
        ValueError: When param1 is empty
        RuntimeError: When operation fails
        
    Example:
        >>> result = your_function("hello", 5)
        >>> print(result)
        ['processed', 'hello', '5']
    """
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create a Feature Branch**: `git checkout -b feature/your-feature-name`
2. **Write Tests**: Ensure new code has appropriate test coverage
3. **Run Tests**: `pytest` should pass completely
4. **Check Code Style**: `black` and `flake8` should pass
5. **Update Documentation**: Include relevant documentation updates
6. **Test Manually**: Verify your changes work as expected

### Pull Request Guidelines

1. **Clear Title**: Use descriptive titles like "Add support for Chainlit web framework"
2. **Detailed Description**: Explain what changes you made and why
3. **Link Issues**: Reference any related issues with "Fixes #123"
4. **Include Examples**: Show how your changes work
5. **Screenshots/Output**: Include terminal output or screenshots if relevant

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)  
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

## 🐛 Bug Reports

### Before Reporting

1. **Search Existing Issues**: Check if the bug was already reported
2. **Verify Bug**: Ensure it's reproducible
3. **Test Latest Version**: Try with the most recent version

### Bug Report Template

```markdown
## Bug Description
Clear description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- AI Pitfall Detector Version: [e.g., 2.0.0]
- Terminal: [e.g., Windows Terminal, iTerm2, gnome-terminal]

## Additional Context
Add any other context about the problem here.

## Logs
```
Paste any relevant log output here
```
```

## 💡 Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature you'd like to see.

## Use Case
Explain the problem this feature would solve or the workflow it would improve.

## Proposed Solution
Describe how you envision this feature working.

## Alternatives Considered
Alternative solutions or features you've considered.

## Additional Context
Any other context, mockups, or examples.
```

## 🏷️ Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality
- **PATCH** version for backwards-compatible bug fixes

### Release Checklist

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create git tag
5. Push to GitHub
6. Create GitHub release
7. Deploy to PyPI (maintainers only)

## 🤝 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone, regardless of:
- Age, body size, disability, ethnicity
- Gender identity and expression
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

Examples of behavior that contributes to creating a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported to the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

## 📞 Getting Help

- **Documentation**: Check the [README](README.md) first
- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-pitfall-detector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-pitfall-detector/discussions)
- **Discord**: [Community Discord](https://discord.gg/ai-pitfall-detector) (coming soon)

## 🙏 Recognition

Contributors are recognized in several ways:
- Listed in release notes
- Mentioned in the README contributors section
- GitHub contributor graphs
- Special recognition for significant contributions

Thank you for contributing to AI Pitfall Detector! 🎉