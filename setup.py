"""Setup script for AI Pitfall Detector."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="ai-pitfall-detector",
    version="2.0.0",
    author="AI Development Team",
    author_email="developers@ai-pitfall-detector.com",
    description="🕳️ Don't step into the same pit twice - Intelligent CLI tool for detecting AI tool conflicts before installation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-pitfall-detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Data Scientists", 
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Installation/Setup",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-pitfall=pitfall_detector.cli:cli",
        ],
    },
    keywords="ai, tools, conflicts, analysis, cli, machine-learning, llm, interactive, automation, devops, agent-frameworks, streamlit, gradio, langchain",
    project_urls={
        "Homepage": "https://github.com/yourusername/ai-pitfall-detector",
        "Bug Reports": "https://github.com/yourusername/ai-pitfall-detector/issues",
        "Feature Requests": "https://github.com/yourusername/ai-pitfall-detector/discussions",
        "Source": "https://github.com/yourusername/ai-pitfall-detector",
        "Documentation": "https://github.com/yourusername/ai-pitfall-detector#readme",
        "Changelog": "https://github.com/yourusername/ai-pitfall-detector/blob/main/CHANGELOG.md",
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)