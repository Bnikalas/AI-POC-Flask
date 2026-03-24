import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # LangChain Configuration
    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "database-creator")
    
    # LLM Configuration
    DEFAULT_LLM_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
    LLM_TEMPERATURE = 0.7
    LLM_MAX_TOKENS = 2000
    
    # Supported databases
    SUPPORTED_DATABASES = {
        "athena": "Amazon Athena",
        "snowflake": "Snowflake",
        "sqlserver": "SQL Server",
        "postgres": "PostgreSQL",
        "mysql": "MySQL"
    }
    
    # File upload settings
    UPLOAD_FOLDER = "uploads"
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {"csv", "parquet"}
    
    # Caching Configuration
    ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"
    CACHE_TYPE = os.getenv("CACHE_TYPE", "in_memory")  # "in_memory" or "redis"
