# Automated Database Creator - Project Structure

```
automated-db-creator/
├── backend/
│   ├── app.py                 # Flask/FastAPI main app
│   ├── requirements.txt
│   ├── config.py              # Configuration management
│   ├── services/
│   │   ├── file_processor.py  # CSV/Parquet parsing
│   │   ├── llm_service.py     # OpenRouter integration
│   │   ├── schema_designer.py # Schema generation logic
│   │   └── db_connector.py    # Multi-DB connection handler
│   ├── models/
│   │   ├── database_models.py # DB connection models
│   │   └── schema_models.py   # Schema data structures
│   └── routes/
│       ├── upload.py          # File upload endpoint
│       ├── database.py        # DB selection/connection
│       └── schema.py          # Schema generation endpoint
├── frontend/
│   ├── selenium_ui.py         # Selenium-based UI
│   ├── pages/
│   │   ├── upload_page.py
│   │   ├── db_selection_page.py
│   │   ├── credentials_page.py
│   │   └── schema_preview_page.py
│   └── utils/
│       └── browser_driver.py
├── tests/
│   ├── test_file_processor.py
│   ├── test_llm_service.py
│   └── test_db_connector.py
├── .env.example
└── README.md
```
