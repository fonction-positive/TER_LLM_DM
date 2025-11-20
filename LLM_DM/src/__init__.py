"""
FIDD-Bench Package

Flexible & Intelligent Data Generator for Data Mining Benchmarking
"""

__version__ = "0.1.0"
__author__ = "TER Project Team"

from .generator.core import DataGenerator
from .llm.client import LLMClient
from .llm.parser import ConfigParser
from .benchmark.spmf_runner import SPMFRunner
from .benchmark.metrics import MetricsCalculator

__all__ = [
    "DataGenerator",
    "LLMClient",
    "ConfigParser",
    "SPMFRunner",
    "MetricsCalculator"
]
