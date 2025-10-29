# Local Development Guide

This guide explains how to develop AI Sandbox applications on your laptop, then deploy to the server without code changes.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Local Environment Setup](#local-environment-setup)
3. [Running Applications](#running-applications)
4. [Development Workflow](#development-workflow)
5. [Server Migration](#server-migration)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

Get up and running in 5 minutes:

```bash
# 1. Clone repository (if not already)
cd ~/ai-sandbox-homelab

# 2. Start PostgreSQL
docker-compose -f docker-compose.local.yml up -d

# 3. Install Python dependencies
cd streamlit_apps/app1
pip install -r requirements.txt

# 4. Run the app
streamlit run streamlit_main.py
```

Open http://localhost:8501 in your browser.

---

## Local Environment Setup

### Prerequisites

- **Docker Desktop** installed and running
- **Python 3.12+** installed
- **Git** for version control

### 1. Database Setup (PostgreSQL)

Start PostgreSQL in Docker:

```bash
# From project root
docker-compose -f docker-compose.local.yml up -d
```

This starts:
- PostgreSQL on `localhost:5432`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `ai_sandbox`

**Optional: pgAdmin** (Database web UI):
```bash
# Start with pgAdmin
docker-compose -f docker-compose.local.yml --profile tools up -d

# Access at: http://localhost:5050
# Email: admin@localhost.com
# Password: admin
```

**Verify database**:
```bash
# Check if running
docker ps | grep postgres

# View logs
docker-compose -f docker-compose.local.yml logs -f postgres
```

### 2. Environment Configuration

The `.env` file is already configured for local development:

```bash
ENVIRONMENT=local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_sandbox
AI_PROVIDER=mock
AI_BASE_URL=http://localhost:11434
AI_MODEL=llama3.1:8b
OPENAI_API_KEY=
LOG_LEVEL=INFO
```

**No changes needed for local development!**

### 3. Python Environment

Install dependencies for the app you want to run:

```bash
# Option A: Global install (quick and dirty)
cd streamlit_apps/app1
pip install -r requirements.txt

# Option B: Virtual environment (recommended)
cd streamlit_apps/app1
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Running Applications

### App1 (Test Application)

```bash
cd streamlit_apps/app1
streamlit run streamlit_main.py
```

Opens at http://localhost:8501

**What it does:**
- System status dashboard
- AI Q&A interface
- Sentiment analysis
- AI interaction logs viewer

### Stopping Services

```bash
# Stop Streamlit: Ctrl+C in terminal

# Stop PostgreSQL
docker-compose -f docker-compose.local.yml down

# Stop and remove data (WARNING: Deletes database)
docker-compose -f docker-compose.local.yml down -v
```

---

## Development Workflow

### Creating a New App

Follow the convention: `streamlit_apps/appN/`

```bash
# Create app directory
mkdir -p streamlit_apps/app2

# Create required files
cd streamlit_apps/app2
touch streamlit_main.py
touch requirements.txt
touch README.md
```

**File structure:**
```
streamlit_apps/app2/
├── streamlit_main.py    # Entry point (MUST be this name)
├── requirements.txt     # Python dependencies
└── README.md           # App documentation
```

**Template `streamlit_main.py`:**
```python
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import get_config
from shared.db import get_session, init_database
from shared.ai import get_ai_client, call_structured_llm

st.title("My New App")

# Initialize database
init_database()

# Your app code here...
```

### Using Shared Utilities

**Configuration:**
```python
from shared.config import get_config

config = get_config()
print(f"Environment: {config.environment}")
print(f"AI Provider: {config.ai_provider}")
```

**Database:**
```python
from shared.db import get_session, init_database

# Initialize (run once at startup)
init_database()

# Query data
with get_session() as session:
    results = session.query(MyModel).all()
```

**AI Integration:**
```python
from shared.ai import get_ai_client, call_structured_llm
from shared.models import SimpleAIResponse

# Get client (handles mock/ollama/openai automatically)
client = get_ai_client()

# Call AI with structured response
response, call_id = call_structured_llm(
    client=client,
    response_model=SimpleAIResponse,
    user_prompt="What is Python?",
)

if response:
    print(response.answer)  # Type-safe!
else:
    print("AI failed - app still works (progressive enhancement)")
```

### Creating Custom Response Models

Add to `shared/models.py`:

```python
from pydantic import BaseModel, Field
from typing import List

class MyCustomResponse(BaseModel):
    """My custom AI response."""
    summary: str = Field(..., description="Brief summary")
    key_points: List[str] = Field(..., description="Main points")
    confidence: float = Field(..., ge=0, le=1, description="Confidence 0-1")
```

Then use in your app:

```python
from shared.models import MyCustomResponse

response, call_id = call_structured_llm(
    client=client,
    response_model=MyCustomResponse,
    user_prompt="Analyze this...",
)
```

### Testing Different AI Providers

**Mock (Default - Free, instant)**
```bash
# In .env
AI_PROVIDER=mock
```

**Ollama (Local AI - requires installation)**
```bash
# 1. Install Ollama: https://ollama.ai
# 2. Download model: ollama pull llama3.1:8b
# 3. Start server: ollama serve

# In .env
AI_PROVIDER=ollama
AI_BASE_URL=http://localhost:11434
AI_MODEL=llama3.1:8b
```

**OpenAI (Cloud API - requires API key)**
```bash
# Get API key: https://platform.openai.com/api-keys

# In .env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key...
AI_MODEL=gpt-4o-mini
```

---

## Server Migration

### When You're Ready to Deploy to Server

Your code is already server-ready! Just update configuration.

### Step 1: Update .env File

Change these values in `.env`:

```bash
# FROM (Local):
ENVIRONMENT=local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_sandbox
AI_PROVIDER=mock
AI_BASE_URL=http://localhost:11434

# TO (Server):
ENVIRONMENT=dev
DATABASE_URL=postgresql://postgres:your_password@192.168.1.101:5432/ai_sandbox
AI_PROVIDER=ollama
AI_BASE_URL=http://192.168.1.102:11434
```

**Complete .env for server:**
```bash
ENVIRONMENT=dev
DATABASE_URL=postgresql://postgres:your_password@192.168.1.101:5432/ai_sandbox
AI_PROVIDER=ollama
AI_BASE_URL=http://192.168.1.102:11434
AI_MODEL=llama3.1:8b
OPENAI_API_KEY=
LOG_LEVEL=INFO
```

### Step 2: Server Setup (One-Time)

**On VM 100 (PostgreSQL) - 192.168.1.101:**
```bash
# Already set up via infrastructure/docker/deploy-postgresql.sh
# Just verify it's running:
docker ps | grep postgres
```

**On VM 101 (Ollama) - 192.168.1.102:**
```bash
# Already set up via infrastructure/scripts/install-ollama.sh
# Verify:
ollama list
curl http://192.168.1.102:11434/api/tags
```

**On VM 102 (DEV Apps) - 192.168.1.103:**
```bash
# Clone repository
git clone https://github.com/JoshuaBearup/ai-sandbox-homelab.git
cd ai-sandbox-homelab

# Copy and update .env
cp .env.example .env
nano .env  # Update with server settings

# Install dependencies
cd streamlit_apps/app1
pip install -r requirements.txt

# Run app
streamlit run streamlit_main.py --server.port 8501 --server.address 0.0.0.0
```

### Step 3: Access Your App

From your laptop, access the server app:
```
http://192.168.1.103:8501
```

**That's it! Same code, different environment.**

---

## Configuration Reference

### Environment Variables

| Variable | Local | Server | Description |
|----------|-------|--------|-------------|
| `ENVIRONMENT` | `local` | `dev` / `preprod` / `prd` | Deployment environment |
| `DATABASE_URL` | `localhost:5432` | `192.168.1.101:5432` | PostgreSQL server |
| `AI_PROVIDER` | `mock` | `ollama` | AI service to use |
| `AI_BASE_URL` | `localhost:11434` | `192.168.1.102:11434` | Ollama server URL |
| `AI_MODEL` | `llama3.1:8b` | `llama3.1:8b` | Model name |
| `OPENAI_API_KEY` | *(empty)* | *(empty)* | Only if using OpenAI |
| `LOG_LEVEL` | `INFO` | `INFO` / `WARNING` | Logging verbosity |

### AI Provider Comparison

| Provider | Cost | Speed | Quality | Use Case |
|----------|------|-------|---------|----------|
| **Mock** | Free | Instant | N/A (fake) | Local development, testing |
| **Ollama** | Free | 15-25 tok/s | Good | Server deployment, privacy |
| **OpenAI** | $0.15-$10/1M tok | Fast | Excellent | Production fallback, high quality |

### Database Schemas

The `shared/db.py` module automatically creates these tables:

**ai_interaction_logs**
- `id`: Auto-increment primary key
- `call_id`: Unique UUID for each AI call
- `timestamp`: When call was made
- `provider`: mock / ollama / openai
- `model`: Model name
- `prompt`: User's prompt
- `response`: AI response (JSON)
- `success`: Boolean (did call succeed)
- `error_message`: Error details if failed
- `latency_ms`: Response time
- `environment`: Where call was made (local/dev/preprod/prd)

---

## Troubleshooting

### Database Connection Errors

**Symptom:** "Can't connect to database"

**Solutions:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# If not running, start it
docker-compose -f docker-compose.local.yml up -d

# Check logs
docker-compose -f docker-compose.local.yml logs postgres

# Verify connection manually
docker exec -it ai-sandbox-postgres-local psql -U postgres -d ai_sandbox

# Inside psql:
\dt  # List tables
SELECT 1;  # Test query
\q  # Exit
```

### AI Provider Errors

**Symptom:** "AI client not available"

**Mock provider:**
- Should always work
- If failing, check logs for Python errors

**Ollama provider:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start Ollama
ollama serve

# Verify model is downloaded
ollama list

# Download if needed
ollama pull llama3.1:8b
```

**OpenAI provider:**
```bash
# Check API key is set
echo $OPENAI_API_KEY

# Test key manually
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Import Errors

**Symptom:** "No module named 'shared'"

**Solution:**
```python
# Add this at top of streamlit_main.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Or install as package:**
```bash
# From project root
pip install -e streamlit_apps/
```

### Port Already in Use

**Symptom:** "Port 8501 already in use"

**Solution:**
```bash
# Find process using port
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill process or use different port
streamlit run streamlit_main.py --server.port 8502
```

### Docker Issues

**Symptom:** "Cannot connect to Docker daemon"

**Solution:**
```bash
# Make sure Docker Desktop is running

# Check Docker status
docker ps

# Restart Docker Desktop if needed
```

---

## Best Practices

### 1. Always Use Shared Utilities

✅ **Good:**
```python
from shared.db import get_session
from shared.ai import get_ai_client
```

❌ **Bad:**
```python
import psycopg2  # Don't use raw database connections
from openai import OpenAI  # Don't use AI clients directly
```

**Why:** Shared utilities handle configuration, error handling, and logging automatically.

### 2. Always Use Pydantic Models for AI Responses

✅ **Good:**
```python
class MyResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)

response, _ = call_structured_llm(
    response_model=MyResponse,
    ...
)
```

❌ **Bad:**
```python
response = client.chat("question")
data = json.loads(response)  # No validation!
```

**Why:** Type safety, automatic validation, better error messages.

### 3. Always Implement Progressive Enhancement

✅ **Good:**
```python
# Core feature (always works)
data = load_from_database()
display(data)

# AI enhancement (optional)
try:
    insights = get_ai_insights(data)
    if insights:
        display(insights)
except Exception:
    pass  # Core still works
```

❌ **Bad:**
```python
# App breaks if AI fails
insights = get_ai_insights(data)
display(insights)  # Error if AI down!
```

**Why:** Users can still use your app even when AI is unavailable.

### 4. Log All AI Interactions

The framework does this automatically via `call_structured_llm()`:
- Every call logged to database
- Includes prompt, response, latency
- Enables debugging and auditing

**View logs in app:** AI Logs tab shows all interactions

---

## Development Checklist

When creating a new app:

- [ ] Create `streamlit_apps/appN/` directory
- [ ] Create `streamlit_main.py` (must be this name)
- [ ] Create `requirements.txt` with dependencies
- [ ] Create `README.md` with app documentation
- [ ] Import from `shared.*` (not direct dependencies)
- [ ] Use Pydantic models for all AI responses
- [ ] Implement progressive enhancement (core works without AI)
- [ ] Test with all three AI providers (mock, ollama, openai)
- [ ] Test database connectivity
- [ ] Update `.env.example` if adding new config
- [ ] Document configuration changes in README

---

## Next Steps

Now that you have local development working:

1. **Build your application** locally using mock AI
2. **Test thoroughly** with local PostgreSQL
3. **Set up server infrastructure** (see [SETUP.md](SETUP.md))
4. **Update .env** with server settings
5. **Deploy to server** - same code, zero changes!

See [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for framework principles and patterns.

---

**Questions?** Check [AGENTS.md](AGENTS.md) for coding conventions or create an issue on GitHub.
