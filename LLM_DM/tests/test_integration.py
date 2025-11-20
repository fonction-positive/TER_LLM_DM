"""
Integration Tests

Tests the full pipeline from config to data generation to benchmarking.
"""

import pytest
import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from generator.core import DataGenerator
from llm.parser import ConfigParser
from utils.file_io import FileIO


class TestIntegration:
    """Integration tests for the complete system."""
    
    def test_full_generation_pipeline(self, tmp_path):
        """Test complete data generation pipeline."""
        # Step 1: Create config
        config = {
            "dataset_meta": {
                "num_transactions": 200,
                "num_items": 50,
                "density": 0.12,
                "avg_transaction_len": 6
            },
            "distribution_config": {
                "method": "zipf",
                "params": {"alpha": 1.2}
            },
            "pattern_injection": [
                {
                    "id": "integration_test_pattern",
                    "items": [5, 10, 15],
                    "target_support": 0.08,
                    "noise_ratio": 0.05
                }
            ]
        }
        
        # Step 2: Validate config
        parser = ConfigParser()
        validated_config = parser.parse(config)
        
        # Step 3: Generate data
        generator = DataGenerator(validated_config)
        data = generator.generate(seed=42)
        
        # Verify data shape
        assert data.shape == (200, 50)
        
        # Step 4: Get statistics
        stats = generator.get_statistics()
        
        assert stats['num_patterns_injected'] == 1
        assert 0.06 <= stats['injected_patterns'][0]['actual_support'] <= 0.10
        
        # Step 5: Save to SPMF
        output_file = tmp_path / "integration_test.spmf"
        generator.to_spmf(str(output_file))
        
        assert output_file.exists()
        
        # Step 6: Verify SPMF file
        transactions = FileIO.read_spmf(str(output_file))
        assert len(transactions) == 200
    
    def test_config_to_file_pipeline(self, tmp_path):
        """Test saving and loading config files."""
        config = {
            "dataset_meta": {
                "num_transactions": 100,
                "num_items": 30,
                "density": 0.1
            },
            "distribution_config": {
                "method": "random",
                "params": {}
            },
            "pattern_injection": []
        }
        
        # Save config
        config_file = tmp_path / "pipeline_config.json"
        ConfigParser.to_file(config, str(config_file))
        
        # Load config
        loaded_config = ConfigParser.from_file(str(config_file))
        
        # Generate from loaded config
        generator = DataGenerator(loaded_config)
        data = generator.generate(seed=123)
        
        assert data.shape[0] == 100
        assert data.shape[1] == 30
    
    def test_multiple_patterns(self, tmp_path):
        """Test generation with multiple injected patterns."""
        config = {
            "dataset_meta": {
                "num_transactions": 500,
                "num_items": 100,
                "density": 0.1
            },
            "distribution_config": {
                "method": "zipf",
                "params": {"alpha": 1.1}
            },
            "pattern_injection": [
                {
                    "id": "pattern_1",
                    "items": [1, 2, 3],
                    "target_support": 0.1,
                    "noise_ratio": 0.0
                },
                {
                    "id": "pattern_2",
                    "items": [10, 20],
                    "target_support": 0.15,
                    "noise_ratio": 0.05
                },
                {
                    "id": "pattern_3",
                    "items": [50, 51, 52, 53],
                    "target_support": 0.05,
                    "noise_ratio": 0.1
                }
            ]
        }
        
        parser = ConfigParser()
        validated = parser.parse(config)
        
        generator = DataGenerator(validated)
        data = generator.generate(seed=999)
        
        stats = generator.get_statistics()
        
        # Verify all patterns were injected
        assert stats['num_patterns_injected'] == 3
        assert len(stats['injected_patterns']) == 3
        
        # Check each pattern has reasonable support
        for pattern_stat in stats['injected_patterns']:
            target = pattern_stat['target_support']
            actual = pattern_stat['actual_support']
            # Allow some variance
            assert actual >= target * 0.7  # At least 70% of target


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
