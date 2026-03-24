from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.llms.base import LLM
from langchain.output_parsers import PydanticOutputParser
from langchain.schema import HumanMessage, SystemMessage
import json
from typing import Dict, Any
from models.schema_models import SchemaDesign
from config import Config

class SchemaDesignerChain:
    """LangChain chain for designing database schemas using LLM"""
    
    def __init__(self, llm: LLM):
        """
        Initialize the schema designer chain
        
        Args:
            llm: LangChain LLM instance (e.g., OpenRouter)
        """
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=SchemaDesign)
        self.chain = self._create_chain()
    
    def _create_chain(self):
        """Create the LangChain chain with prompt and parser"""
        
        prompt_template = """You are an expert database architect. Analyze the following data structure and design an optimal database schema.

Data Analysis:
- Total Rows: {row_count}
- Total Columns: {column_count}

Column Details:
{columns_info}

Sample Data:
{sample_data}

Potential Keys Detected:
- Primary Key Candidates: {primary_keys}
- Foreign Key Candidates: {foreign_keys}

Based on this analysis, design a database schema that:
1. Normalizes the data appropriately
2. Identifies fact and dimension tables if applicable
3. Defines proper relationships
4. Suggests indexes for performance

{format_instructions}

Provide your response as a valid JSON object."""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=[
                "row_count",
                "column_count",
                "columns_info",
                "sample_data",
                "primary_keys",
                "foreign_keys"
            ],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            }
        )
        
        # Create chain: prompt -> LLM -> parser
        chain = prompt | self.llm | self.parser
        return chain
    
    def design_schema(self, data_analysis: Dict[str, Any]) -> SchemaDesign:
        """
        Design a database schema based on data analysis
        
        Args:
            data_analysis: Dictionary containing file analysis results
            
        Returns:
            SchemaDesign: Pydantic model with complete schema design
            
        Raises:
            ValueError: If schema design fails or is invalid
        """
        try:
            # Prepare input data
            columns_info = json.dumps(data_analysis.get("columns", []), indent=2)
            sample_data = json.dumps(data_analysis.get("sample_data", [])[:3], indent=2)
            
            potential_keys = data_analysis.get("potential_keys", {})
            primary_keys = ", ".join(potential_keys.get("primary_key_candidates", [])) or "None detected"
            foreign_keys = ", ".join(potential_keys.get("foreign_key_candidates", [])) or "None detected"
            
            # Invoke chain
            result = self.chain.invoke({
                "row_count": data_analysis.get("row_count", 0),
                "column_count": data_analysis.get("column_count", 0),
                "columns_info": columns_info,
                "sample_data": sample_data,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys
            })
            
            return result
            
        except Exception as e:
            raise ValueError(f"Schema design failed: {str(e)}")
    
    def validate_schema(self, schema: SchemaDesign) -> bool:
        """
        Validate the generated schema
        
        Args:
            schema: SchemaDesign object to validate
            
        Returns:
            bool: True if schema is valid
        """
        try:
            # Check required fields
            if not schema.schema_type:
                raise ValueError("Schema type is required")
            
            if not schema.tables:
                raise ValueError("At least one table is required")
            
            # Validate schema type
            valid_types = ["star", "snowflake", "normalized"]
            if schema.schema_type not in valid_types:
                raise ValueError(f"Invalid schema type. Must be one of: {valid_types}")
            
            # Validate tables
            for table in schema.tables:
                if not table.name:
                    raise ValueError("Table name is required")
                if not table.columns:
                    raise ValueError(f"Table {table.name} must have at least one column")
                
                # Validate columns
                for column in table.columns:
                    if not column.name:
                        raise ValueError(f"Column name is required in table {table.name}")
                    if not column.data_type:
                        raise ValueError(f"Data type is required for column {column.name}")
            
            # Validate relationships
            table_names = {table.name for table in schema.tables}
            for rel in schema.relationships:
                if rel.from_table not in table_names:
                    raise ValueError(f"Relationship references non-existent table: {rel.from_table}")
                if rel.to_table not in table_names:
                    raise ValueError(f"Relationship references non-existent table: {rel.to_table}")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Schema validation failed: {str(e)}")
