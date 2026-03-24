from typing import Dict, Any

class DatabaseConnector:
    """Handles connections to various database systems"""
    
    def __init__(self, db_type: str, credentials: Dict[str, str]):
        self.db_type = db_type.lower()
        self.credentials = credentials
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            if self.db_type == "athena":
                self._connect_athena()
            elif self.db_type == "snowflake":
                self._connect_snowflake()
            elif self.db_type == "sqlserver":
                self._connect_sqlserver()
            elif self.db_type == "postgres":
                self._connect_postgres()
            elif self.db_type == "mysql":
                self._connect_mysql()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
            
            return True
        except Exception as e:
            print(f"Connection failed: {str(e)}")
            return False
    
    def _connect_athena(self):
        """Connect to Amazon Athena"""
        try:
            import boto3
            self.connection = boto3.client(
                "athena",
                region_name=self.credentials.get("region", "us-east-1"),
                aws_access_key_id=self.credentials["access_key"],
                aws_secret_access_key=self.credentials["secret_key"]
            )
        except ImportError:
            raise ImportError("boto3 not installed. Install with: pip install boto3")
    
    def _connect_snowflake(self):
        """Connect to Snowflake"""
        try:
            import snowflake.connector
            self.connection = snowflake.connector.connect(
                user=self.credentials["username"],
                password=self.credentials["password"],
                account=self.credentials["account"],
                warehouse=self.credentials.get("warehouse"),
                database=self.credentials.get("database")
            )
        except ImportError:
            raise ImportError("snowflake-connector-python not installed")
    
    def _connect_sqlserver(self):
        """Connect to SQL Server"""
        try:
            import pyodbc
            connection_string = (
                f"Driver={{ODBC Driver 17 for SQL Server}};"
                f"Server={self.credentials['server']};"
                f"Database={self.credentials['database']};"
                f"UID={self.credentials['username']};"
                f"PWD={self.credentials['password']}"
            )
            self.connection = pyodbc.connect(connection_string)
        except ImportError:
            raise ImportError("pyodbc not installed")
    
    def _connect_postgres(self):
        """Connect to PostgreSQL"""
        try:
            from sqlalchemy import create_engine
            engine = create_engine(
                f"postgresql://{self.credentials['username']}:{self.credentials['password']}"
                f"@{self.credentials['host']}:{self.credentials.get('port', 5432)}"
                f"/{self.credentials['database']}"
            )
            self.connection = engine
        except ImportError:
            raise ImportError("sqlalchemy not installed")
    
    def _connect_mysql(self):
        """Connect to MySQL"""
        try:
            from sqlalchemy import create_engine
            engine = create_engine(
                f"mysql+pymysql://{self.credentials['username']}:{self.credentials['password']}"
                f"@{self.credentials['host']}:{self.credentials.get('port', 3306)}"
                f"/{self.credentials['database']}"
            )
            self.connection = engine
        except ImportError:
            raise ImportError("sqlalchemy not installed")
    
    def execute_query(self, query: str) -> bool:
        """Execute SQL query"""
        try:
            if self.db_type == "athena":
                self._execute_athena_query(query)
            else:
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"Query execution failed: {str(e)}")
            return False
    
    def _execute_athena_query(self, query: str):
        """Execute query on Athena"""
        self.connection.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": self.credentials.get("database", "default")},
            ResultConfiguration={"OutputLocation": self.credentials["output_location"]}
        )
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
