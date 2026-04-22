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
            
            # Validate required credentials
            required = ["username", "password", "account"]
            missing = [k for k in required if k not in self.credentials or not self.credentials[k]]
            if missing:
                raise ValueError(f"Missing Snowflake credentials: {', '.join(missing)}")
            
            account = self.credentials["account"].strip()
            
            # Clean up account identifier - remove URL parts if present
            if "snowflakecomputing.com" in account:
                # Extract just the account ID from full URL
                account = account.split(".")[0]
                print(f"Cleaned account ID from URL: {account}")
            
            # Build connection parameters
            conn_params = {
                "user": self.credentials["username"].strip(),
                "password": self.credentials["password"].strip(),
                "account": account,
            }
            
            # Add optional parameters
            if self.credentials.get("warehouse"):
                conn_params["warehouse"] = self.credentials["warehouse"].strip()
            if self.credentials.get("database"):
                conn_params["database"] = self.credentials["database"].strip()
            if self.credentials.get("schema"):
                conn_params["schema"] = self.credentials["schema"].strip()
            if self.credentials.get("role"):
                conn_params["role"] = self.credentials["role"].strip()
            
            print(f"\nSnowflake Connection Parameters:")
            print(f"  Account: {conn_params['account']}")
            print(f"  User: {conn_params['user']}")
            print(f"  Warehouse: {conn_params.get('warehouse', 'Not specified')}")
            print(f"  Database: {conn_params.get('database', 'Not specified')}")
            print(f"  Schema: {conn_params.get('schema', 'Not specified')}")
            
            print(f"\nAttempting Snowflake connection...")
            self.connection = snowflake.connector.connect(
                **conn_params,
                connect_timeout=10,
                client_session_keep_alive=False
            )
            print("✓ Snowflake connection successful!")
            
        except ImportError:
            raise ImportError(
                "snowflake-connector-python not installed.\n"
                "Install with: pip install snowflake-connector-python"
            )
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Snowflake Connection Error:")
            print(f"  {error_msg}")
            
            # Provide helpful hints
            if "Could not connect" in error_msg or "250001" in error_msg:
                print("\nTroubleshooting tips:")
                print("  1. Verify account ID format (should be like: xy12345, not full URL)")
                print("  2. Check username and password are correct")
                print("  3. Ensure Snowflake account is active")
                print("  4. Check network connectivity to Snowflake")
                print("  5. Verify warehouse exists and is running")
            
            raise RuntimeError(f"Snowflake connection failed: {error_msg}")
    
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
            elif self.db_type == "snowflake":
                self._execute_snowflake_query(query)
            else:
                cursor = self.connection.cursor()
                cursor.execute(query)
                self.connection.commit()
                cursor.close()
            return True
        except Exception as e:
            print(f"Query execution failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _execute_snowflake_query(self, query: str):
        """Execute query on Snowflake"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            cursor.close()
            print(f"Query executed successfully on Snowflake")
        except Exception as e:
            print(f"Snowflake query execution error: {str(e)}")
            raise
    
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
