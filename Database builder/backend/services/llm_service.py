from typing import Dict, Any
from config import Config
from chains.schema_designer_chain import SchemaDesignerChain
from models.schema_models import SchemaDesign

try:
    from langchain_community.llms import OpenRouter
    from langchain.callbacks import get_openai_callback
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class LLMService:
    """LangChain-based LLM service for schema design"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize LLM service
        
        Args:
            api_key: OpenRouter API key (uses Config.OPENROUTER_API_KEY if not provided)
            model: LLM model name (uses Config.DEFAULT_LLM_MODEL if not provided)
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not installed. Install with: pip install langchain langchain-community")
        
        self.api_key = api_key or Config.OPENROUTER_API_KEY
        self.model = model or Config.DEFAULT_LLM_MODEL
        
        # Initialize LangChain LLM
        self.llm = OpenRouter(
            openrouter_api_key=self.api_key,
            model_name=self.model,
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_TOKENS
        )
        
        # Initialize schema designer chain
        self.schema_chain = SchemaDesignerChain(self.llm)
        self.total_cost = 0.0
    
    def design_schema(self, data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design database schema using LLM
        
        Args:
            data_analysis: Dictionary containing file analysis results
            
        Returns:
            Dictionary with schema design and metadata
        """
        try:
            # Track costs if available
            with get_openai_callback() as cb:
                # Use LangChain chain to design schema
                schema_design = self.schema_chain.design_schema(data_analysis)
                
                # Validate schema
                self.schema_chain.validate_schema(schema_design)
                
                # Track cost
                self.total_cost += cb.total_cost
            
            return {
                "success": True,
                "schema": schema_design.model_dump(),
                "cost": cb.total_cost,
                "total_cost": self.total_cost
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "schema": None
            }
    
    def get_total_cost(self) -> float:
        """Get total API cost for this session"""
        return self.total_cost
    
    def reset_cost(self):
        """Reset cost tracking"""
        self.total_cost = 0.0
