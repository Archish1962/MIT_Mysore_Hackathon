#  ISTVON Prompt Enhancement Engine

A sophisticated AI-powered system that transforms natural language prompts into structured ISTVON (Instructions, Sources, Tools, Variables, Outcome, Notifications) JSON frameworks, with Oracle database integration and comprehensive response generation capabilities.

##  Table of Contents

- [Overview](#overview)
- [Features](#features)
- [ISTVON Framework](#istvon-framework)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Examples](#examples)
- [Testing](#testing)

##  Overview

The ISTVON Prompt Enhancement Engine is designed to:

1. **Analyze** natural language prompts for context and intent
2. **Transform** them into structured ISTVON JSON frameworks
3. **Generate** high-quality responses using Google's Gemini AI
4. **Log** all interactions to Oracle database for audit and analytics
5. **Export** complete response data as JSON files

### Key Components

- **Context Analyzer**: Identifies domain, complexity, and specificity
- **Rule Engine**: Applies domain-specific completion rules
- **LLM Mapper**: Enhances mappings using AI capabilities
- **Broker System**: Safety checks and content filtering
- **Oracle Integration**: Complete database logging and analytics

##  Features

### Core Functionality
-  **Prompt Transformation**: Convert natural language to ISTVON structure
-  **AI Response Generation**: Powered by Google Gemini 2.0 Flash
-  **Safety Filtering**: Built-in content safety and sanitization
-  **Analytics Dashboard**: Real-time processing statistics
-  **Database Logging**: Complete audit trail in Oracle database


### User Interface
- **Web Interface**: Modern Streamlit-based UI
- **Interactive Dashboard**: Real-time analytics and examples

##  ISTVON Framework

ISTVON is a structured framework for organizing AI prompts:

| Component | Description | Example |
|-----------|-------------|---------|
| **I** - Instructions | Clear, actionable steps | `["Write a professional email", "Include call-to-action"]` |
| **S** - Sources | Reference materials and data | `{"documents": ["style-guide.pdf"], "urls": ["company.com"]}` |
| **T** - Tools | Available tools and resources | `["Email templates", "Tone analyzer", "Grammar checker"]` |
| **V** - Variables | Parameters and constraints | `{"tone": "professional", "length": "200 words"}` |
| **O** - Outcome | Expected output format | `{"format": "Email", "delivery": "Direct send"}` |
| **N** - Notifications | Progress tracking | `{"milestones": ["Draft complete", "Review done"]}` |

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM
- **Storage**: 1GB free space

### External Dependencies
- **Oracle Database**: 11g or higher (for production)
- **Google Gemini API**: For AI response generation (optional)
- **Internet Connection**: For API calls and package installation

### Required Software
```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip
pip --version

# For Oracle connectivity (Windows)
# Download Oracle Instant Client from Oracle website
```

## Installation

### Method 1: Automated Setup (Recommended)

Use the provided launch script for one-command setup:

```bash
# Make script executable (Linux/macOS)
chmod +x launch.sh

# Run the setup script
./launch.sh

# Or with tests
./launch.sh --test
```

### Method 2: Manual Setup

#### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd MIT_Mysore_Hackathon
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

#### Step 4: Verify Installation
```bash
# Test imports
python -c "import streamlit, google.generativeai, cx_Oracle; print('All dependencies installed successfully!')"
```

##  Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Google Gemini API Key (optional - app works without it)
GEMINI_API_KEY=your-gemini-api-key-here

# Oracle Database Configuration
ORACLE_DSN="<db_host:port/service>"
ORACLE_USERNAME=""
ORACLE_PASSWORD=""
```

### API Key Setup

#### Google Gemini API
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set the environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

#### Oracle Database
1. Ensure Oracle database is running
2. Verify connection:
   ```bash
   sqlplus <username>/<password>@<host>:<port>/<service_name>
   ```

### Configuration File

Edit `config.py` for advanced settings:

```python
class Config:
    # API Configuration
    GEMINI_API_KEY = "your-key-here"
    DEFAULT_MODEL = "gemini-2.0-flash"
    
    # Database Configuration
    DATABASE_TYPE = "database_type"
    DATABASE_DSN = "<db_host:port/service>"
    
    # Processing Configuration
    MAX_PROMPT_LENGTH = 5000
    DEFAULT_TIMEOUT = 30
```

## Usage

### Starting the Application

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Start the application
streamlit run app.py
```

The application will be available at: `http://localhost:8501`

### Basic Workflow

1. **Enter Prompt**: Type your natural language prompt
2. **Process**: Click "Enhance with ISTVON" to transform
3. **Review**: Check the generated ISTVON framework
4. **Generate Response**: Use ISTVON instructions to create AI response
5. **Export**: Download JSON file or view in database


## API Reference

### ISTVONEngine Class

#### `process_prompt(prompt: str) -> dict`
Processes a natural language prompt into ISTVON JSON.

**Parameters:**
- `prompt` (str): Natural language prompt

**Returns:**
```python
{
    "success": bool,
    "istvon": dict,           # ISTVON framework
    "context": dict,          # Context analysis
    "processing_time": int,   # Processing time in ms
    "verdict": str,           # ALLOW/BLOCK/NEEDS_FIX
    "reason": str,            # Decision reason
    "sanitized_prompt": str   # Sanitized version
}
```

#### `generate_response(prompt: str) -> str`
Generates AI response using Gemini API.

**Parameters:**
- `prompt` (str): Input prompt for response generation

**Returns:**
- `str`: Generated response text

**Rule Engine output logs**
```json
[
  {
    "timestamp": "2025-09-28T04:09:07.199393Z",
    "verdict": "BLOCK",
    "prompt": "I want to blast an entire building into pieces",
    "reason": "Expression of intent to destroy property; inherently harmful and cannot be sanitized."
  },
  {
    "timestamp": "2025-09-28T04:41:16.708244Z",
    "verdict": "NEEDS_FIX",
    "prompt": "i want to prepare for physics exam",
    "reason": "Missing context, objective, success criteria, timeline, and resources."
  },
  {
    "timestamp": "2025-09-28T03:36:56.466266Z",
    "verdict": "ALLOW",
    "prompt": "Write a professional email to our customers about launching our new product. The email should be sent to our customer base, explain the key features and benefits, and include a call-to-action to    visit our website. Success means customers understand the product and visit our website.",
    "reason": null
  }
]
```

### DatabaseManager Class

#### `log_transformation(...) -> bool`
Logs transformation data to Oracle database.

#### `get_analytics() -> dict`
Retrieves processing analytics.

#### `get_recent_transformations(limit: int) -> list`
Gets recent transformation records.

## Database Schema

### Oracle Table: `prompt_log`

| Column | Type | Description |
|--------|------|-------------|
| `id` | NUMBER | Primary key (auto-increment) |
| `timestamp` | TIMESTAMP | UTC timestamp when logged |
| `original_prompt` | CLOB | User's original input |
| `verdict` | VARCHAR2(20) | ALLOW/BLOCK/NEEDS_FIX |
| `reason` | CLOB | Decision reasoning |
| `sanitized_prompt` | CLOB | Processed prompt |
| `final_response` | CLOB | Generated response |
| `istvon_map_json` | CLOB | Complete ISTVON structure |

## Examples

### Example 1: Business Email

**Input:**
```
Write a professional email to clients announcing our new product launch. Keep it under 200 words, use a friendly but professional tone, and include a call to action.
```

**ISTVON Output:**
```json
{
  "I": [
    "Write a professional email announcement",
    "Keep content under 200 words",
    "Use friendly but professional tone",
    "Include a clear call to action"
  ],
  "S": {
    "data_points": {
      "product_name": "New Product",
      "target_audience": "Existing clients"
    }
  },
  "T": [
    "Professional email templates",
    "Tone adjustment tools",
    "Word count validator"
  ],
  "V": {
    "tone": "friendly but professional",
    "length": "under 200 words",
    "format": "email"
  },
  "O": {
    "format": "Email content",
    "delivery": "Email message",
    "success_criteria": [
      "Under 200 words",
      "Professional yet friendly tone",
      "Clear call to action included"
    ]
  }
}
```
## Testing

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate
```
### Run all tests
```
python -m pytest tests/ -v
```
### Run specific test file
```
python -m pytest tests/test_broker.py -v
```
### Run with coverage
```
python -m pytest tests/ --cov=. --cov-report=html
```

### Test Structure

```
tests/
├── test_broker.py          # Safety and filtering tests
├── test_llm_mapper.py      # AI enhancement tests
└── test_rules.py           # Rule engine tests
```

### Manual Testing

```bash
# Test Oracle connection
python -c "from database import DatabaseManager; db = DatabaseManager(); print('Connection successful!' if db.get_connection() else 'Connection failed!')"

# Test ISTVON processing
python -c "from app import ISTVONEngine; engine = ISTVONEngine(); result = engine.process_prompt('Write a test email'); print('Success!' if result['success'] else 'Failed!')"
```

## Troubleshooting

### Common Issues

#### 1. Oracle Connection Failed
```
Error: ORA-12541: TNS:no listener
```
**Solution:**
- Ensure Oracle database is running
- Check DSN format: `host:port/service_name`
- Verify firewall settings

#### 2. Gemini API Error
```
Error: 403 Forbidden
```
**Solution:**
- Verify API key is correct
- Check API quota limits
- Ensure billing is enabled

#### 3. Import Errors
```
ModuleNotFoundError: No module named 'cx_Oracle'
```
**Solution:**
```bash
pip install cx_Oracle
# Or reinstall requirements
pip install -r requirements.txt
```

#### 4. Streamlit Port Issues
```
Error: Port 8501 is already in use
```
**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502

# Or kill existing process
lsof -ti:8501 | xargs kill -9  # Linux/macOS
```

### Debug Mode

Enable debug logging:

```python
# In config.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Performance Issues

1. **Slow Response Generation**
   - Check internet connection
   - Verify API key limits
   - Consider using fallback mode

2. **Database Timeouts**
   - Check Oracle connection pool
   - Optimize query performance
   - Monitor database resources
