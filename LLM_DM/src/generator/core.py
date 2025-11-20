"""
Core Data Generator Module

Main engine for generating synthetic transactional datasets.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from .distributions import DistributionEngine
from .injector import PatternInjector


class DataGenerator:
    """
    Main class for generating synthetic transactional data.
    
    Combines distribution modeling and pattern injection to create
    realistic benchmark datasets for data mining algorithms.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize generator with configuration.
        
        Args:
            config: Validated configuration dictionary with keys:
                   - dataset_meta
                   - distribution_config
                   - pattern_injection
        """
        self.config = config
        self.meta = config["dataset_meta"]
        self.dist_config = config["distribution_config"]
        self.patterns = config.get("pattern_injection", [])
        
        self.num_transactions = self.meta["num_transactions"]
        self.num_items = self.meta["num_items"]
        self.density = self.meta["density"]
        self.avg_transaction_len = self.meta.get("avg_transaction_len")
        
        # Initialize components
        self.dist_engine = DistributionEngine()
        self.injector = PatternInjector(self.num_transactions, self.num_items)
        
        # Will hold generated data
        self.data: Optional[np.ndarray] = None
    
    def generate(self, seed: Optional[int] = None) -> np.ndarray:
        """
        Generate the complete dataset.
        
        Args:
            seed: Random seed for reproducibility
        
        Returns:
            Binary matrix (num_transactions x num_items)
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Step 1: Generate item frequency distribution
        item_probs = self.dist_engine.generate_item_frequencies(
            self.num_items,
            method=self.dist_config["method"],
            params=self.dist_config["params"]
        )
        
        # Step 2: Generate base transactions
        self.data = self._generate_transactions(item_probs)
        
        # Step 3: Inject patterns (if any)
        if self.patterns:
            self.data = self.injector.inject_multiple_patterns(
                self.data,
                self.patterns
            )
        
        return self.data
    
    def _generate_transactions(self, item_probs: np.ndarray) -> np.ndarray:
        """
        Generate base transactions using item probabilities.
        
        Args:
            item_probs: Probability distribution over items
        
        Returns:
            Binary matrix (num_transactions x num_items)
        """
        data = np.zeros((self.num_transactions, self.num_items), dtype=np.int8)
        
        for i in range(self.num_transactions):
            # Determine transaction length
            if self.avg_transaction_len:
                # Use Poisson distribution around average
                trans_len = np.random.poisson(self.avg_transaction_len)
                trans_len = max(1, min(trans_len, self.num_items))
            else:
                # Use density-based approach
                trans_len = max(1, int(self.num_items * self.density))
            
            # Sample items based on probabilities
            selected_items = np.random.choice(
                self.num_items,
                size=trans_len,
                replace=False,
                p=item_probs
            )
            
            data[i, selected_items] = 1
        
        return data
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the generated dataset.
        
        Returns:
            Dictionary with dataset statistics
        """
        if self.data is None:
            raise RuntimeError("Data not generated yet. Call generate() first.")
        
        transaction_lengths = self.data.sum(axis=1)
        item_frequencies = self.data.sum(axis=0)
        
        stats = {
            "num_transactions": self.num_transactions,
            "num_items": self.num_items,
            "total_entries": int(self.data.sum()),
            "actual_density": float(self.data.sum() / (self.num_transactions * self.num_items)),
            "avg_transaction_length": float(transaction_lengths.mean()),
            "std_transaction_length": float(transaction_lengths.std()),
            "min_transaction_length": int(transaction_lengths.min()),
            "max_transaction_length": int(transaction_lengths.max()),
            "most_frequent_item": int(item_frequencies.argmax()),
            "max_item_frequency": int(item_frequencies.max()),
            "min_item_frequency": int(item_frequencies.min()),
            "num_patterns_injected": len(self.patterns)
        }
        
        # Verify injected patterns
        if self.patterns:
            stats["injected_patterns"] = []
            for pattern in self.patterns:
                actual_support = PatternInjector.verify_pattern(
                    self.data,
                    pattern["items"]
                )
                stats["injected_patterns"].append({
                    "id": pattern.get("id", "unknown"),
                    "items": pattern["items"],
                    "target_support": pattern["target_support"],
                    "actual_support": actual_support
                })
        
        return stats
    
    def to_spmf(self, filepath: str):
        """
        Save dataset in SPMF format.
        
        SPMF format: Each line is a transaction.
        Items are space-separated integers.
        
        Args:
            filepath: Output file path
        """
        if self.data is None:
            raise RuntimeError("Data not generated yet. Call generate() first.")
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for transaction in self.data:
                # Get items (column indices where value is 1)
                items = np.where(transaction == 1)[0]
                # Write as space-separated integers
                f.write(" ".join(map(str, items)) + "\n")
    
    def to_csv(self, filepath: str):
        """
        Save dataset as CSV (binary matrix).
        
        Args:
            filepath: Output file path
        """
        if self.data is None:
            raise RuntimeError("Data not generated yet. Call generate() first.")
        
        import pandas as pd
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        df = pd.DataFrame(
            self.data,
            columns=[f"item_{i}" for i in range(self.num_items)]
        )
        df.to_csv(filepath, index=False)


if __name__ == "__main__":
    # Test data generation
    test_config = {
        "dataset_meta": {
            "num_transactions": 1000,
            "num_items": 100,
            "density": 0.1,
            "avg_transaction_len": 10
        },
        "distribution_config": {
            "method": "zipf",
            "params": {"alpha": 1.2}
        },
        "pattern_injection": [
            {
                "id": "test_pattern",
                "items": [5, 10, 15],
                "target_support": 0.08,
                "noise_ratio": 0.05
            }
        ]
    }
    
    generator = DataGenerator(test_config)
    data = generator.generate(seed=42)
    
    # Print statistics
    import json
    stats = generator.get_statistics()
    print(json.dumps(stats, indent=2))
    
    # Save to file
    generator.to_spmf("test_output.spmf")
    print("\nData saved to test_output.spmf")
