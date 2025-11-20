"""
Metrics Calculator Module

Calculates and compares performance metrics for benchmarking.
"""

import time
from typing import Dict, List, Set, Optional
import json
from pathlib import Path


class MetricsCalculator:
    """
    Calculates performance metrics for pattern mining algorithms.
    
    Metrics include:
    - Execution time
    - Memory usage (if available)
    - Number of patterns found
    - Precision and Recall (if ground truth is available)
    """
    
    def __init__(self, ground_truth: Optional[List[Dict]] = None):
        """
        Initialize metrics calculator.
        
        Args:
            ground_truth: List of injected patterns with format:
                         [{"items": [1, 2, 3], "target_support": 0.05}, ...]
        """
        self.ground_truth = ground_truth or []
    
    def calculate_accuracy(
        self,
        found_patterns: List[Dict],
        min_support_threshold: float
    ) -> Dict:
        """
        Calculate precision and recall against ground truth.
        
        Args:
            found_patterns: Patterns found by algorithm
                           [{"items": [1, 2], "support": 50}, ...]
            min_support_threshold: Minimum support used in mining
        
        Returns:
            Dictionary with precision, recall, and F1 score
        """
        if not self.ground_truth:
            return {
                "precision": None,
                "recall": None,
                "f1_score": None,
                "note": "No ground truth available"
            }
        
        # Convert patterns to sets for comparison
        ground_truth_sets = [
            frozenset(p["items"]) for p in self.ground_truth
            if p.get("target_support", 0) >= min_support_threshold
        ]
        
        found_sets = [frozenset(p["items"]) for p in found_patterns]
        
        # Calculate metrics
        true_positives = len([p for p in found_sets if p in ground_truth_sets])
        false_positives = len([p for p in found_sets if p not in ground_truth_sets])
        false_negatives = len([p for p in ground_truth_sets if p not in found_sets])
        
        # Precision: TP / (TP + FP)
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0.0
        )
        
        # Recall: TP / (TP + FN)
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0.0
        )
        
        # F1 Score: 2 * (Precision * Recall) / (Precision + Recall)
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "ground_truth_count": len(ground_truth_sets),
            "found_count": len(found_sets)
        }
    
    def compare_algorithms(
        self,
        results: List[Dict]
    ) -> Dict:
        """
        Compare performance of multiple algorithm runs.
        
        Args:
            results: List of result dictionaries from algorithm runs
        
        Returns:
            Comparison summary
        """
        if not results:
            return {"error": "No results to compare"}
        
        comparison = {
            "algorithms": [],
            "fastest": None,
            "most_patterns": None,
            "best_recall": None
        }
        
        fastest_time = float('inf')
        most_patterns = 0
        best_recall = 0.0
        
        for result in results:
            algo_name = result.get("algorithm", "Unknown")
            exec_time = result.get("execution_time", float('inf'))
            num_patterns = result.get("num_patterns_found", 0)
            accuracy = result.get("accuracy", {})
            recall = accuracy.get("recall", 0.0) if accuracy else 0.0
            
            comparison["algorithms"].append({
                "name": algo_name,
                "execution_time": exec_time,
                "num_patterns": num_patterns,
                "recall": recall
            })
            
            if exec_time < fastest_time:
                fastest_time = exec_time
                comparison["fastest"] = algo_name
            
            if num_patterns > most_patterns:
                most_patterns = num_patterns
                comparison["most_patterns"] = algo_name
            
            if recall and recall > best_recall:
                best_recall = recall
                comparison["best_recall"] = algo_name
        
        return comparison
    
    def generate_report(
        self,
        results: Dict,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a human-readable benchmark report.
        
        Args:
            results: Results dictionary from benchmark run
            output_file: Optional file path to save report
        
        Returns:
            Report as formatted string
        """
        report_lines = [
            "=" * 60,
            "FIDD-Bench Benchmark Report",
            "=" * 60,
            ""
        ]
        
        # Dataset info
        if "dataset_info" in results:
            report_lines.extend([
                "Dataset Information:",
                f"  Transactions: {results['dataset_info'].get('num_transactions', 'N/A')}",
                f"  Items: {results['dataset_info'].get('num_items', 'N/A')}",
                f"  Density: {results['dataset_info'].get('actual_density', 'N/A'):.2%}",
                ""
            ])
        
        # Algorithm results
        if "algorithm_results" in results:
            report_lines.append("Algorithm Results:")
            for algo_result in results["algorithm_results"]:
                algo_name = algo_result.get("algorithm", "Unknown")
                report_lines.extend([
                    f"\n  {algo_name}:",
                    f"    Execution Time: {algo_result.get('execution_time', 'N/A'):.4f}s",
                    f"    Patterns Found: {algo_result.get('num_patterns_found', 'N/A')}",
                ])
                
                if "accuracy" in algo_result:
                    acc = algo_result["accuracy"]
                    if acc.get("precision") is not None:
                        report_lines.extend([
                            f"    Precision: {acc['precision']:.2%}",
                            f"    Recall: {acc['recall']:.2%}",
                            f"    F1 Score: {acc['f1_score']:.4f}"
                        ])
            
            report_lines.append("")
        
        # Comparison
        if "comparison" in results:
            comp = results["comparison"]
            report_lines.extend([
                "Performance Comparison:",
                f"  Fastest Algorithm: {comp.get('fastest', 'N/A')}",
                f"  Most Patterns Found: {comp.get('most_patterns', 'N/A')}",
                f"  Best Recall: {comp.get('best_recall', 'N/A')}",
                ""
            ])
        
        report_lines.append("=" * 60)
        
        report = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
        
        return report


if __name__ == "__main__":
    # Test metrics calculation
    ground_truth = [
        {"items": [1, 2, 3], "target_support": 0.1},
        {"items": [5, 10], "target_support": 0.05}
    ]
    
    found_patterns = [
        {"items": [1, 2, 3], "support": 100},
        {"items": [5, 10], "support": 50},
        {"items": [7, 8], "support": 40}  # False positive
    ]
    
    calculator = MetricsCalculator(ground_truth)
    accuracy = calculator.calculate_accuracy(found_patterns, min_support_threshold=0.04)
    
    print("Accuracy Metrics:")
    print(json.dumps(accuracy, indent=2))
