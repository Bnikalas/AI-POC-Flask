from typing import Dict, List, Any
from config import Config

class PIIDetector:
    """Detects Personally Identifiable Information (PII) in data using AI"""
    
    def __init__(self, llm):
        """
        Initialize PII detector with LLM
        
        Args:
            llm: LangChain LLM instance
        """
        self.llm = llm
    
    def detect_pii_columns(self, columns: List[Dict[str, Any]], sample_data: List[Dict]) -> List[str]:
        """
        Detect which columns contain PII using AI
        
        Args:
            columns: List of column info dicts with 'name' and 'dtype'
            sample_data: Sample rows from the data (list of dicts)
            
        Returns:
            List of column names that contain PII
        """
        try:
            # Build prompt for PII detection
            column_names = [col["name"] for col in columns]
            
            prompt = f"""Analyze the following column names and sample data to identify which columns likely contain Personally Identifiable Information (PII).

Column Names: {', '.join(column_names)}

Sample Data (first 3 rows):
{self._format_sample_data(sample_data, column_names)}

PII includes: names, email addresses, phone numbers, social security numbers, credit card numbers, addresses, dates of birth, IP addresses, etc.

Respond with ONLY a JSON array of column names that contain PII. Example: ["email", "phone_number"]
If no PII detected, respond with: []

Response:"""
            
            # Call LLM
            response = self.llm.invoke(prompt)
            
            # Parse response - handle both string and object responses
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON array from response
            import json
            import re
            
            json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            if json_match:
                pii_columns = json.loads(json_match.group())
                print(f"PII Detection Result: {pii_columns}")
                return pii_columns if isinstance(pii_columns, list) else []
            
            print("PII Detection: No JSON array found in response")
            return []
            
        except Exception as e:
            print(f"PII detection error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    @staticmethod
    def _format_sample_data(sample_data: List[Dict], column_names: List[str]) -> str:
        """Format sample data for display in prompt"""
        if not sample_data:
            return "No sample data available"
        
        lines = []
        for i, row in enumerate(sample_data[:3], 1):
            row_str = ", ".join([f"{col}: {row.get(col, 'N/A')}" for col in column_names])
            lines.append(f"Row {i}: {row_str}")
        
        return "\n".join(lines)
