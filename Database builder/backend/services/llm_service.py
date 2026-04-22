from typing import Dict, Any
from config import Config
from chains.schema_designer_chain import SchemaDesignerChain
from models.schema_models import SchemaDesign

try:
    from langchain_openrouter import ChatOpenRouter
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"Warning: langchain_openrouter not installed: {e}")
    LANGCHAIN_AVAILABLE = False

class LLMService:
    """LangChain-based LLM service for schema design using OpenRouter"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize LLM service with OpenRouter
        
        Args:
            api_key: OpenRouter API key (uses Config.OPENROUTER_API_KEY if not provided)
            model: LLM model name (uses Config.DEFAULT_LLM_MODEL if not provided)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError(
                "langchain_openrouter is not installed. Install with:\n"
                "pip install langchain-openrouter\n"
                "Or reinstall requirements: pip install -r backend/requirements.txt"
            )
        
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        self.model = model or Config.DEFAULT_LLM_MODEL
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required. Set OPENROUTER_API_KEY in .env")
        
        # Initialize LangChain ChatOpenRouter
        try:
            self.llm = ChatOpenRouter(
                model=self.model,
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS,
                openrouter_api_key=self.api_key
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ChatOpenRouter: {str(e)}")
        
        # Initialize schema designer chain
        try:
            self.schema_chain = SchemaDesignerChain(self.llm)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize schema chain: {str(e)}")
        
        self.total_cost = 0.0
    
    def design_schema(self, data_analysis: Dict[str, Any], database_type: str = "snowflake", schema_name: str = "PUBLIC", multiple_files: bool = False) -> Dict[str, Any]:
        """
        Design database schema using LLM
        
        Args:
            data_analysis: Dictionary containing file analysis results (single or multiple files)
            database_type: Target database type
            schema_name: Schema name for the database
            multiple_files: Whether data_analysis contains multiple files
            
        Returns:
            Dictionary with schema design and metadata
        """
        try:
            # If multiple files, combine all analyses into a single analysis for the LLM
            if multiple_files and isinstance(data_analysis, dict):
                combined_analysis = self._combine_file_analyses(data_analysis)
            else:
                combined_analysis = data_analysis
            
            # Use LangChain chain to design schema with database-specific parameters
            schema_design = self.schema_chain.design_schema(combined_analysis, database_type, schema_name)
            
            # Validate schema
            self.schema_chain.validate_schema(schema_design)
            
            return {
                "success": True,
                "schema": schema_design,
                "cost": 0.0,
                "total_cost": self.total_cost
            }
            
        except Exception as e:
            import traceback
            print(f"Schema design error: {str(e)}")
            print(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "schema": None
            }
    
    def _combine_file_analyses(self, file_analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Combine multiple file analyses into a single analysis
        
        Args:
            file_analyses: Dictionary of filename -> analysis
            
        Returns:
            Combined analysis dictionary
        """
        combined_columns = []
        all_column_names = set()
        
        # Combine columns from all files, avoiding duplicates
        for filename, analysis in file_analyses.items():
            if "columns" in analysis:
                for col in analysis["columns"]:
                    col_name = col.get("name", "")
                    if col_name not in all_column_names:
                        combined_columns.append({
                            **col,
                            "source_file": filename
                        })
                        all_column_names.add(col_name)
        
        # Create combined analysis
        combined_analysis = {
            "column_count": len(combined_columns),
            "columns": combined_columns,
            "file_count": len(file_analyses),
            "files": list(file_analyses.keys())
        }
        
        return combined_analysis
    
    def get_total_cost(self) -> float:
        """Get total API cost for this session"""
        return self.total_cost
    
    def reset_cost(self):
        """Reset cost tracking"""
        self.total_cost = 0.0
