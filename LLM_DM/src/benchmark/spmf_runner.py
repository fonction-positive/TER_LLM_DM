"""
SPMF Runner Module

Executes SPMF algorithms via subprocess and parses results.
"""

import subprocess
import os
import time
from typing import Dict, List, Optional
from pathlib import Path


class SPMFRunner:
    """
    Wrapper for running SPMF (Sequential Pattern Mining Framework) algorithms.
    
    SPMF is a Java-based library that must be installed separately.
    """
    
    # Common SPMF algorithms
    ALGORITHMS = {
        "Apriori": "Apriori",
        "FPGrowth": "FPGrowth",
        "Eclat": "Eclat",
        "LCM": "LCM",
        "CHARM": "Charm"
    }
    
    def __init__(
        self,
        spmf_jar_path: str,
        java_memory: str = "4g"
    ):
        """
        Initialize SPMF runner.
        
        Args:
            spmf_jar_path: Path to spmf.jar file
            java_memory: Maximum Java heap memory (e.g., "4g", "2048m")
        """
        self.jar_path = Path(spmf_jar_path)
        self.java_memory = java_memory
        
        if not self.jar_path.exists():
            raise FileNotFoundError(
                f"SPMF jar not found at {self.jar_path}. "
                f"Please download from https://www.philippe-fournier-viger.com/spmf/"
            )
        
        # Verify Java is installed
        try:
            subprocess.run(
                ["java", "-version"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "Java is not installed or not in PATH. "
                "Please install Java 8 or higher."
            )
    
    def run_algorithm(
        self,
        algorithm: str,
        input_file: str,
        output_file: str,
        min_support: float,
        timeout: int = 300
    ) -> Dict:
        """
        Run a frequent itemset mining algorithm.
        
        Args:
            algorithm: Algorithm name (e.g., "Apriori", "FPGrowth")
            input_file: Path to input data (SPMF format)
            output_file: Path to save results
            min_support: Minimum support threshold (0.0-1.0 or absolute count)
            timeout: Maximum execution time in seconds
        
        Returns:
            Dictionary with execution metrics
        
        Raises:
            ValueError: If algorithm is unknown
            TimeoutError: If execution exceeds timeout
            RuntimeError: If SPMF execution fails
        """
        if algorithm not in self.ALGORITHMS:
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Valid options: {list(self.ALGORITHMS.keys())}"
            )
        
        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Build command
        cmd = [
            "java",
            f"-Xmx{self.java_memory}",
            "-jar",
            str(self.jar_path),
            "run",
            self.ALGORITHMS[algorithm],
            str(input_file),
            str(output_file),
            str(min_support)
        ]
        
        # Execute
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            
            execution_time = time.time() - start_time
            
            # Parse output
            metrics = {
                "algorithm": algorithm,
                "min_support": min_support,
                "execution_time": execution_time,
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            # Try to extract patterns count from output file
            try:
                with open(output_file, "r") as f:
                    patterns = f.readlines()
                metrics["num_patterns_found"] = len(patterns)
            except Exception:
                metrics["num_patterns_found"] = None
            
            return metrics
        
        except subprocess.TimeoutExpired:
            raise TimeoutError(
                f"Algorithm '{algorithm}' exceeded timeout of {timeout}s"
            )
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"SPMF execution failed:\n"
                f"Command: {' '.join(cmd)}\n"
                f"Error: {e.stderr}"
            )
    
    def parse_output(self, output_file: str) -> List[Dict]:
        """
        Parse SPMF output file to extract patterns.
        
        Args:
            output_file: Path to SPMF output file
        
        Returns:
            List of patterns with their support
        """
        patterns = []
        
        try:
            with open(output_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # SPMF format: items #SUP: support
                    if "#SUP:" in line:
                        parts = line.split("#SUP:")
                        items_str = parts[0].strip()
                        support = int(parts[1].strip())
                        
                        items = [int(x) for x in items_str.split()]
                        
                        patterns.append({
                            "items": items,
                            "support": support
                        })
                    else:
                        # Simple format: just items
                        items = [int(x) for x in line.split()]
                        patterns.append({
                            "items": items,
                            "support": None
                        })
        
        except Exception as e:
            print(f"Warning: Could not parse output file: {e}")
        
        return patterns


if __name__ == "__main__":
    # Test SPMF runner (requires spmf.jar to be available)
    import os
    
    jar_path = os.getenv("SPMF_JAR_PATH", "./lib/spmf.jar")
    
    if Path(jar_path).exists():
        runner = SPMFRunner(jar_path)
        print(f"SPMF runner initialized with jar: {jar_path}")
        print(f"Available algorithms: {list(runner.ALGORITHMS.keys())}")
    else:
        print(f"SPMF jar not found at {jar_path}")
        print("Please download SPMF and set SPMF_JAR_PATH in .env")
