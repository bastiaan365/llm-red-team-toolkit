#!/usr/bin/env python
"""Setup configuration for LLM Red Team Toolkit."""

from setuptools import setup, find_packages

setup(
    name="llm-red-team-toolkit",
    version="0.1.0",
    description="Automated security testing toolkit for LLM-based applications",
    author="Bastiaan",
    author_email="bastiaanrusch01@gmail.com",
    url="https://github.com/yourusername/llm-red-team-toolkit",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "aiohttp>=3.8.0",
        "pydantic>=2.0",
        "jinja2>=3.1.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "isort>=5.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "pre-commit>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "redteam=redteam.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
    ],
    keywords="security testing llm vulnerability assessment red team",
)
