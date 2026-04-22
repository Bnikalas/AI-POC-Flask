from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from typing import Dict, List
from config import Config
from services.file_processor import FileProcessor
from services.llm_service import LLMService
from services.db_connector import DatabaseConnector

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = Config.MAX_FILE_SIZE
app.config["UPLOAD_FOLDER"] = Config.UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Initialize LLM service (will be created per request)
llm_service = None

@app.route("/", methods=["GET"])
def serve_frontend():
    """Serve frontend"""
    return send_from_directory("../frontend", "index.html")

@app.route("/<path:path>", methods=["GET"])
def serve_static(path):
    """Serve static files"""
    return send_from_directory("../frontend", path)

@app.route("/api/config", methods=["GET"])
def get_config():
    """Get configuration including default LLM model"""
    return jsonify({
        "default_model": Config.DEFAULT_LLM_MODEL,
        "supported_databases": Config.SUPPORTED_DATABASES,
        "max_file_size": Config.MAX_FILE_SIZE
    })

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "langchain_enabled": True})

@app.route("/api/databases", methods=["GET"])
def get_databases():
    """Get list of supported databases"""
    return jsonify({"databases": Config.SUPPORTED_DATABASES})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Upload and analyze data file"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed: {Config.ALLOWED_EXTENSIONS}"}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        
        # Ensure upload folder exists
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        
        file.save(filepath)
        
        # Verify file was saved
        if not os.path.exists(filepath):
            return jsonify({"error": "File save failed"}), 500
        
        # Analyze file using FileProcessor
        data = FileProcessor.read_file(filepath)
        analysis = FileProcessor.analyze_data_structure(data)
        
        # Detect PII columns using AI if API key provided
        openrouter_key = request.form.get("openrouter_key")
        model = request.form.get("model")
        
        if openrouter_key and model:
            from services.pii_detector import PIIDetector
            
            try:
                # Initialize LLM service with provided credentials
                llm_service = LLMService(
                    api_key=openrouter_key,
                    model=model
                )
                
                pii_detector = PIIDetector(llm_service.llm)
                pii_columns = pii_detector.detect_pii_columns(analysis["columns"], data[:5].to_dict('records'))
                
                # Mark PII columns
                for col in analysis["columns"]:
                    col["is_pii"] = col["name"] in pii_columns
                    
                print(f"PII detection completed. Found {len(pii_columns)} PII columns: {pii_columns}")
            except Exception as e:
                print(f"PII detection error: {str(e)}")
                # Continue without PII detection
                for col in analysis["columns"]:
                    col["is_pii"] = False
        else:
            # No API key provided, skip PII detection
            for col in analysis["columns"]:
                col["is_pii"] = False
        
        return jsonify({
            "success": True,
            "filename": filename,
            "analysis": analysis
        })
    except Exception as e:
        import traceback
        print(f"Upload error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route("/api/design-schema", methods=["POST"])
def design_schema():
    """Design database schema using LLM with LangChain from multiple files"""
    data = request.json
    
    # Support both single file (file_analysis) and multiple files (file_analyses)
    file_analyses = data.get("file_analyses") or {}
    single_file_analysis = data.get("file_analysis")
    
    if not file_analyses and not single_file_analysis:
        return jsonify({"error": "File analysis required"}), 400
    
    # Convert single file to multiple files format for consistency
    if single_file_analysis and not file_analyses:
        file_analyses = {"file": single_file_analysis}
    
    try:
        # Get database type and schema from request
        database_type = data.get("db_type", "snowflake")
        schema_name = data.get("schema_name", "PUBLIC")
        
        # Initialize LLM service with provided credentials
        llm_service = LLMService(
            api_key=data.get("openrouter_key"),
            model=data.get("model")
        )
        
        # Design schema using LangChain with database-specific parameters
        # Pass all file analyses to the LLM
        result = llm_service.design_schema(
            file_analyses,
            database_type=database_type,
            schema_name=schema_name,
            multiple_files=True
        )
        
        if not result["success"]:
            return jsonify({"error": result.get("error", "Schema design failed")}), 500
        
        return jsonify({
            "success": True,
            "schema": result["schema"],
            "cost": result.get("cost", 0),
            "total_cost": result.get("total_cost", 0)
        })
    except Exception as e:
        import traceback
        print(f"Design schema error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route("/api/deploy-schema", methods=["POST"])
def deploy_schema():
    """Deploy schema to selected database"""
    data = request.json
    
    required_fields = ["db_type", "credentials", "schema"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        db_type = data["db_type"]
        credentials = data["credentials"]
        schema = data["schema"]
        
        print(f"\n=== Deployment Started ===")
        print(f"Database Type: {db_type}")
        
        # Validate credentials
        if not credentials:
            return jsonify({"error": "No credentials provided"}), 400
        
        connector = DatabaseConnector(db_type, credentials)
        
        print(f"Attempting to connect to {db_type}...")
        if not connector.connect():
            error_msg = f"Failed to connect to {db_type} database. Check your credentials."
            print(f"Connection Error: {error_msg}")
            return jsonify({"error": error_msg}), 500
        
        print(f"Connected successfully to {db_type}")
        
        # Generate DDL statements from schema
        ddl_statements = generate_ddl_from_schema(schema, db_type)
        print(f"Generated {len(ddl_statements)} DDL statements")
        
        # Execute DDL statements and track logs
        execution_logs = []
        failed_statements = []
        
        for i, statement in enumerate(ddl_statements, 1):
            log_entry = {
                "statement_number": i,
                "total_statements": len(ddl_statements),
                "sql": statement,
                "status": "pending",
                "error": None
            }
            
            print(f"\nExecuting statement {i}/{len(ddl_statements)}:")
            print(f"  {statement[:100]}...")
            
            try:
                if connector.execute_query(statement):
                    log_entry["status"] = "success"
                    print(f"  ✓ Success")
                else:
                    log_entry["status"] = "failed"
                    log_entry["error"] = "Query execution returned false"
                    failed_statements.append(statement)
                    print(f"  ❌ Failed: {log_entry['error']}")
            except Exception as e:
                log_entry["status"] = "failed"
                log_entry["error"] = str(e)
                failed_statements.append(statement)
                print(f"  ❌ Failed: {str(e)}")
            
            execution_logs.append(log_entry)
        
        connector.close()
        
        if failed_statements:
            error_msg = f"Deployed with errors. {len(failed_statements)} statements failed."
            print(f"\n{error_msg}")
            return jsonify({
                "success": False,
                "message": error_msg,
                "failed_count": len(failed_statements),
                "failed_statements": failed_statements,
                "execution_logs": execution_logs
            }), 200  # Return 200 so frontend can display logs
        
        success_msg = f"Schema deployed successfully! {len(ddl_statements)} tables created."
        print(f"\n✓ {success_msg}")
        return jsonify({
            "success": True,
            "message": success_msg,
            "statements_executed": len(ddl_statements),
            "execution_logs": execution_logs
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n❌ Deployment Error: {str(e)}")
        print(error_trace)
        return jsonify({
            "error": f"Deployment failed: {str(e)}",
            "details": error_trace
        }), 500

@app.route("/api/fix-sql", methods=["POST"])
def fix_sql():
    """Fix SQL errors using LLM"""
    data = request.json
    
    required_fields = ["error_message", "failed_sql", "db_type"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        from chains.sql_correction_chain import SQLCorrectionChain
        
        # Initialize LLM service with provided credentials
        llm_service = LLMService(
            api_key=data.get("openrouter_key"),
            model=data.get("model")
        )
        
        # Create SQL correction chain
        correction_chain = SQLCorrectionChain(llm_service.llm)
        
        # Correct the SQL
        result = correction_chain.correct_sql(
            failed_sql=data["failed_sql"],
            error_message=data["error_message"],
            db_type=data["db_type"]
        )
        
        if not result["success"]:
            return jsonify({"error": result.get("error", "SQL correction failed")}), 500
        
        return jsonify({
            "success": True,
            "corrected_sql": result["corrected_sql"],
            "original_sql": result["original_sql"],
            "error_message": result["error_message"]
        })
    
    except Exception as e:
        import traceback
        print(f"SQL correction error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def generate_ddl_from_schema(schema: Dict, db_type: str) -> List[str]:
    """Generate DDL statements from schema design"""
    ddl_statements = []
    
    # If schema already has SQL statements, use them
    if schema.get("sql_statements") and len(schema["sql_statements"]) > 0:
        return schema["sql_statements"]
    
    # Otherwise generate from tables
    if "tables" in schema:
        for table in schema["tables"]:
            ddl = generate_create_table_sql(table, db_type)
            if ddl:
                ddl_statements.append(ddl)
    
    return ddl_statements

def generate_create_table_sql(table: Dict, db_type: str) -> str:
    """Generate CREATE TABLE SQL for a table"""
    table_name = table.get("name", "table")
    columns = table.get("columns", [])
    
    if not columns:
        return None
    
    col_defs = []
    for col in columns:
        col_name = col.get("name", "column")
        col_type = col.get("data_type", "VARCHAR(255)")
        nullable = col.get("nullable", True)
        primary_key = col.get("primary_key", False)
        
        col_def = f"{col_name} {col_type}"
        
        if primary_key:
            col_def += " PRIMARY KEY"
        elif not nullable:
            col_def += " NOT NULL"
        
        col_defs.append(col_def)
    
    sql = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
    return sql

def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True, port=5000)
