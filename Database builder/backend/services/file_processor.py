import csv
import json
from pathlib import Path
from typing import Dict, List, Any
from models.schema_models import DataAnalysis

class FileProcessor:
    """Handles CSV and Parquet file processing"""
    
    @staticmethod
    def read_file(file_path: str) -> List[Dict]:
        """Read CSV or Parquet file"""
        path = Path(file_path)
        
        if path.suffix.lower() == ".csv":
            return FileProcessor._read_csv(file_path)
        elif path.suffix.lower() == ".parquet":
            raise ValueError("Parquet support requires pandas. Please use CSV format.")
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    @staticmethod
    def _read_csv(file_path: str) -> List[Dict]:
        """Read CSV file"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def analyze_data_structure(data: List[Dict]) -> dict:
        """
        Analyze data structure and return metadata as dictionary
        
        Args:
            data: List of dictionaries from CSV file
            
        Returns:
            dict: Analysis results with all required fields
        """
        if not data:
            raise ValueError("No data found in file")
        
        columns = list(data[0].keys())
        analysis_columns = []
        
        for col in columns:
            values = [row.get(col) for row in data if row.get(col)]
            unique_values = set(values)
            null_count = len(data) - len(values)
            
            col_info = {
                "name": col,
                "dtype": "string",
                "null_count": null_count,
                "unique_count": len(unique_values),
                "sample_values": list(unique_values)[:3]
            }
            analysis_columns.append(col_info)
        
        # Detect potential keys
        potential_keys = FileProcessor.detect_potential_keys(data)
        
        # Return as dictionary (compatible with both old and new code)
        analysis = {
            "row_count": len(data),
            "column_count": len(columns),
            "columns": analysis_columns,
            "sample_data": data[:5],
            "potential_keys": potential_keys
        }
        
        return analysis
    
    @staticmethod
    def detect_potential_keys(data: List[Dict]) -> Dict[str, List[str]]:
        """
        Detect potential primary and foreign keys
        
        Args:
            data: List of dictionaries from CSV file
            
        Returns:
            Dictionary with primary and foreign key candidates
        """
        potential_keys = {
            "primary_key_candidates": [],
            "foreign_key_candidates": []
        }
        
        if not data:
            return potential_keys
        
        columns = list(data[0].keys())
        
        # Primary key candidates: columns with unique values
        for col in columns:
            values = [row.get(col) for row in data]
            if len(set(values)) == len(data):
                potential_keys["primary_key_candidates"].append(col)
        
        # Foreign key candidates: columns ending with _id
        for col in columns:
            if col.endswith("_id") and col not in potential_keys["primary_key_candidates"]:
                potential_keys["foreign_key_candidates"].append(col)
        
        return potential_keys
