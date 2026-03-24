from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
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
    """Design database schema using LLM with LangChain"""
    data = request.json
    
    if not data.get("file_analysis"):
        return jsonify({"error": "File analysis required"}), 400
    
    try:
        # Initialize LLM service with provided credentials
        llm_service = LLMService(
            api_key=data.get("openrouter_key"),
            model=data.get("model")
        )
        
        # Design schema using LangChain
        result = llm_service.design_schema(data["file_analysis"])
        
        if not result["success"]:
            return jsonify({"error": result.get("error", "Schema design failed")}), 500
        
        return jsonify({
            "success": True,
            "schema": result["schema"],
            "cost": result.get("cost", 0),
            "total_cost": result.get("total_cost", 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/deploy-schema", methods=["POST"])
def deploy_schema():
    """Deploy schema to selected database"""
    data = request.json
    
    required_fields = ["db_type", "credentials", "schema", "ddl_statements"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        connector = DatabaseConnector(data["db_type"], data["credentials"])
        
        if not connector.connect():
            return jsonify({"error": "Failed to connect to database"}), 500
        
        # Execute DDL statements
        for statement in data["ddl_statements"]:
            if not connector.execute_query(statement):
                connector.close()
                return jsonify({"error": f"Failed to execute: {statement}"}), 500
        
        connector.close()
        return jsonify({"success": True, "message": "Schema deployed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True, port=5000)
