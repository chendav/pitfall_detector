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
    version="0.1.0",
    author="AI Pitfall Detector Team",
    author_email="",
    description="A CLI tool to detect conflicts between AI tools before installation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chendav/pitfall_detector",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Tools",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "ai-pitfall=pitfall_detector.cli:cli",
        ],
    },
    keywords="ai, tools, conflicts, analysis, cli, machine-learning, llm",
    project_urls={
        "Bug Reports": "https://github.com/chendav/pitfall_detector/issues",
        "Source": "https://github.com/chendav/pitfall_detector",
    },
)