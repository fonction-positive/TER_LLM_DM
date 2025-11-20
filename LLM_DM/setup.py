"""
FIDD-Bench Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fidd-bench",
    version="0.1.0",
    author="TER Project Team",
    author_email="lazaar@lisn.fr",
    description="Flexible & Intelligent Data Generator for Data Mining Benchmarking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/fidd-bench",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fidd-bench=main:cli",
        ],
    },
)
