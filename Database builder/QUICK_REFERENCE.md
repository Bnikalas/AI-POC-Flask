# LangChain Integration - Quick Reference

## Installation & Setup (2 minutes)

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add OPENROUTER_API_KEY

# Run app
cd backend
python app.py

# Open browser
# http://localhost:5000
```

---

## Key Files & Their Purpose

| File | Purpose | Status |
|------|---------|--------|
| `backend/models/schema_models.py` | Pydantic models | ✅ NEW |
| `backend/chains/schema_designer_chain.py` | LangChain chain | ✅ NEW |
| `backend/services/llm_service.py` | LLM integration | ✅ UPDATED |
| `backend/services/file_processor.py` | File processing | ✅ UPDATED |
| `backend/app.py` | Flask API | ✅ UPDATED |
| `backend/config.py` | Configuration | ✅ UPDATED |
| `backend/requirements.txt` | Dependencies | ✅ UPDATED |

---

## Core Classes

### FileProcessor
```python
from backend.services.file_processor import FileProcessor

# Read file
data = FileProcessor.read_file("file.csv")

# Analyze
analysis = FileProcessor.analyze_data_structure(data)
# Returns: DataAnalysis (Pydantic model)

# Detect keys
keys = FileProcessor.detect_potential_keys(data)
```

### LLMService
```python
from backend.services.llm_service import LLMService

# Initialize
llm = LLMService(api_key="key", model="model")

# Design schema
result = llm.design_schema(analysis.model_dump())
# Returns: {"success": bool, "schema": dict, "cost": float}

# Get cost
total = llm.get_total_cost()
```

### SchemaDesignerChain
```python
from backend.chains.schema_designer_chain import SchemaDesignerChain

# Initialize
chain = SchemaDesignerChain(llm)

# Design schema
schema = chain.design_schema(data_analysis)
# Returns: SchemaDesign (Pydantic model)

# Validate
chain.validate_schema(schema)
```

### Pydantic Models
```python
from backend.models.schema_models import (
    Column, Table, Relationship, SchemaDesign, DataAnalysis
)

# All models have:
# - Automatic validation
# - Type hints
# - JSON serialization
# - Clear error messages

# Example
schema = SchemaDesign(
    schema_type="normalized",
    tables=[...],
    relationships=[...],
    normalization_notes="..."
)

# Serialize to JSON
json_data = schema.model_dump()
```

---

## API Endpoints

### GET /api/health
```bash
curl http://localhost:5000/api/health
# Response: {"status": "healthy", "langchain_enabled": true}
```

### GET /api/databases
```bash
curl http://localhost:5000/api/databases
# Response: {"databases": {"athena": "Amazon Athena", ...}}
```

### POST /api/upload
```bash
curl -F "file=@data.csv" http://localhost:5000/api/upload
# Response: {
#   "success": true,
#   "filename": "data.csv",
#   "analysis": {DataAnalysis model}
# }
```

### POST /api/design-schema
```bash
curl -X POST http://localhost:5000/api/design-schema \
  -H "Content-Type: application/json" \
  -d '{
    "file_analysis": {...},
    "openrouter_key": "key",
    "model": "model"
  }'
# Response: {
#   "success": true,
#   "schema": {SchemaDesign model},
#   "cost": 0.0123,
#   "total_cost": 0.0456
# }
```

---

## Common Tasks

### Task 1: Upload and Analyze File
```python
from backend.services.file_processor import FileProcessor

# Read file
data = FileProcessor.read_file("data.csv")

# Analyze
analysis = FileProcessor.analyze_data_structure(data)

# Access results
print(f"Rows: {analysis.row_count}")
print(f"Columns: {analysis.column_count}")
print(f"Primary keys: {analysis.potential_keys['primary_key_candidates']}")
```

### Task 2: Design Schema
```python
from backend.services.llm_service import LLMService
from backend.services.file_processor import FileProcessor

# Analyze file
data = FileProcessor.read_file("data.csv")
analysis = FileProcessor.analyze_data_structure(data)

# Design schema
llm = LLMService(api_key="your_key")
result = llm.design_schema(analysis.model_dump())

# Check result
if result['success']:
    schema = result['schema']
    print(f"Schema type: {schema['schema_type']}")
    print(f"Tables: {len(schema['tables'])}")
    print(f"Cost: ${result['cost']}")
else:
    print(f"Error: {result['error']}")
```

### Task 3: Validate Schema
```python
from backend.chains.schema_designer_chain import SchemaDesignerChain
from backend.models.schema_models import SchemaDesign

# Create chain
chain = SchemaDesignerChain(llm)

# Validate
try:
    chain.validate_schema(schema)
    print("✓ Schema is valid")
except ValueError as e:
    print(f"✗ Validation error: {e}")
```

### Task 4: Track Costs
```python
from backend.services.llm_service import LLMService

llm = LLMService()

# Make calls
result1 = llm.design_schema(analysis1.model_dump())
result2 = llm.design_schema(analysis2.model_dump())

# Get total cost
total = llm.get_total_cost()
print(f"Total cost: ${total}")

# Reset
llm.reset_cost()
```

---

## Troubleshooting

### Error: "No module named 'langchain'"
```bash
pip install langchain langchain-community
```

### Error: "OPENROUTER_API_KEY not found"
```bash
# Check .env file
cat .env | grep OPENROUTER_API_KEY

# If missing, add it
echo "OPENROUTER_API_KEY=your_key" >> .env
```

### Error: "Pydantic validation error"
```python
# Check field types
from pydantic import ValidationError

try:
    schema = SchemaDesign(...)
except ValidationError as e:
    print(e.json())  # Shows detailed errors
```

### Error: "Schema design failed"
```python
# Check LLM is working
from backend.services.llm_service import LLMService

llm = LLMService()
# If this fails, LLM is not configured correctly
```

---

## Configuration

### Environment Variables (.env)
```bash
# Required
OPENROUTER_API_KEY=your_key

# Optional - LangChain monitoring
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=database-creator

# Optional - Caching
ENABLE_CACHING=true
CACHE_TYPE=in_memory
```

### Config File (backend/config.py)
```python
# LLM Settings
DEFAULT_LLM_MODEL = "meta-llama/llama-2-70b-chat"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000

# File Upload
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {"csv", "parquet"}

# Caching
ENABLE_CACHING = True
CACHE_TYPE = "in_memory"
```

---

## Data Models

### DataAnalysis
```python
{
    "row_count": int,
    "column_count": int,
    "columns": [
        {
            "name": str,
            "dtype": str,
            "null_count": int,
            "unique_count": int,
            "sample_values": list
        }
    ],
    "sample_data": list,
    "potential_keys": {
        "primary_key_candidates": list,
        "foreign_key_candidates": list
    }
}
```

### SchemaDesign
```python
{
    "schema_type": "normalized|star|snowflake",
    "tables": [
        {
            "name": str,
            "columns": [
                {
                    "name": str,
                    "data_type": str,
                    "nullable": bool,
                    "primary_key": bool,
                    "foreign_key": str|null
                }
            ]
        }
    ],
    "relationships": [
        {
            "from_table": str,
            "to_table": str,
            "from_column": str,
            "to_column": str,
            "relationship_type": str
        }
    ],
    "normalization_notes": str,
    "recommendations": list
}
```

---

## Performance Tips

1. **Cache Results**
   ```python
   # Enable caching in .env
   ENABLE_CACHING=true
   ```

2. **Batch Requests**
   ```python
   # Process multiple files efficiently
   for file in files:
       analysis = FileProcessor.analyze_data_structure(data)
       # Reuse LLM instance
       result = llm.design_schema(analysis.model_dump())
   ```

3. **Monitor Costs**
   ```python
   # Track API costs
   total = llm.get_total_cost()
   print(f"Total cost: ${total}")
   ```

4. **Use Appropriate Model**
   ```python
   # Faster, cheaper models for simple tasks
   llm = LLMService(model="gpt-3.5-turbo")
   
   # More capable models for complex tasks
   llm = LLMService(model="gpt-4")
   ```

---

## Testing

### Unit Test Example
```python
from backend.models.schema_models import SchemaDesign

def test_schema_validation():
    schema = SchemaDesign(
        schema_type="normalized",
        tables=[...],
        normalization_notes="Test"
    )
    assert schema.schema_type == "normalized"
    print("✓ Test passed")
```

### Integration Test Example
```python
from backend.services.file_processor import FileProcessor
from backend.services.llm_service import LLMService

def test_full_workflow():
    # Upload
    data = FileProcessor.read_file("test.csv")
    analysis = FileProcessor.analyze_data_structure(data)
    
    # Design
    llm = LLMService()
    result = llm.design_schema(analysis.model_dump())
    
    # Verify
    assert result['success']
    assert 'schema' in result
    print("✓ Full workflow test passed")
```

---

## Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list | grep langchain

# Install specific version
pip install langchain==0.1.14

# Reinstall all dependencies
pip install --force-reinstall -r backend/requirements.txt

# Run app with debug
FLASK_DEBUG=1 python backend/app.py

# Run tests
pytest tests/

# Check code style
flake8 backend/

# Type checking
mypy backend/
```

---

## Resources

- **LangChain Docs:** https://python.langchain.com/
- **Pydantic Docs:** https://docs.pydantic.dev/
- **OpenRouter Docs:** https://openrouter.ai/docs
- **LangSmith:** https://smith.langchain.com/

---

## Summary

✅ **Phase 1 Complete**
- LangChain integrated
- Pydantic models implemented
- Cost tracking enabled
- Type safety achieved

📚 **Documentation**
- SETUP_LANGCHAIN.md - Setup guide
- LANGCHAIN_IMPLEMENTATION.md - Implementation details
- PHASE1_SUMMARY.md - Complete summary
- QUICK_REFERENCE.md - This file

🚀 **Next Phase**
- LangGraph workflow orchestration
- Agent & tools implementation
- Advanced features

---

## Quick Links

| Document | Purpose |
|----------|---------|
| SETUP_LANGCHAIN.md | How to set up and test |
| LANGCHAIN_IMPLEMENTATION.md | What was implemented |
| PHASE1_SUMMARY.md | Complete summary |
| CODE_STRUCTURE.md | Code organization |
| LANGCHAIN_INTEGRATION.md | Architecture & planning |
