from pydantic import BaseModel, Field
from typing import List, Optional

class Column(BaseModel):
    """Database column definition"""
    name: str = Field(..., description="Column name")
    data_type: str = Field(..., description="Data type (VARCHAR, INT, DATETIME, etc.)")
    nullable: bool = Field(default=True, description="Whether column allows NULL values")
    primary_key: bool = Field(default=False, description="Whether this is a primary key")
    foreign_key: Optional[str] = Field(default=None, description="Foreign key reference (table.column)")
    description: Optional[str] = Field(default=None, description="Column description")

class Table(BaseModel):
    """Database table definition"""
    name: str = Field(..., description="Table name")
    columns: List[Column] = Field(..., description="List of columns in the table")
    description: Optional[str] = Field(default=None, description="Table description")
    indexes: Optional[List[str]] = Field(default=None, description="Index definitions")

class Relationship(BaseModel):
    """Relationship between tables"""
    from_table: str = Field(..., description="Source table name")
    to_table: str = Field(..., description="Target table name")
    from_column: str = Field(..., description="Source column name")
    to_column: str = Field(..., description="Target column name")
    relationship_type: str = Field(default="one_to_many", description="Type: one_to_one, one_to_many, many_to_many")

class SchemaDesign(BaseModel):
    """Complete database schema design"""
    schema_type: str = Field(..., description="Schema type: 'star', 'snowflake', or 'normalized'")
    tables: List[Table] = Field(..., description="List of tables in the schema")
    relationships: List[Relationship] = Field(default_factory=list, description="Relationships between tables")
    normalization_notes: str = Field(..., description="Notes on normalization approach")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for optimization")
    sql_statements: List[str] = Field(default_factory=list, description="SQL DDL statements to create tables")
    
    class Config:
        json_schema_extra = {
            "example": {
                "schema_type": "normalized",
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "user_id", "data_type": "INT", "primary_key": True},
                            {"name": "email", "data_type": "VARCHAR(255)", "nullable": False}
                        ]
                    }
                ],
                "relationships": [],
                "normalization_notes": "Fully normalized to 3NF",
                "recommendations": ["Add indexes on email column"],
                "sql_statements": ["CREATE TABLE users (user_id INT PRIMARY KEY, email VARCHAR(255) NOT NULL)"]
            }
        }

class DataAnalysis(BaseModel):
    """Analysis of uploaded data file"""
    row_count: int = Field(..., description="Number of rows in the file")
    column_count: int = Field(..., description="Number of columns in the file")
    columns: List[dict] = Field(..., description="Column metadata")
    sample_data: List[dict] = Field(..., description="Sample rows from the file")
    potential_keys: dict = Field(..., description="Detected primary and foreign key candidates")
