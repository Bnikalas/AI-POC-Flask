from langchain_core.prompts import PromptTemplate
import json
import re
from typing import Dict, Any
from models.schema_models import SchemaDesign
from config import Config

class SchemaDesignerChain:
    """LangChain chain for designing database schemas using LLM"""
    
    def __init__(self, llm):
        """
        Initialize the schema designer chain
        
        Args:
            llm: LangChain LLM instance (e.g., ChatOpenRouter)
        """
        self.llm = llm
        self.chain = self._create_chain()
    
    def _create_chain(self):
        """Create the LangChain chain with prompt"""
        
        prompt_template = """You are an expert database architect. Analyze the following data structure and design an optimal database schema.

Column Details:
{columns_info}

Potential Keys Detected:
- Primary Key Candidates: {primary_keys}
- Foreign Key Candidates: {foreign_keys}

Target Database: {database_type}
Schema Name: {schema_name}

Based on this analysis, design a database schema that:
1. Normalizes the data appropriately
2. Identifies fact and dimension tables if applicable
3. Defines proper relationships
4. Suggests indexes for performance

IMPORTANT: Generate SQL DDL statements that are compatible with {database_type} syntax.
For Snowflake: Use uppercase keywords, include schema name in CREATE TABLE statements (e.g., CREATE TABLE {schema_name}.table_name)
For PostgreSQL: Use lowercase, include schema if specified
For MySQL: Use backticks for identifiers if needed
For SQL Server: Use square brackets for identifiers if needed

Provide your response in the following format:

SCHEMA TYPE: normalized | star | snowflake | any other

TABLES:
- table_name: Description of the table

NORMALIZATION NOTES:
Explanation of normalization approach

RECOMMENDATIONS:
- Recommendation 1
- Recommendation 2

SQL STATEMENTS:
```sql
CREATE or replace TABLE {schema_name}.table_name (
    col_name VARCHAR(255) NOT NULL PRIMARY KEY
);
```

Make sure to include all CREATE TABLE statements and any CREATE INDEX statements."""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=[
                "column_count",
                "columns_info",
                "primary_keys",
                "foreign_keys",
                "database_type",
                "schema_name"
            ]
        )
        
        # Create chain: prompt -> LLM (no parser, just text)
        chain = prompt | self.llm
        return chain
    
    def design_schema(self, data_analysis: Dict[str, Any], database_type: str = "snowflake", schema_name: str = "PUBLIC") -> Dict[str, Any]:
        """
        Design a database schema based on data analysis
        
        Args:
            data_analysis: Dictionary containing file analysis results
            database_type: Target database type (snowflake, postgres, mysql, sqlserver, athena)
            schema_name: Schema name for the database
            
        Returns:
            Dictionary with schema design and SQL statements
            
        Raises:
            ValueError: If schema design fails or is invalid
        """
        try:
            # Prepare input data
            columns_info = json.dumps(data_analysis.get("columns", []), indent=2)
            
            potential_keys = data_analysis.get("potential_keys", {})
            primary_keys = ", ".join(potential_keys.get("primary_key_candidates", [])) or "None detected"
            foreign_keys = ", ".join(potential_keys.get("foreign_key_candidates", [])) or "None detected"
            
            print(f"\n=== Schema Design Started ===")
            print(f"Database Type: {database_type}")
            print(f"Schema Name: {schema_name}")
            print(f"Columns: {len(data_analysis.get('columns', []))}")
            
            # Invoke chain to get LLM response as text
            response = self.chain.invoke({
                "column_count": data_analysis.get("column_count", 0),
                "columns_info": columns_info,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys,
                "database_type": database_type,
                "schema_name": schema_name or "PUBLIC"
            })
            
            print(f"LLM Response received (length: {len(response.content) if hasattr(response, 'content') else len(str(response))})")
            
            # Extract content from response object
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse the text response to extract sections
            schema_design = self._parse_text_response(response_text, schema_name)
            
            print(f"✓ Schema design completed successfully")
            print(f"  SQL Statements: {len(schema_design.get('sql_statements', []))}")
            
            return schema_design
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"\n❌ Schema design error: {str(e)}")
            print(f"Traceback:\n{error_trace}")
            raise ValueError(f"Schema design failed: {str(e)}")
    
    def _parse_text_response(self, response_text: str, schema_name: str) -> Dict[str, Any]:
        """
        Parse the LLM text response to extract schema design details
        
        Args:
            response_text: The text response from LLM
            schema_name: The schema name for SQL generation
            
        Returns:
            Dictionary with schema design details
        """
        schema_design = {
            "schema_type": "normalized",
            "tables": [],
            "relationships": [],
            "normalization_notes": "",
            "recommendations": [],
            "sql_statements": []
        }
        
        # Extract schema type
        schema_type_match = re.search(r'SCHEMA TYPE:\s*(\w+)', response_text, re.IGNORECASE)
        if schema_type_match:
            schema_design["schema_type"] = schema_type_match.group(1).lower()
        
        # Extract normalization notes
        norm_match = re.search(r'NORMALIZATION NOTES:\s*(.*?)(?=RECOMMENDATIONS:|SQL STATEMENTS:|$)', response_text, re.IGNORECASE | re.DOTALL)
        if norm_match:
            schema_design["normalization_notes"] = norm_match.group(1).strip()
        
        # Extract recommendations
        rec_match = re.search(r'RECOMMENDATIONS:\s*(.*?)(?=SQL STATEMENTS:|$)', response_text, re.IGNORECASE | re.DOTALL)
        if rec_match:
            recommendations_text = rec_match.group(1).strip()
            # Split by bullet points or newlines
            recommendations = [line.strip().lstrip('- ').strip() for line in recommendations_text.split('\n') if line.strip()]
            schema_design["recommendations"] = [r for r in recommendations if r]
        
        # Extract SQL statements
        sql_match = re.search(r'SQL STATEMENTS:\s*(.*?)$', response_text, re.IGNORECASE | re.DOTALL)
        if sql_match:
            sql_text = sql_match.group(1).strip()
            
            # Extract SQL from code blocks
            code_blocks = re.findall(r'```(?:sql)?\s*(.*?)```', sql_text, re.DOTALL)
            if code_blocks:
                for block in code_blocks:
                    # Split by semicolon to get individual statements
                    statements = [s.strip() for s in block.split(';') if s.strip()]
                    # Filter out comments and empty statements
                    for stmt in statements:
                        # Skip comment-only lines
                        if not stmt.startswith('--') and stmt:
                            schema_design["sql_statements"].append(stmt)
            else:
                # If no code blocks, try to extract CREATE statements
                create_statements = re.findall(r'(CREATE\s+(?:TABLE|INDEX|SCHEMA).*?(?=CREATE|$))', sql_text, re.IGNORECASE | re.DOTALL)
                for stmt in create_statements:
                    stmt = stmt.strip()
                    if stmt and not stmt.startswith('--'):
                        if stmt.endswith(';'):
                            schema_design["sql_statements"].append(stmt)
                        else:
                            schema_design["sql_statements"].append(stmt + ';')
        
        # Extract tables from TABLES section
        tables_match = re.search(r'TABLES:\s*(.*?)(?=NORMALIZATION NOTES:|RECOMMENDATIONS:|SQL STATEMENTS:|$)', response_text, re.IGNORECASE | re.DOTALL)
        if tables_match:
            tables_text = tables_match.group(1).strip()
            # Parse table descriptions
            table_lines = [line.strip() for line in tables_text.split('\n') if line.strip()]
            for line in table_lines:
                if line.startswith('-'):
                    # Format: - table_name: Description
                    parts = line.lstrip('- ').split(':', 1)
                    if len(parts) == 2:
                        table_name = parts[0].strip()
                        description = parts[1].strip()
                        schema_design["tables"].append({
                            "name": table_name,
                            "description": description
                        })
        
        return schema_design
    
    def validate_schema(self, schema: Dict[str, Any]) -> bool:
        """
        Validate the generated schema
        
        Args:
            schema: Dictionary with schema design
            
        Returns:
            bool: True if schema is valid
        """
        try:
            # Check required fields
            if not schema.get("schema_type"):
                raise ValueError("Schema type is required")
            
            if not schema.get("sql_statements"):
                raise ValueError("At least one SQL statement is required")
            
            # Validate schema type
            valid_types = ["star", "snowflake", "normalized"]
            if schema.get("schema_type") not in valid_types:
                raise ValueError(f"Invalid schema type. Must be one of: {valid_types}")
            
            # Validate SQL statements - just check they're not empty
            for i, sql in enumerate(schema.get("sql_statements", [])):
                if not sql or not isinstance(sql, str):
                    raise ValueError(f"SQL statement {i+1} is invalid")
                # Just check it's not empty, don't validate DDL keywords
                # (comments and other text are allowed)
                if not sql.strip():
                    raise ValueError(f"SQL statement {i+1} is empty")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Schema validation failed: {str(e)}")
