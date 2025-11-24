from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="immoscout",
    version="0.1.1",
    description="A Python API wrapper for ImmobilienScout24",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="wiestju",
    url="https://github.com/wiestju/immoscout",
    project_urls={
        "Bug Tracker": "https://github.com/wiestju/immoscout/issues",
        "Source Code": "https://github.com/wiestju/immoscout",
        "Documentation": "https://github.com/wiestju/immoscout#readme",
    },
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
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
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
)
