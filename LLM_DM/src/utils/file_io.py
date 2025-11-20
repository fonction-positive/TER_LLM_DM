"""
File I/O Module

Utilities for reading and writing various file formats.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional


class FileIO:
    """
    Centralized file I/O operations for the project.
    """
    
    @staticmethod
    def read_json(filepath: str) -> Dict:
        """
        Read JSON file.
        
        Args:
            filepath: Path to JSON file
        
        Returns:
            Parsed JSON as dictionary
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    @staticmethod
    def write_json(data: Dict, filepath: str, indent: int = 2):
        """
        Write data to JSON file.
        
        Args:
            data: Dictionary to save
            filepath: Output file path
            indent: JSON indentation level
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    
    @staticmethod
    def read_yaml(filepath: str) -> Dict:
        """
        Read YAML file.
        
        Args:
            filepath: Path to YAML file
        
        Returns:
            Parsed YAML as dictionary
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def write_yaml(data: Dict, filepath: str):
        """
        Write data to YAML file.
        
        Args:
            data: Dictionary to save
            filepath: Output file path
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    
    @staticmethod
    def read_spmf(filepath: str) -> List[List[int]]:
        """
        Read SPMF format file.
        
        Args:
            filepath: Path to SPMF file
        
        Returns:
            List of transactions (each transaction is a list of item IDs)
        """
        transactions = []
        
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse space-separated integers
                items = [int(x) for x in line.split() if x.strip()]
                transactions.append(items)
        
        return transactions
    
    @staticmethod
    def write_spmf(transactions: List[List[int]], filepath: str):
        """
        Write transactions to SPMF format file.
        
        Args:
            transactions: List of transactions
            filepath: Output file path
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            for transaction in transactions:
                f.write(" ".join(map(str, transaction)) + "\n")
    
    @staticmethod
    def read_text(filepath: str) -> str:
        """
        Read text file.
        
        Args:
            filepath: Path to text file
        
        Returns:
            File contents as string
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    
    @staticmethod
    def write_text(content: str, filepath: str):
        """
        Write text to file.
        
        Args:
            content: Text content
            filepath: Output file path
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    
    @staticmethod
    def ensure_dir(dirpath: str):
        """
        Ensure directory exists, create if not.
        
        Args:
            dirpath: Directory path
        """
        Path(dirpath).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def list_files(dirpath: str, pattern: str = "*") -> List[str]:
        """
        List files in directory matching pattern.
        
        Args:
            dirpath: Directory path
            pattern: Glob pattern (e.g., "*.json", "*.spmf")
        
        Returns:
            List of file paths
        """
        return [str(p) for p in Path(dirpath).glob(pattern)]


def load_config(config_path: Optional[str] = None) -> Dict:
    """
    Load global configuration from YAML file.
    
    Args:
        config_path: Path to config file (default: config/settings.yaml)
    
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default to config/settings.yaml
        config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    
    return FileIO.read_yaml(str(config_path))


if __name__ == "__main__":
    # Test file I/O
    test_data = {
        "test": "data",
        "number": 123,
        "list": [1, 2, 3]
    }
    
    # Test JSON
    FileIO.write_json(test_data, "test_output.json")
    loaded = FileIO.read_json("test_output.json")
    print("JSON test:", loaded)
    
    # Test SPMF
    transactions = [[1, 2, 3], [2, 4], [1, 3, 5]]
    FileIO.write_spmf(transactions, "test_output.spmf")
    loaded_trans = FileIO.read_spmf("test_output.spmf")
    print("SPMF test:", loaded_trans)
