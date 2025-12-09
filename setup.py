"""
Setup script for ss_re_scraper package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ss_re_scraper",
    version="0.1.0",
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
    ],
)
