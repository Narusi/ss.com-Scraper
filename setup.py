"""
Setup script for ss_re_scraper package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ss_re_scraper",
    version="0.2.0",
    author="Nauris",
    description="A Python package for scraping real estate data from www.ss.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Narusi/ss.com-Scraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.25.0',
        'beautifulsoup4>=4.9.0',
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'nbformat>=4.2.0',
    ],
    extras_require={
        'analysis': [
            'matplotlib>=3.0.0',
            'plotly>=4.0.0',
            'seaborn>=0.9.0',
        ],
        'pdf': [
            'reportlab>=3.5.0',
            'matplotlib>=3.0.0',
        ],
    },
)
