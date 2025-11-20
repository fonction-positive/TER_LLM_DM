"""
Unit Tests for Data Generator Module
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generator.core import DataGenerator
from generator.distributions import DistributionEngine
from generator.injector import PatternInjector


class TestDistributionEngine:
    """Tests for distribution generation."""
    
    def test_random_distribution(self):
        """Test uniform random distribution."""
        probs = DistributionEngine.generate_item_frequencies(100, "random")
        
        assert len(probs) == 100
        assert np.isclose(probs.sum(), 1.0)
        assert all(probs > 0)
    
    def test_zipf_distribution(self):
        """Test Zipf distribution."""
        probs = DistributionEngine.generate_item_frequencies(
            100, "zipf", {"alpha": 1.2}
        )
        
        assert len(probs) == 100
        assert np.isclose(probs.sum(), 1.0)
        # First item should be most frequent
        assert probs[0] == max(probs)
    
    def test_invalid_distribution(self):
        """Test that invalid distribution raises error."""
        with pytest.raises(ValueError):
            DistributionEngine.generate_item_frequencies(100, "invalid")


class TestPatternInjector:
    """Tests for pattern injection."""
    
    def test_inject_simple_pattern(self):
        """Test injecting a simple pattern."""
        num_trans = 1000
        num_items = 50
        
        data = np.zeros((num_trans, num_items), dtype=int)
        injector = PatternInjector(num_trans, num_items)
        
        pattern = [5, 10, 15]
        target_support = 0.1
        
        data = injector.inject_pattern(data, pattern, target_support)
        
        # Verify pattern was injected
        actual_support = PatternInjector.verify_pattern(data, pattern)
        assert 0.08 <= actual_support <= 0.12  # Allow 2% variance
    
    def test_inject_with_noise(self):
        """Test injection with noise."""
        num_trans = 1000
        num_items = 50
        
        data = np.zeros((num_trans, num_items), dtype=int)
        injector = PatternInjector(num_trans, num_items)
        
        pattern = [1, 2, 3]
        target_support = 0.15
        noise_ratio = 0.2
        
        data = injector.inject_pattern(data, pattern, target_support, noise_ratio)
        
        # With noise, actual support should be lower
        actual_support = PatternInjector.verify_pattern(data, pattern)
        assert actual_support < target_support


class TestDataGenerator:
    """Tests for main data generator."""
    
    def test_basic_generation(self):
        """Test basic data generation."""
        config = {
            "dataset_meta": {
                "num_transactions": 100,
                "num_items": 50,
                "density": 0.1,
                "avg_transaction_len": 5
            },
            "distribution_config": {
                "method": "random",
                "params": {}
            },
            "pattern_injection": []
        }
        
        generator = DataGenerator(config)
        data = generator.generate(seed=42)
        
        assert data.shape == (100, 50)
        assert data.dtype == np.int8
    
    def test_generation_with_patterns(self):
        """Test generation with pattern injection."""
        config = {
            "dataset_meta": {
                "num_transactions": 500,
                "num_items": 100,
                "density": 0.08,
                "avg_transaction_len": 8
            },
            "distribution_config": {
                "method": "zipf",
                "params": {"alpha": 1.1}
            },
            "pattern_injection": [
                {
                    "id": "test_pattern",
                    "items": [10, 20, 30],
                    "target_support": 0.1,
                    "noise_ratio": 0.05
                }
            ]
        }
        
        generator = DataGenerator(config)
        data = generator.generate(seed=42)
        
        stats = generator.get_statistics()
        
        assert stats['num_transactions'] == 500
        assert stats['num_items'] == 100
        assert stats['num_patterns_injected'] == 1
        assert len(stats['injected_patterns']) == 1
    
    def test_spmf_output(self, tmp_path):
        """Test SPMF format output."""
        config = {
            "dataset_meta": {
                "num_transactions": 10,
                "num_items": 20,
                "density": 0.2,
                "avg_transaction_len": 4
            },
            "distribution_config": {
                "method": "random",
                "params": {}
            },
            "pattern_injection": []
        }
        
        generator = DataGenerator(config)
        generator.generate(seed=42)
        
        output_file = tmp_path / "test.spmf"
        generator.to_spmf(str(output_file))
        
        assert output_file.exists()
        
        # Read and verify format
        with open(output_file, "r") as f:
            lines = f.readlines()
        
        assert len(lines) == 10  # Should have 10 transactions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
