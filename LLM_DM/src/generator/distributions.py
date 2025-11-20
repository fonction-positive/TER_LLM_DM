"""
Distribution Engine Module

Provides statistical distribution functions for item frequency generation.
"""

import numpy as np
from typing import List, Dict, Any
from scipy.stats import zipf, norm, expon


class DistributionEngine:
    """
    Generates item frequency distributions for synthetic data.
    
    Supports various distribution types:
    - Random: Uniform random distribution
    - Zipf: Power law distribution (models real-world long-tail phenomena)
    - Normal: Gaussian distribution
    - Exponential: Exponential decay distribution
    """
    
    @staticmethod
    def generate_item_frequencies(
        num_items: int,
        method: str = "zipf",
        params: Dict[str, Any] = None
    ) -> np.ndarray:
        """
        Generate probability distribution for items.
        
        Args:
            num_items: Number of unique items
            method: Distribution method ("random", "zipf", "normal", "exponential")
            params: Distribution-specific parameters
        
        Returns:
            Array of probabilities (sums to 1.0) for each item
        """
        params = params or {}
        
        if method == "random":
            return DistributionEngine._random_distribution(num_items)
        elif method == "zipf":
            return DistributionEngine._zipf_distribution(num_items, params)
        elif method == "normal":
            return DistributionEngine._normal_distribution(num_items, params)
        elif method == "exponential":
            return DistributionEngine._exponential_distribution(num_items, params)
        else:
            raise ValueError(f"Unknown distribution method: {method}")
    
    @staticmethod
    def _random_distribution(num_items: int) -> np.ndarray:
        """Uniform random distribution."""
        probs = np.ones(num_items)
        return probs / probs.sum()
    
    @staticmethod
    def _zipf_distribution(num_items: int, params: Dict) -> np.ndarray:
        """
        Zipf (power law) distribution.
        
        Common in real-world data: a few items are very frequent,
        most items are rare.
        
        Args:
            params: {"alpha": float} - Zipf parameter (typically 1.0-2.0)
        """
        alpha = params.get("alpha", 1.1)
        
        # Generate Zipf probabilities
        # Higher rank = lower probability
        ranks = np.arange(1, num_items + 1)
        probs = 1.0 / np.power(ranks, alpha)
        
        # Normalize to sum to 1
        return probs / probs.sum()
    
    @staticmethod
    def _normal_distribution(num_items: int, params: Dict) -> np.ndarray:
        """
        Normal (Gaussian) distribution.
        
        Args:
            params: {"mean": float, "std": float}
        """
        mean = params.get("mean", 0.5)
        std = params.get("std", 0.2)
        
        # Generate positions normalized to [0, 1]
        positions = np.linspace(0, 1, num_items)
        
        # Compute Gaussian probabilities
        probs = norm.pdf(positions, loc=mean, scale=std)
        
        # Ensure no negative values and normalize
        probs = np.maximum(probs, 0)
        return probs / probs.sum()
    
    @staticmethod
    def _exponential_distribution(num_items: int, params: Dict) -> np.ndarray:
        """
        Exponential distribution.
        
        Args:
            params: {"scale": float}
        """
        scale = params.get("scale", 1.0)
        
        # Generate exponential probabilities
        x = np.linspace(0, 5, num_items)  # 5 is arbitrary scale
        probs = expon.pdf(x, scale=scale)
        
        return probs / probs.sum()


if __name__ == "__main__":
    # Test distributions
    import matplotlib.pyplot as plt
    
    num_items = 100
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Random
    probs = DistributionEngine.generate_item_frequencies(num_items, "random")
    axes[0, 0].bar(range(num_items), probs)
    axes[0, 0].set_title("Random Distribution")
    axes[0, 0].set_xlabel("Item ID")
    axes[0, 0].set_ylabel("Probability")
    
    # Zipf
    probs = DistributionEngine.generate_item_frequencies(
        num_items, "zipf", {"alpha": 1.2}
    )
    axes[0, 1].bar(range(num_items), probs)
    axes[0, 1].set_title("Zipf Distribution (α=1.2)")
    axes[0, 1].set_xlabel("Item ID")
    axes[0, 1].set_ylabel("Probability")
    
    # Normal
    probs = DistributionEngine.generate_item_frequencies(
        num_items, "normal", {"mean": 0.5, "std": 0.15}
    )
    axes[1, 0].bar(range(num_items), probs)
    axes[1, 0].set_title("Normal Distribution")
    axes[1, 0].set_xlabel("Item ID")
    axes[1, 0].set_ylabel("Probability")
    
    # Exponential
    probs = DistributionEngine.generate_item_frequencies(
        num_items, "exponential", {"scale": 0.5}
    )
    axes[1, 1].bar(range(num_items), probs)
    axes[1, 1].set_title("Exponential Distribution")
    axes[1, 1].set_xlabel("Item ID")
    axes[1, 1].set_ylabel("Probability")
    
    plt.tight_layout()
    plt.savefig("distributions_test.png", dpi=150)
    print("Distribution plots saved to distributions_test.png")
