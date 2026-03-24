# Automated Database Creator from Input Data Files

An AI-powered application that automatically designs and deploys database schemas based on input data files (CSV/Parquet) to various database systems.

## Features

- **Multi-format Support**: CSV and Parquet file processing
- **AI-Powered Schema Design**: Uses OpenRouter LLM to intelligently design optimal database schemas
- **Multi-Database Support**: Amazon Athena, Snowflake, SQL Server, PostgreSQL, MySQL
- **Secure Credential Management**: Safe handling of database credentials
- **Automated DDL Generation**: Generates SQL scripts for table creation
- **Schema Analysis**: Detects primary/foreign keys and relationships
- **Selenium-based UI**: Automated testing and user interface

## Project Structure

```
automated-db-creator/
├── backend/          # Flask API server
├── frontend/         # Selenium UI automation
├── tests/           # Test suite
└── README.md
```

## Setup

### Prerequisites
- Python 3.8+
- OpenRouter API key
- Database credentials for target system

### Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenRouter API key
   ```

## Usage

### Start Backend Server
```bash
cd backend
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/databases` - List supported databases
- `POST /api/upload` - Upload and analyze data file
- `POST /api/design-schema` - Design schema using LLM
- `POST /api/deploy-schema` - Deploy schema to database

### Example Workflow

1. Upload CSV/Parquet file
2. Select target database system
3. Enter database credentials
4. Provide OpenRouter API key and model
5. Review AI-generated schema
6. Deploy to database

## Configuration

Edit `backend/config.py` to customize:
- Supported databases
- File upload limits
- LLM model settings
- Temperature and token limits

## Testing

```bash
pytest tests/
```

## Database-Specific Setup

### Amazon Athena
- Requires AWS Access Key and Secret Key
- S3 bucket for query results

### Snowflake
- Account identifier
- Username and password
- Warehouse and database names

### SQL Server
- Server hostname
- Database name
- Username and password

## Security Notes

- Never commit `.env` file with real credentials
- Use environment variables for sensitive data
- Credentials are not stored permanently
- All connections use secure protocols

## Next Steps

1. Build React/Vue frontend UI
2. Add database schema visualization
3. Implement entity relationship diagrams
4. Add data validation and transformation
5. Create deployment logs and history
6. Add rollback functionality

## License

MIT
