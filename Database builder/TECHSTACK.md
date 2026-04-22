# Automated Database Creator - Technology Stack

## Overview
A full-stack web application that uses AI to automatically design and deploy database schemas from data files.

---

## Frontend Technology Stack

### Core Technologies
- **HTML5** - Markup and structure
- **CSS3** - Styling and responsive design
- **JavaScript (ES6+)** - Client-side logic and interactivity

### Frontend Features
- **Drag & Drop File Upload** - Native HTML5 File API
- **Responsive Design** - Mobile-first CSS Grid/Flexbox
- **Real-time UI Updates** - DOM manipulation
- **API Communication** - Fetch API for HTTP requests
- **Loading States** - Spinner animations and toast notifications
- **Form Handling** - Dynamic form generation based on database selection

### Frontend Architecture
```
frontend/
├── index.html          # Single-page application structure
├── styles.css          # All styling (no CSS framework)
├── app.js              # Client-side logic
└── selenium_ui.py      # Automated testing (optional)
```

### Frontend Workflow
1. User uploads CSV/Parquet file
2. JavaScript sends file to backend via FormData
3. Backend analyzes and returns structure
4. Frontend displays analysis results
5. User selects database and enters credentials
6. Frontend sends schema design request
7. Backend returns AI-generated schema
8. Frontend displays schema preview
9. User deploys schema to database

---

## Backend Technology Stack

### Core Framework
- **Flask 2.3.3** - Lightweight Python web framework
- **Python 3.10.11** - Programming language

### Key Libraries

#### LLM & AI Integration
- **LangChain 0.2.0** - LLM orchestration framework
- **langchain-core 0.2.0** - Core LangChain utilities
- **langchain-openrouter 0.1.0** - OpenRouter integration
- **Pydantic 2.4.2** - Data validation and serialization

#### Data Processing
- **CSV Processing** - Built-in Python `csv` module
- **JSON Handling** - Built-in Python `json` module

#### Database Connectivity
- **boto3** - AWS services (Athena)
- **snowflake-connector-python** - Snowflake connection
- **pyodbc** - SQL Server connection
- **SQLAlchemy** - PostgreSQL/MySQL ORM

#### Web & API
- **Flask-CORS 4.0.0** - Cross-Origin Resource Sharing
- **Werkzeug** - WSGI utilities (file handling)
- **requests 2.31.0** - HTTP library

#### Utilities
- **python-dotenv 1.0.0** - Environment variable management
- **typing-extensions 4.8.0** - Type hints support

### Backend Architecture
```
backend/
├── app.py                          # Flask application & API routes
├── config.py                       # Configuration management
├── requirements.txt                # Dependencies
├── services/
│   ├── file_processor.py          # CSV/Parquet file handling
│   ├── llm_service.py             # LangChain LLM integration
│   └── db_connector.py            # Multi-database connections
├── models/
│   ├── schema_models.py           # Pydantic data models
│   └── __init__.py
└── chains/
    ├── schema_designer_chain.py   # LangChain chain for schema design
    └── __init__.py
```

### Backend API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Serve frontend |
| GET | `/api/health` | Health check |
| GET | `/api/config` | Get configuration |
| GET | `/api/databases` | List supported databases |
| POST | `/api/upload` | Upload and analyze file |
| POST | `/api/design-schema` | Design schema with AI |
| POST | `/api/deploy-schema` | Deploy schema to database |

---

## External Services & APIs

### LLM Provider
- **OpenRouter** - LLM API provider
  - Supports multiple models (Claude, Llama, Nemotron, etc.)
  - Free tier available
  - API: `https://openrouter.ai/api/v1`

### Supported Databases
1. **Amazon Athena** - AWS data warehouse
2. **Snowflake** - Cloud data platform
3. **SQL Server** - Microsoft database
4. **PostgreSQL** - Open-source relational DB
5. **MySQL** - Open-source relational DB

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend (HTML/CSS/JavaScript)                      │   │
│  │  - File upload                                       │   │
│  │  - Database selection                               │   │
│  │  - Credential entry                                 │   │
│  │  - Schema preview                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Routes (app.py)                                 │   │
│  │  - /api/upload                                       │   │
│  │  - /api/design-schema                               │   │
│  │  - /api/deploy-schema                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Services Layer                                      │   │
│  │  ├─ FileProcessor (CSV/Parquet analysis)            │   │
│  │  ├─ LLMService (LangChain + OpenRouter)             │   │
│  │  └─ DatabaseConnector (Multi-DB support)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Data Models (Pydantic)                              │   │
│  │  ├─ DataAnalysis                                     │   │
│  │  ├─ SchemaDesign                                     │   │
│  │  ├─ Table, Column, Relationship                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LangChain Chain                                     │   │
│  │  ├─ PromptTemplate (structured prompts)             │   │
│  │  ├─ ChatOpenRouter (LLM)                            │   │
│  │  └─ PydanticOutputParser (validation)               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ API Calls
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  ├─ OpenRouter API (LLM inference)                         │
│  ├─ AWS Athena (database deployment)                       │
│  ├─ Snowflake (database deployment)                        │
│  ├─ SQL Server (database deployment)                       │
│  ├─ PostgreSQL (database deployment)                       │
│  └─ MySQL (database deployment)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Decisions & Rationale

### Why Flask?
- Lightweight and flexible
- Easy to set up and deploy
- Perfect for REST APIs
- Good ecosystem for extensions

### Why LangChain?
- Unified interface for multiple LLMs
- Built-in prompt management
- Output parsing and validation
- Error handling and retries

### Why Pydantic?
- Type-safe data validation
- Automatic JSON serialization
- IDE autocomplete support
- Clear error messages

### Why OpenRouter?
- Access to multiple LLM models
- Free tier available
- Simple API
- No vendor lock-in

### Why Vanilla JavaScript?
- No build process needed
- Lightweight and fast
- Easy to understand and maintain
- Perfect for simple UI interactions

---

## Development Environment

### System Requirements
- **Python**: 3.10.11+
- **Node.js**: Not required (vanilla JavaScript)
- **OS**: Windows, macOS, Linux

### Development Tools
- **Code Editor**: VS Code, PyCharm, etc.
- **Version Control**: Git
- **Package Manager**: pip (Python)
- **Virtual Environment**: venv

### Running Locally
```bash
# Backend
cd backend
python app.py

# Frontend
# Automatically served by Flask at http://localhost:5000
```

---

## Deployment Architecture

### Backend Deployment Options
1. **Heroku** - Easy deployment with git push
2. **AWS EC2** - Full control and scalability
3. **Google Cloud Run** - Serverless option
4. **DigitalOcean** - Simple and affordable
5. **Docker** - Containerized deployment

### Frontend Deployment Options
1. **Same server as backend** - Current setup
2. **CDN** - For static files
3. **Netlify/Vercel** - Static hosting
4. **AWS S3 + CloudFront** - Scalable static hosting

### Database Deployment
- Deployed to user's selected database system
- No database required for the application itself
- All data is temporary (uploaded files, analysis results)

---

## Security Considerations

### Frontend Security
- CORS enabled for API communication
- No sensitive data stored in browser
- Input validation on file upload
- Secure file type checking

### Backend Security
- Environment variables for API keys
- Secure file upload handling
- Input validation with Pydantic
- Error handling without exposing internals
- HTTPS recommended for production

### Data Security
- Credentials not stored permanently
- Files deleted after processing
- API keys passed securely
- No logging of sensitive data

---

## Performance Characteristics

### Frontend
- **Load Time**: < 2 seconds
- **File Upload**: Supports up to 100MB
- **UI Responsiveness**: Instant (no heavy computation)

### Backend
- **File Analysis**: < 5 seconds for typical files
- **Schema Design**: 10-30 seconds (depends on LLM)
- **Database Deployment**: 5-60 seconds (depends on DB)

### Scalability
- **Concurrent Users**: Limited by server resources
- **File Size**: Up to 100MB (configurable)
- **Database Support**: 5 different systems
- **LLM Models**: Any model available on OpenRouter

---

## Dependencies Summary

### Python Packages (11 total)
```
Flask==2.3.3
flask-cors==4.0.0
python-dotenv==1.0.0
requests==2.31.0
langchain==0.2.0
langchain-core==0.2.0
langchain-openrouter==0.1.0
pydantic==2.4.2
typing-extensions==4.8.0
boto3 (optional)
snowflake-connector-python (optional)
pyodbc (optional)
sqlalchemy (optional)
```

### Frontend Dependencies
- None (vanilla HTML/CSS/JavaScript)

---

## Version History

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.10.11 | Runtime |
| Flask | 2.3.3 | Web framework |
| LangChain | 0.2.0 | LLM orchestration |
| Pydantic | 2.4.2 | Data validation |
| OpenRouter | Latest | LLM provider |

---

## Future Technology Considerations

### Phase 2 (LangGraph)
- **LangGraph 0.0.44** - Workflow orchestration
- State machine for complex workflows
- Better error handling and retries

### Phase 3 (Agents)
- **LangChain Agents** - Autonomous decision making
- Tool calling and validation
- Multi-step reasoning

### Phase 4 (Advanced)
- **Redis** - Caching layer
- **PostgreSQL** - Application database
- **Docker** - Containerization
- **Kubernetes** - Orchestration

---

## Summary

**Frontend**: HTML5 + CSS3 + Vanilla JavaScript (no frameworks)
**Backend**: Flask + Python 3.10 + LangChain + Pydantic
**LLM**: OpenRouter (multiple models)
**Databases**: 5 supported systems (Athena, Snowflake, SQL Server, PostgreSQL, MySQL)
**Architecture**: REST API with single-page frontend
**Deployment**: Flexible (Heroku, AWS, Docker, etc.)

This is a modern, scalable, and maintainable tech stack suitable for production use.
