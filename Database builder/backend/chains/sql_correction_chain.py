from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any

class SQLCorrectionChain:
    """Chain for correcting SQL errors using LLM"""
    
    def __init__(self, llm):
        self.llm = llm
        self._create_chain()
    
    def _create_chain(self):
        """Create the SQL correction chain"""
        self.correction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert SQL developer. Your task is to fix SQL errors.

Given:
1. A failed SQL statement
2. The error message from the database
3. The target database type

Provide a corrected SQL statement that will work.

IMPORTANT:
- Return ONLY the corrected SQL statement, nothing else
- Do not include explanations or comments
- Ensure the SQL is valid for the target database
- Preserve the original intent of the query
- Use proper syntax for the database type specified"""),
            ("human", """Database Type: {db_type}

Failed SQL:
{failed_sql}

Error Message:
{error_message}

Please provide the corrected SQL statement:""")
        ])
    
    def correct_sql(self, failed_sql: str, error_message: str, db_type: str = "snowflake") -> Dict[str, Any]:
        """
        Correct a failed SQL statement
        
        Args:
            failed_sql: The SQL statement that failed
            error_message: The error message from the database
            db_type: The target database type
        
        Returns:
            Dictionary with corrected SQL and metadata
        """
        try:
            # Create the chain
            chain = self.correction_prompt | self.llm
            
            # Run the chain
            response = chain.invoke({
                "failed_sql": failed_sql,
                "error_message": error_message,
                "db_type": db_type
            })
            
            # Extract corrected SQL from response
            corrected_sql = response.content.strip()
            
            # Clean up the SQL - remove markdown code blocks if present
            if corrected_sql.startswith("```"):
                corrected_sql = corrected_sql.split("```")[1]
                if corrected_sql.startswith("sql"):
                    corrected_sql = corrected_sql[3:]
                corrected_sql = corrected_sql.strip()
            
            return {
                "success": True,
                "corrected_sql": corrected_sql,
                "original_sql": failed_sql,
                "error_message": error_message,
                "db_type": db_type
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_sql": failed_sql
            }
