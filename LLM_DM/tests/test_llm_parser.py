"""
Unit Tests for LLM Parser Module
"""

import pytest
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm.parser import ConfigParser, ConfigValidationError


class TestConfigParser:
    """Tests for configuration parser."""
    
    def test_valid_config(self):
        """Test parsing a valid configuration."""
        config = {
            "dataset_meta": {
                "num_transactions": 1000,
                "num_items": 100,
                "density": 0.1
            },
            "distribution_config": {
                "method": "zipf",
                "params": {"alpha": 1.2}
            },
            "pattern_injection": []
        }
        
        parser = ConfigParser()
        validated = parser.parse(config)
        
        assert validated["dataset_meta"]["num_transactions"] == 1000
        assert validated["dataset_meta"]["num_items"] == 100
        assert validated["distribution_config"]["method"] == "zipf"
    
    def test_missing_required_fields_strict(self):
        """Test that missing required fields raise error in strict mode."""
        config = {
            "dataset_meta": {
                "num_transactions": 1000
                # missing num_items
            },
            "distribution_config": {
                "method": "zipf",
                "params": {}
            }
        }
        
        parser = ConfigParser(strict_mode=True)
        
        with pytest.raises(ConfigValidationError):
            parser.parse(config)
    
    def test_missing_required_fields_non_strict(self):
        """Test that missing fields get defaults in non-strict mode."""
        config = {
            "dataset_meta": {
                "num_transactions": 1000
                # missing num_items
            },
            "distribution_config": {
                "method": "zipf",
                "params": {}
            }
        }
        
        parser = ConfigParser(strict_mode=False)
        validated = parser.parse(config)
        
        # Should have default num_items
        assert "num_items" in validated["dataset_meta"]
        assert validated["dataset_meta"]["num_items"] > 0
    
    def test_invalid_density(self):
        """Test that invalid density raises error."""
        config = {
            "dataset_meta": {
                "num_transactions": 1000,
                "num_items": 100,
                "density": 1.5  # Invalid: > 1.0
            },
            "distribution_config": {
                "method": "random",
                "params": {}
            }
        }
        
        parser = ConfigParser()
        
        with pytest.raises(ConfigValidationError):
            parser.parse(config)
    
    def test_pattern_injection_validation(self):
        """Test pattern injection validation."""
        config = {
            "dataset_meta": {
                "num_transactions": 1000,
                "num_items": 100,
                "density": 0.1
            },
            "distribution_config": {
                "method": "random",
                "params": {}
            },
            "pattern_injection": [
                {
                    "items": [1, 5, 10],
                    "target_support": 0.05,
                    "noise_ratio": 0.1
                }
            ]
        }
        
        parser = ConfigParser()
        validated = parser.parse(config)
        
        assert len(validated["pattern_injection"]) == 1
        assert validated["pattern_injection"][0]["items"] == [1, 5, 10]
    
    def test_invalid_pattern_support(self):
        """Test that invalid support raises error."""
        config = {
            "dataset_meta": {
                "num_transactions": 1000,
                "num_items": 100,
                "density": 0.1
            },
            "distribution_config": {
                "method": "random",
                "params": {}
            },
            "pattern_injection": [
                {
                    "items": [1, 2],
                    "target_support": 1.5  # Invalid: > 1.0
                }
            ]
        }
        
        parser = ConfigParser(strict_mode=True)
        
        with pytest.raises(ConfigValidationError):
            parser.parse(config)
    
    def test_file_io(self, tmp_path):
        """Test reading/writing config to file."""
        config = {
            "dataset_meta": {
                "num_transactions": 500,
                "num_items": 50,
                "density": 0.15
            },
            "distribution_config": {
                "method": "zipf",
                "params": {"alpha": 1.0}
            },
            "pattern_injection": []
        }
        
        # Write to file
        filepath = tmp_path / "test_config.json"
        ConfigParser.to_file(config, str(filepath))
        
        assert filepath.exists()
        
        # Read back
        loaded = ConfigParser.from_file(str(filepath))
        
        assert loaded["dataset_meta"]["num_transactions"] == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
