# Project Code Structure Guide

## Overview
This is a full-stack application with a Python Flask backend and HTML/CSS/JavaScript frontend. The app automates database schema creation from data files using AI.

---

## Backend Files (Python)

### `backend/app.py` - Main Application Entry Point
**Purpose:** Core Flask application that runs the server and handles all API routes.

**Key Components:**
- Initializes Flask app with CORS support
- Serves frontend files (HTML, CSS, JS)
- Defines all API endpoints
- Handles file uploads and processing

**Main Routes:**
- `GET /` - Serves the frontend (index.html)
- `GET /api/health` - Health check
- `GET /api/databases` - Returns list of supported databases
- `POST /api/upload` - Receives file upload, analyzes it
- `POST /api/design-schema` - Calls LLM to design schema
- `POST /api/deploy-schema` - Deploys schema to database

**When to modify:**
- Add new API endpoints
- Change upload folder location
- Modify CORS settings
- Add new routes for features

---

### `backend/config.py` - Configuration Settings
**Purpose:** Centralized configuration for the entire application.

**Contains:**
- OpenRouter API settings (base URL, model defaults)
- Supported database list
- File upload limits (max size, allowed extensions)
- LLM parameters (temperature, max tokens)

**Key Variables:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key (from .env)
- `SUPPORTED_DATABASES` - Dict of available databases
- `MAX_FILE_SIZE` - Maximum upload file size (100MB)
- `ALLOWED_EXTENSIONS` - File types allowed (.csv, .parquet)
- `DEFAULT_LLM_MODEL` - Default AI model to use

**When to modify:**
- Add new database support
- Change file size limits
- Update LLM model defaults
- Adjust AI temperature/token settings

---

### `backend/services/file_processor.py` - Data File Handling
**Purpose:** Reads and analyzes uploaded CSV/Parquet files.

**Main Functions:**
1. `read_file(file_path)` - Opens CSV or Parquet file and returns data
2. `analyze_data_structure(data)` - Examines file structure:
   - Counts rows and columns
   - Identifies data types
   - Detects null values
   - Finds unique values
3. `detect_potential_keys(data)` - Finds:
   - Primary key candidates (columns with unique values)
   - Foreign key candidates (columns ending with _id)

**Data Flow:**
```
User uploads file → read_file() → analyze_data_structure() → detect_potential_keys() → Return analysis
```

**When to modify:**
- Add Parquet support (requires pandas)
- Change key detection logic
- Add data validation
- Support new file formats (JSON, Excel, etc.)

---

### `backend/services/llm_service.py` - AI Integration
**Purpose:** Communicates with OpenRouter API to design database schemas using AI.

**Main Functions:**
1. `__init__(api_key, model)` - Initialize with API credentials
2. `design_schema(data_analysis)` - Sends data analysis to LLM and gets schema design
3. `_build_schema_design_prompt(data_analysis)` - Creates the prompt for LLM
4. `_call_openrouter(prompt)` - Makes HTTP request to OpenRouter API
5. `_parse_schema_response(response)` - Extracts JSON from LLM response

**How It Works:**
```
File Analysis → Build Prompt → Call OpenRouter API → Parse Response → Return Schema
```

**LLM Prompt Includes:**
- Row and column counts
- Column details (names, types, unique values)
- Request for schema type, tables, relationships, normalization

**When to modify:**
- Change the prompt to get different schema designs
- Switch to different LLM model
- Adjust temperature/token limits
- Add more context to the prompt

---

### `backend/services/db_connector.py` - Database Connections
**Purpose:** Handles connections to different database systems.

**Supported Databases:**
- Amazon Athena (AWS)
- Snowflake
- SQL Server
- PostgreSQL
- MySQL

**Main Functions:**
1. `connect()` - Establishes connection based on db_type
2. `execute_query(query)` - Runs SQL queries
3. `close()` - Closes connection

**Connection Methods:**
- `_connect_athena()` - Uses boto3 (AWS SDK)
- `_connect_snowflake()` - Uses snowflake-connector
- `_connect_sqlserver()` - Uses pyodbc
- `_connect_postgres()` - Uses SQLAlchemy
- `_connect_mysql()` - Uses SQLAlchemy

**When to modify:**
- Add new database support
- Change connection parameters
- Add connection pooling
- Add retry logic

---

### `backend/requirements.txt` - Python Dependencies
**Purpose:** Lists all Python packages needed to run the app.

**Current Packages:**
- `Flask` - Web framework
- `flask-cors` - Cross-origin requests
- `python-dotenv` - Load environment variables
- `requests` - HTTP requests to OpenRouter

**Optional Packages** (install only if needed):
- `boto3` - For AWS Athena
- `snowflake-connector-python` - For Snowflake
- `pyodbc` - For SQL Server
- `sqlalchemy` - For PostgreSQL/MySQL

**When to modify:**
- Add new Python packages
- Update package versions
- Remove unused dependencies

---

## Frontend Files (HTML/CSS/JavaScript)

### `frontend/index.html` - Main Web Page
**Purpose:** The HTML structure of the user interface.

**Contains 6 Main Sections (Steps):**
1. **Step 1: Upload Data File**
   - Drag-and-drop area for CSV/Parquet files
   - File analysis results display

2. **Step 2: Select Database System**
   - Grid of database options (Athena, Snowflake, etc.)
   - Visual selection with icons

3. **Step 3: Database Credentials**
   - Dynamic form fields based on selected database
   - Input fields for username, password, host, etc.

4. **Step 4: LLM Configuration**
   - OpenRouter API key input
   - LLM model selection

5. **Step 5: Schema Preview**
   - "Design Schema with AI" button
   - Display of generated schema in JSON format

6. **Step 6: Deploy to Database**
   - "Deploy Schema" button
   - Deployment status display

**Key Elements:**
- `id="file-upload"` - File input element
- `id="database-grid"` - Database selection grid
- `id="credentials-form"` - Dynamic credentials form
- `id="schema-preview"` - Schema display area
- `id="deployment-status"` - Deployment results

**When to modify:**
- Add new steps/sections
- Change form fields
- Add new database options
- Modify layout structure

---

### `frontend/styles.css` - Styling & Layout
**Purpose:** All visual styling and responsive design.

**Main Sections:**
1. **CSS Variables** (`:root`)
   - Color scheme (primary, success, danger, grays)
   - Easy to change theme colors

2. **Layout Classes**
   - `.container` - Max width wrapper
   - `.step` - Each workflow step
   - `.step-header` - Step title and number
   - `.step-content` - Step content area

3. **Component Styles**
   - `.upload-area` - File upload zone
   - `.database-grid` - Database selection grid
   - `.form-group` - Form input styling
   - `.btn` - Button styles (primary, secondary, success)

4. **Interactive States**
   - `:hover` - Hover effects
   - `.dragover` - Drag-over state
   - `.selected` - Selected state
   - `:focus` - Focus state

5. **Utilities**
   - `.hidden` - Hide elements
   - `.loading` - Loading spinner
   - `.toast` - Notification messages

6. **Animations**
   - `@keyframes spin` - Loading spinner rotation
   - `@keyframes slideIn` - Toast notification slide-in

7. **Responsive Design**
   - `@media (max-width: 768px)` - Mobile adjustments

**When to modify:**
- Change colors (update `:root` variables)
- Adjust spacing/padding
- Modify button styles
- Add new animations
- Change responsive breakpoints

---

### `frontend/app.js` - Frontend Logic & API Calls
**Purpose:** Handles all user interactions and communicates with backend API.

**Key Variables:**
- `API_BASE = "http://localhost:5000/api"` - Backend URL
- `currentState` - Stores user data (file, analysis, credentials, schema)

**Main Functions:**

1. **File Upload**
   - `setupFileUpload()` - Setup drag-drop and file input
   - `handleFileUpload(file)` - Process uploaded file
   - `displayFileAnalysis(data)` - Show analysis results

2. **Database Selection**
   - `loadDatabases()` - Fetch and display database options
   - `selectDatabase(dbType, element)` - Handle database selection
   - `showCredentialsForm(dbType)` - Show relevant credential fields

3. **Schema Design**
   - `designSchema()` - Call LLM to design schema
   - `displaySchema(schema)` - Show generated schema

4. **Deployment**
   - `deploySchema()` - Deploy schema to database
   - `generateDDL(schema)` - Create SQL statements
   - `displayDeploymentStatus(message)` - Show deployment result

5. **Utilities**
   - `showLoading(show)` - Show/hide loading spinner
   - `showToast(message, type)` - Show notification messages

**API Calls Made:**
```javascript
GET  /api/databases              // Get list of databases
POST /api/upload                 // Upload file
POST /api/design-schema          // Design schema with AI
POST /api/deploy-schema          // Deploy to database
```

**When to modify:**
- Add new workflow steps
- Change API endpoints
- Add form validation
- Modify error handling
- Add new database credential fields

---

### `frontend/selenium_ui.py` - Automated Testing
**Purpose:** Selenium script for automated UI testing (optional).

**Main Class:** `DatabaseCreatorUI`

**Methods:**
- `start()` - Open browser and navigate to app
- `upload_file(file_path)` - Upload test file
- `select_database(db_type)` - Select database
- `enter_credentials(credentials)` - Fill credential form
- `enter_openrouter_key(api_key, model)` - Enter LLM config
- `design_schema()` - Click design button
- `deploy_schema()` - Click deploy button
- `close()` - Close browser

**When to modify:**
- Add more test scenarios
- Update element selectors
- Add assertions/validations
- Create test data

---

## Configuration Files

### `.env.example` - Environment Variables Template
**Purpose:** Template for environment variables (sensitive data).

**Contains:**
- `OPENROUTER_API_KEY` - Your OpenRouter API key
- Database credentials (examples)
- Flask settings

**How to Use:**
1. Copy to `.env`
2. Fill in your actual values
3. Never commit `.env` to git

**When to modify:**
- Add new environment variables
- Update variable names
- Add documentation

---

### `requirements.txt` - Python Dependencies
Already explained above in Backend section.

---

## Documentation Files

### `README.md` - Project Overview
**Purpose:** High-level project documentation.

**Contains:**
- Project description
- Features list
- Setup instructions
- Usage guide
- API endpoints
- Database-specific setup
- Security notes

**When to modify:**
- Update setup instructions
- Add new features
- Document new endpoints
- Add troubleshooting section

---

### `CODE_STRUCTURE.md` - This File
**Purpose:** Detailed explanation of all code files.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  frontend/index.html (UI Structure)                  │   │
│  │  frontend/styles.css (Styling)                       │   │
│  │  frontend/app.js (User Interactions)                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP Requests
┌─────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  backend/app.py (API Routes)                         │   │
│  │  ├─ GET /api/databases                              │   │
│  │  ├─ POST /api/upload                                │   │
│  │  ├─ POST /api/design-schema                         │   │
│  │  └─ POST /api/deploy-schema                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  backend/services/                                   │   │
│  │  ├─ file_processor.py (Read & Analyze Files)        │   │
│  │  ├─ llm_service.py (Call OpenRouter API)            │   │
│  │  └─ db_connector.py (Connect to Databases)          │   │
│  └──────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  backend/config.py (Settings & Configuration)       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↓ External APIs
┌─────────────────────────────────────────────────────────────┐
│  OpenRouter API (LLM for Schema Design)                     │
│  Database Systems (Athena, Snowflake, SQL Server, etc.)     │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: What to Modify For Common Tasks

| Task | File(s) to Modify |
|------|-------------------|
| Add new database support | `backend/config.py`, `backend/services/db_connector.py`, `frontend/app.js` |
| Change UI colors | `frontend/styles.css` (`:root` variables) |
| Modify LLM prompt | `backend/services/llm_service.py` (_build_schema_design_prompt) |
| Add new form fields | `frontend/index.html`, `frontend/app.js` |
| Change file upload limit | `backend/config.py` (MAX_FILE_SIZE) |
| Add new API endpoint | `backend/app.py` |
| Fix file processing | `backend/services/file_processor.py` |
| Change database connection | `backend/services/db_connector.py` |
| Add validation | `frontend/app.js` (handleFileUpload, designSchema) |
| Update dependencies | `backend/requirements.txt` |

---

## File Relationships

```
app.py (Main)
├── Imports config.py (Settings)
├── Imports file_processor.py (File handling)
├── Imports llm_service.py (AI integration)
├── Imports db_connector.py (Database connections)
└── Serves frontend/
    ├── index.html (Structure)
    ├── styles.css (Styling)
    └── app.js (Logic)
        └── Calls API endpoints in app.py
```

---

## Environment Setup

**Backend Setup:**
1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows)
3. Install: `pip install -r backend/requirements.txt`
4. Create `.env` from `.env.example`
5. Run: `python backend/app.py`

**Frontend:**
- No installation needed
- Automatically served by Flask
- Access at `http://localhost:5000`

---

## Common Modifications Examples

### Example 1: Add a new database
1. Add to `backend/config.py` SUPPORTED_DATABASES
2. Add connection method in `backend/services/db_connector.py`
3. Add icon and form fields in `frontend/app.js` showCredentialsForm()

### Example 2: Change UI theme
1. Edit `:root` variables in `frontend/styles.css`
2. Update colors (--primary, --success, etc.)

### Example 3: Modify schema design prompt
1. Edit `backend/services/llm_service.py`
2. Modify `_build_schema_design_prompt()` method
3. Change what information is sent to LLM

### Example 4: Add file validation
1. Edit `frontend/app.js` handleFileUpload()
2. Add validation checks before upload
3. Show error toast if validation fails
