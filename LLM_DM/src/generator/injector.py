"""
Pattern Injector Module

Injects specific frequent patterns into generated datasets to create
Ground Truth for benchmarking.
"""

import numpy as np
from typing import List, Dict, Set


class PatternInjector:
    """
    Injects predefined patterns into transaction data.
    
    This creates "hidden" frequent itemsets with known support,
    allowing validation of pattern mining algorithm accuracy.
    """
    
    def __init__(self, num_transactions: int, num_items: int):
        """
        Initialize the pattern injector.
        
        Args:
            num_transactions: Total number of transactions in dataset
            num_items: Total number of unique items
        """
        self.num_transactions = num_transactions
        self.num_items = num_items
    
    def inject_pattern(
        self,
        data: np.ndarray,
        pattern_items: List[int],
        target_support: float,
        noise_ratio: float = 0.0
    ) -> np.ndarray:
        """
        Inject a specific pattern into the dataset.
        
        Args:
            data: Binary matrix (num_transactions x num_items)
            pattern_items: List of item IDs to inject together
            target_support: Desired support (0.0-1.0)
            noise_ratio: Probability of randomly omitting an item (0.0-1.0)
        
        Returns:
            Modified data matrix with injected pattern
        
        Raises:
            ValueError: If pattern_items are invalid
        """
        # Validate inputs
        if not pattern_items:
            raise ValueError("pattern_items cannot be empty")
        
        if any(item < 0 or item >= self.num_items for item in pattern_items):
            raise ValueError(
                f"pattern_items must be in range [0, {self.num_items-1}]"
            )
        
        if not (0.0 < target_support <= 1.0):
            raise ValueError("target_support must be between 0 and 1")
        
        if not (0.0 <= noise_ratio < 1.0):
            raise ValueError("noise_ratio must be between 0 and 1")
        
        # Calculate number of transactions to inject into
        # Increase count to compensate for noise
        if noise_ratio > 0:
            # Adjust for expected loss due to noise
            # More aggressive compensation for higher noise ratios
            compensation_factor = 1.0 / (1 - noise_ratio * 0.7)
            adjusted_support = target_support * compensation_factor
            num_injections = int(self.num_transactions * min(adjusted_support, 1.0))
        else:
            num_injections = int(self.num_transactions * target_support)
        
        if num_injections == 0:
            return data  # Support too low, skip injection
        
        # Randomly select transactions to inject pattern into
        transaction_indices = np.random.choice(
            self.num_transactions,
            size=num_injections,
            replace=False
        )
        
        # Inject pattern
        for trans_idx in transaction_indices:
            for item in pattern_items:
                # Apply noise: sometimes skip an item
                if np.random.random() > noise_ratio:
                    data[trans_idx, item] = 1
        
        return data
    
    def inject_multiple_patterns(
        self,
        data: np.ndarray,
        patterns: List[Dict]
    ) -> np.ndarray:
        """
        Inject multiple patterns sequentially.
        
        Args:
            data: Binary matrix (num_transactions x num_items)
            patterns: List of pattern dictionaries with keys:
                     - "items": List[int]
                     - "target_support": float
                     - "noise_ratio": float (optional)
        
        Returns:
            Modified data matrix with all patterns injected
        """
        for pattern in patterns:
            items = pattern["items"]
            support = pattern["target_support"]
            noise = pattern.get("noise_ratio", 0.0)
            
            data = self.inject_pattern(data, items, support, noise)
        
        return data
    
    @staticmethod
    def verify_pattern(
        data: np.ndarray,
        pattern_items: List[int]
    ) -> float:
        """
        Verify the actual support of a pattern in the data.
        
        Args:
            data: Binary matrix (num_transactions x num_items)
            pattern_items: List of item IDs to check
        
        Returns:
            Actual support (fraction of transactions containing all items)
        """
        if not pattern_items:
            return 0.0
        
        # Check each transaction
        contains_pattern = np.ones(data.shape[0], dtype=bool)
        
        for item in pattern_items:
            contains_pattern &= (data[:, item] == 1)
        
        return contains_pattern.sum() / data.shape[0]


if __name__ == "__main__":
    # Test pattern injection
    np.random.seed(42)
    
    num_trans = 1000
    num_items = 50
    
    # Create empty dataset
    data = np.zeros((num_trans, num_items), dtype=int)
    
    # Add some random noise
    for i in range(num_trans):
        num_random_items = np.random.randint(2, 8)
        random_items = np.random.choice(num_items, num_random_items, replace=False)
        data[i, random_items] = 1
    
    # Inject a pattern
    injector = PatternInjector(num_trans, num_items)
    pattern = [5, 10, 15]
    target_support = 0.1
    
    data = injector.inject_pattern(data, pattern, target_support, noise_ratio=0.05)
    
    # Verify
    actual_support = PatternInjector.verify_pattern(data, pattern)
    print(f"Target support: {target_support:.2%}")
    print(f"Actual support: {actual_support:.2%}")
    print(f"Pattern: {pattern}")
