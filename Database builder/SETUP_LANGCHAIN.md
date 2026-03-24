# LangChain Integration - Setup & Testing Guide

## Quick Start

### Step 1: Install Dependencies

```bash
# Navigate to project root
cd "Database builder"

# Install all dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

**Expected output:**
```
Successfully installed langchain-0.1.14 langchain-community-0.0.38 langgraph-0.0.44 pydantic-2.5.0 ...
```

### Step 2: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your OpenRouter API key
# On Windows, use Notepad or your editor:
# OPENROUTER_API_KEY=your_actual_key_here
```

### Step 3: Run the Application

```bash
cd backend
python app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 4: Test in Browser

1. Open `http://localhost:5000`
2. You should see the database creator UI
3. Upload a CSV file
4. Select a database
5. Enter credentials
6. Enter OpenRouter API key
7. Click "Design Schema with AI"

---

## Testing the LangChain Integration

### Test 1: Verify LangChain is Working

```bash
# In Python shell
python

# Then run:
from backend.services.llm_service import LLMService
from backend.models.schema_models import SchemaDesign

print("✓ LangChain imports successful")
```

### Test 2: Test File Processing

```bash
# Create a test CSV file: test_data.csv
id,name,email,age
1,John,john@example.com,30
2,Jane,jane@example.com,25
3,Bob,bob@example.com,35

# In Python shell:
from backend.services.file_processor import FileProcessor

data = FileProcessor.read_file("test_data.csv")
analysis = FileProcessor.analyze_data_structure(data)

print(f"Rows: {analysis.row_count}")
print(f"Columns: {analysis.column_count}")
print(f"Primary keys: {analysis.potential_keys['primary_key_candidates']}")
```

**Expected output:**
```
Rows: 3
Columns: 4
Primary keys: ['id']
```

### Test 3: Test Schema Design (Requires OpenRouter API Key)

```bash
# In Python shell:
from backend.services.llm_service import LLMService
from backend.services.file_processor import FileProcessor

# Load and analyze data
data = FileProcessor.read_file("test_data.csv")
analysis = FileProcessor.analyze_data_structure(data)

# Design schema
llm = LLMService(api_key="your_openrouter_key")
result = llm.design_schema(analysis.model_dump())

print(f"Success: {result['success']}")
print(f"Schema type: {result['schema']['schema_type']}")
print(f"Tables: {len(result['schema']['tables'])}")
print(f"Cost: ${result['cost']}")
```

**Expected output:**
```
Success: True
Schema type: normalized
Tables: 1
Cost: $0.0123
```

### Test 4: Test Pydantic Validation

```bash
# In Python shell:
from backend.models.schema_models import SchemaDesign, Table, Column

# This should work
schema = SchemaDesign(
    schema_type="normalized",
    tables=[
        Table(
            name="users",
            columns=[
                Column(name="id", data_type="INT", primary_key=True),
                Column(name="email", data_type="VARCHAR(255)")
            ]
        )
    ],
    normalization_notes="Normalized to 3NF"
)

print("✓ Schema validation successful")

# This should fail
try:
    bad_schema = SchemaDesign(
        schema_type="invalid",  # Invalid type
        tables=[]
    )
except Exception as e:
    print(f"✓ Validation caught error: {e}")
```

---

## Verifying LangChain Features

### 1. Cost Tracking

```python
from backend.services.llm_service import LLMService

llm = LLMService()
result = llm.design_schema(analysis.model_dump())

print(f"Cost for this request: ${result['cost']}")
print(f"Total session cost: ${result['total_cost']}")
```

### 2. Type Safety

```python
from backend.models.schema_models import DataAnalysis

# This will validate automatically
analysis = DataAnalysis(
    row_count=100,
    column_count=5,
    columns=[...],
    sample_data=[...],
    potential_keys={...}
)

# Type hints work in IDE
print(analysis.row_count)  # IDE knows this is int
```

### 3. Structured Prompts

```python
from backend.chains.schema_designer_chain import SchemaDesignerChain

chain = SchemaDesignerChain(llm)
# Prompt is structured with variables, not string concatenation
schema = chain.design_schema(analysis.model_dump())
```

---

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'langchain'"

**Solution:**
```bash
pip install langchain langchain-community
```

### Issue 2: "OPENROUTER_API_KEY not found"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check it has the key
grep OPENROUTER_API_KEY .env

# If not, add it:
echo "OPENROUTER_API_KEY=your_key_here" >> .env
```

### Issue 3: "Pydantic validation error"

**Solution:**
- Check all required fields are provided
- Verify field types match schema
- Check field values are valid

```python
# Debug validation
from pydantic import ValidationError
from backend.models.schema_models import SchemaDesign

try:
    schema = SchemaDesign(...)
except ValidationError as e:
    print(e.json())  # Shows detailed validation errors
```

### Issue 4: "LLM response parsing failed"

**Solution:**
- Ensure LLM model supports JSON output
- Check OpenRouter API key is valid
- Verify model name is correct

```python
# Test LLM directly
from backend.services.llm_service import LLMService

llm = LLMService()
# If this fails, LLM is not working
```

---

## File Structure Verification

After setup, verify this structure exists:

```
backend/
├── app.py                          ✓
├── config.py                       ✓
├── requirements.txt                ✓
├── services/
│   ├── file_processor.py          ✓
│   ├── llm_service.py             ✓ (Updated)
│   └── db_connector.py            ✓
├── models/                         ✓ (NEW)
│   ├── __init__.py                ✓
│   └── schema_models.py           ✓
└── chains/                         ✓ (NEW)
    ├── __init__.py                ✓
    └── schema_designer_chain.py   ✓
```

---

## Performance Checklist

- [ ] App starts without errors
- [ ] File upload works
- [ ] File analysis returns Pydantic model
- [ ] Schema design returns with cost tracking
- [ ] Type validation works
- [ ] Error messages are clear
- [ ] No deprecation warnings

---

## Next Steps

After verifying Phase 1 works:

1. **Phase 2: LangGraph Workflow**
   - Create `backend/graphs/database_workflow.py`
   - Define workflow states
   - Add conditional branching

2. **Phase 3: Agents & Tools**
   - Create `backend/tools/database_tools.py`
   - Create `backend/agents/schema_agent.py`
   - Define tool descriptions

3. **Phase 4: Advanced Features**
   - Add memory/conversation history
   - Implement caching
   - Add workflow visualization

---

## Support

If you encounter issues:

1. Check error message carefully
2. Verify all dependencies installed: `pip list | grep langchain`
3. Check .env file has OPENROUTER_API_KEY
4. Check Python version: `python --version` (should be 3.8+)
5. Try reinstalling: `pip install --force-reinstall -r backend/requirements.txt`

---

## Summary

✅ **Phase 1 Implementation Complete**

**What's New:**
- LangChain integration for LLM calls
- Pydantic models for type safety
- Cost tracking
- Better error handling
- Structured prompts

**Status:** Ready to test and deploy

**Next:** Phase 2 - LangGraph workflow orchestration
