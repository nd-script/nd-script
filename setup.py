#!/usr/bin/env python3
"""
ND-Script Package Setup
إعداد حزمة ND-Script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
try:
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = [
        'lark>=1.1.0',
        'psutil>=5.8.0',
    ]

setup(
    name="ndscript",
    version="2.0.0",
    author="ND-Script Development Team",
    author_email="ndscript@example.com",
    description="Bilingual Domain-Specific Language for Quantum Fractal Universe Simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ndscript/ndscript",
    project_urls={
        "Bug Tracker": "https://github.com/ndscript/ndscript/issues",
        "Documentation": "https://ndscript.readthedocs.io/",
        "Source Code": "https://github.com/ndscript/ndscript",
        "Playground": "https://ndscript.github.io/playground/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Languages",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Natural Language :: Arabic",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "jupyter": [
            "ipython>=7.0",
            "jupyter>=1.0",
            "notebook>=6.0",
        ],
        "web": [
            "flask>=2.0",
            "flask-cors>=3.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "ndscript=nds.cli:main",
            "nds=nds.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "nds": [
            "grammar/*.lark",
            "web/*.html",
            "web/*.css",
            "web/*.js",
            "examples/*.nds",
            "docs/*.md",
            "docs/*.html",
        ],
    },
    keywords=[
        "ndscript",
        "dsl",
        "bilingual",
        "arabic",
        "english",
        "quantum",
        "fractal",
        "universe",
        "simulation",
        "programming-language",
        "interpreter",
        "compiler",
        "parallel-processing",
        "type-system",
    ],
    zip_safe=False,
)
