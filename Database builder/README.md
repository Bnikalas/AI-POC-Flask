# Automated Database Creator

An AI-powered application that automatically designs and deploys database schemas from CSV/Parquet files to various database systems using LangChain and OpenRouter LLM.

## 🎯 Features

### Core Features
- **Multi-format Support** - CSV and Parquet file processing
- **AI-Powered Schema Design** - Uses LangChain + OpenRouter LLM for intelligent schema design
- **PII Detection** - Automatically detects and flags sensitive data columns
- **Multi-Database Support** - Athena, Snowflake, SQL Server, PostgreSQL, MySQL
- **SQL Error Correction** - AI-powered SQL error fixing and redeployment
- **Execution Logs** - Detailed logs for each SQL statement execution
- **Database-Specific SQL** - Generates syntax optimized for target database

### Advanced Features
- **Schema Normalization** - Suggests normalized table structures
- **Data Type Inference** - Automatically detects optimal data types
- **Relationship Detection** - Identifies primary/foreign key relationships
- **Error Recovery** - Fix and redeploy failed SQL statements
- **Real-time Feedback** - See deployment progress and errors

## 📁 Project Structure

```
automated-db-creator/
├── backend/
│   ├── chains/              # LangChain chains
│   │   ├── schema_designer_chain.py
│   │   └── sql_correction_chain.py
│   ├── models/              # Pydantic models
│   │   └── schema_models.py
│   ├── services/            # Business logic
│   │   ├── db_connector.py
│   │   ├── file_processor.py
│   │   ├── llm_service.py
│   │   └── pii_detector.py
│   ├── uploads/             # Uploaded files
│   ├── app.py              # Flask API
│   ├── config.py           # Configuration
│   └── requirements.txt    # Dependencies
├── frontend/
│   ├── index.html          # Main UI
│   ├── app.js              # Frontend logic
│   └── styles.css          # Styling
├── .env.example            # Environment template
├── README.md               # This file
├── START_HERE.md           # Getting started guide
├── QUICK_REFERENCE.md      # Quick reference
├── TECHSTACK.md            # Technology stack
└── SQL_ERROR_CORRECTION_USAGE.md  # Error correction guide
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10.11 or higher
- OpenRouter API key ([Get one here](https://openrouter.ai/))
- Database credentials for your target system

### Installation

1. **Clone and setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -U langchain-openrouter
   ```

3. **Start the application**
   ```bash
   python app.py
   ```

4. **Open browser**
   ```
   http://localhost:5000
   ```

## 📖 Usage

### 6-Step Workflow

1. **Upload Data File** - Drag & drop CSV or Parquet file
2. **Select Database** - Choose target database system
3. **Enter Credentials** - Provide database connection details
4. **Configure LLM** - Enter OpenRouter API key and model
5. **Design Schema** - AI generates optimized schema
6. **Deploy** - Execute SQL statements on database

### SQL Error Correction

If deployment fails:
1. View execution logs in Step 7
2. Copy error message and failed SQL
3. Paste into error correction dialog (Step 8)
4. Get AI-corrected SQL
5. Redeploy corrected statement

See [SQL_ERROR_CORRECTION_USAGE.md](SQL_ERROR_CORRECTION_USAGE.md) for details.

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/config` | GET | Get configuration |
| `/api/databases` | GET | List supported databases |
| `/api/upload` | POST | Upload and analyze file |
| `/api/design-schema` | POST | Design schema with AI |
| `/api/deploy-schema` | POST | Deploy schema to database |
| `/api/fix-sql` | POST | Fix SQL errors with AI |

## 🗄️ Supported Databases

### Amazon Athena
- AWS Access Key & Secret Key
- S3 output location
- Database name

### Snowflake
- Account identifier (e.g., `xy12345`)
- Username & password
- Warehouse, database, schema

### PostgreSQL
- Host & port (default: 5432)
- Database name
- Username & password
- Schema (optional)

### MySQL
- Host & port (default: 3306)
- Database name
- Username & password

### SQL Server
- Server hostname
- Database name
- Username & password

## ⚙️ Configuration

Edit `backend/config.py`:

```python
# LLM Configuration
DEFAULT_LLM_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
LLM_TEMPERATURE = 0.7
MAX_TOKENS = 4000

# File Upload
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {"csv", "parquet"}

# Supported Databases
SUPPORTED_DATABASES = {
    "athena": "Amazon Athena",
    "snowflake": "Snowflake",
    "sqlserver": "SQL Server",
    "postgres": "PostgreSQL",
    "mysql": "MySQL"
}
```

## 🔒 Security

- Never commit `.env` with real credentials
- API keys passed in request body (use HTTPS in production)
- Database credentials not stored permanently
- PII data flagged but not logged
- SQL injection prevention via parameterized queries

## 🛠️ Technology Stack

See [TECHSTACK.md](TECHSTACK.md) for complete details:

- **Backend**: Flask, LangChain, Pydantic
- **LLM**: OpenRouter API
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Databases**: Multiple connectors (boto3, snowflake-connector-python, etc.)

## 📚 Documentation

- **[START_HERE.md](START_HERE.md)** - Comprehensive getting started guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference for common tasks
- **[TECHSTACK.md](TECHSTACK.md)** - Technology stack details
- **[SQL_ERROR_CORRECTION_USAGE.md](SQL_ERROR_CORRECTION_USAGE.md)** - Error correction guide

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure langchain-openrouter is installed
pip install -U langchain-openrouter
```

### Connection Errors
- Verify database credentials
- Check network connectivity
- Ensure database is running
- For Snowflake: Use account ID only (e.g., `xy12345`)

### LLM Errors
- Verify OpenRouter API key
- Check API quota/limits
- Try different model if current one fails

### File Upload Errors
- Check file size (max 16MB)
- Ensure file is CSV or Parquet format
- Verify file is not corrupted

## 🔄 Development Workflow

1. **Make changes** to backend or frontend
2. **Restart Flask** server if backend changed
3. **Refresh browser** if frontend changed
4. **Test** with sample CSV file
5. **Check logs** for errors

## 🎯 Next Steps

- [ ] Add data validation and transformation
- [ ] Implement schema versioning
- [ ] Add rollback functionality
- [ ] Create data migration tools
- [ ] Add batch processing
- [ ] Implement caching for LLM responses
- [ ] Add user authentication
- [ ] Create deployment history

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions:
1. Check documentation files
2. Review error messages
3. Check database-specific setup
4. Verify API keys and credentials

---

**Version:** 1.0.0  
**Last Updated:** March 2026  
**Status:** Production Ready
