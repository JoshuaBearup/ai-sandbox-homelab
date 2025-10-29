# App1 - Test Application

A demonstration Streamlit application showcasing the AI Sandbox framework patterns.

## Features

- **System Status**: View configuration and test connectivity
- **AI Q&A**: Ask questions and get AI-powered answers with confidence scoring
- **Sentiment Analysis**: Analyze text sentiment with key phrase extraction
- **AI Logs**: View all AI interactions logged to database

## Running Locally

### Prerequisites

1. PostgreSQL running (use docker-compose.local.yml)
2. Python 3.12+
3. `.env` file configured (see `.env.example`)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_main.py
```

The app will open at http://localhost:8501

## Configuration

The app uses environment variables from `.env`:

- `ENVIRONMENT`: Set to "local" for development
- `DATABASE_URL`: PostgreSQL connection string
- `AI_PROVIDER`: "mock" for testing, "ollama" for server, "openai" for cloud
- `AI_MODEL`: Model name (provider-specific)

See [.env.example](../../.env.example) for details.

## Architecture

```
streamlit_main.py
    ↓
    ├─→ shared/config.py (configuration)
    ├─→ shared/db.py (database)
    ├─→ shared/ai.py (AI client)
    └─→ shared/models.py (data models)
```

## Patterns Demonstrated

### 1. Progressive Enhancement
- App works even if AI fails
- Core features always available
- AI enhances but doesn't block

### 2. Type Safety
- All AI responses validated with Pydantic
- Type hints throughout
- Runtime validation

### 3. Separation of Concerns
- UI layer (streamlit_main.py)
- Business logic (shared utilities)
- Data layer (PostgreSQL)

### 4. Convention Over Configuration
- Standard file naming (streamlit_main.py)
- Conventional imports (from shared.*)
- Minimal configuration needed

## Migrating to Server

To run this app on the server (VM 102):

1. Update `.env`:
   - Change `ENVIRONMENT` to "dev"
   - Change `DATABASE_URL` to VM 100 (192.168.1.101)
   - Change `AI_PROVIDER` to "ollama"
   - Change `AI_BASE_URL` to VM 101 (192.168.1.102:11434)

2. No code changes needed!

See [LOCAL_DEVELOPMENT.md](../../LOCAL_DEVELOPMENT.md) for detailed migration guide.
