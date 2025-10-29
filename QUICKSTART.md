# Quick Start Guide

Get the AI Sandbox running on your laptop in 5 minutes!

## Prerequisites

1. **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
2. **Python 3.12+** - [Download here](https://www.python.org/downloads/)
3. **Git** - [Download here](https://git-scm.com/downloads)

## Step 1: Start Docker Desktop

Make sure Docker Desktop is running (check system tray/menu bar for Docker icon).

## Step 2: Start PostgreSQL

From the project root directory:

```bash
docker-compose -f docker-compose.local.yml up -d
```

**Wait ~10 seconds** for PostgreSQL to fully start.

**Verify it's running:**
```bash
docker ps
```

You should see `ai-sandbox-postgres-local` container running.

## Step 3: Install Python Dependencies

```bash
cd streamlit_apps/app1
pip install -r requirements.txt
```

**Note:** On Windows, you might need to install Visual C++ Build Tools for `psycopg2-binary`. Alternatively:
```bash
# If psycopg2-binary fails on Windows:
pip install psycopg2-binary --only-binary :all:
```

## Step 4: Run the App

```bash
# From streamlit_apps/app1 directory
streamlit run streamlit_main.py
```

Your browser will automatically open to http://localhost:8501

## What You'll See

The app has 4 tabs:

1. **System Status** - Check configuration and connectivity
2. **AI Q&A** - Ask questions (uses mock AI for testing)
3. **Sentiment Analysis** - Analyze text sentiment
4. **AI Logs** - View all AI interactions

## Understanding Mock AI

By default, the app uses **Mock AI** (fake responses for testing):
- ✅ Zero cost
- ✅ Instant responses
- ✅ No internet needed
- ✅ Perfect for development

**Mock responses are realistic-looking fake data.** This lets you:
- Test the UI and database
- Verify type safety and validation
- Develop features without real AI

## Testing the App

### Test 1: System Status
1. Go to "System Status" tab
2. Check that:
   - Environment = LOCAL
   - AI Provider = MOCK
   - Database = Connected ✅
   - AI Service = Available ✅

### Test 2: AI Q&A
1. Go to "AI Q&A" tab
2. Type a question: "What is Python?"
3. Click "Ask AI"
4. You'll get a mock response with confidence score

### Test 3: View Logs
1. Go to "AI Logs" tab
2. You'll see your Q&A logged in the database
3. Expand a log entry to see full details

### Test 4: Database Persistence
1. Ask another question in AI Q&A
2. Stop the app (Ctrl+C)
3. Restart: `streamlit run streamlit_main.py`
4. Check AI Logs - your previous questions are still there!

## Stopping Services

```bash
# Stop Streamlit: Ctrl+C in terminal

# Stop PostgreSQL
docker-compose -f docker-compose.local.yml down

# Stop and DELETE all data (WARNING: Removes database)
docker-compose -f docker-compose.local.yml down -v
```

## Next Steps

### Want to Use Real AI?

**Option A: Ollama (Local, Free)**
```bash
# 1. Install Ollama: https://ollama.ai
# 2. Download model
ollama pull llama3.2:3b  # Smaller model for laptops

# 3. Start server
ollama serve

# 4. Update .env
AI_PROVIDER=ollama
AI_BASE_URL=http://localhost:11434
AI_MODEL=llama3.2:3b
```

**Option B: OpenAI (Cloud, Paid)**
```bash
# 1. Get API key: https://platform.openai.com/api-keys

# 2. Update .env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...your-key...
AI_MODEL=gpt-4o-mini
```

### Want to Build Your Own App?

See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for complete development guide.

### Want to Deploy to Server?

See [SETUP.md](SETUP.md) for server infrastructure setup.

## Troubleshooting

### "Cannot connect to Docker daemon"
- Make sure Docker Desktop is running
- Check system tray/menu bar for Docker icon
- Try restarting Docker Desktop

### "Port 5432 already in use"
- Another PostgreSQL is running
- Stop it or change port in docker-compose.local.yml

### "Cannot connect to database"
```bash
# Check if container is running
docker ps

# Check logs
docker-compose -f docker-compose.local.yml logs postgres

# Restart container
docker-compose -f docker-compose.local.yml restart
```

### "Module not found: shared"
```bash
# Make sure you're running from the correct directory
cd streamlit_apps/app1
streamlit run streamlit_main.py
```

### "psycopg2 installation failed" (Windows)
```bash
# Use pre-built binary
pip install psycopg2-binary --only-binary :all:

# Or install Visual C++ Build Tools:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

## Help & Documentation

- **LOCAL_DEVELOPMENT.md** - Complete development guide
- **PROJECT_CONTEXT.md** - Project mission and principles
- **CURRENT_STATUS.md** - What's done, what's next
- **AGENTS.md** - Coding conventions

## Questions?

Create an issue on GitHub or check the documentation files above.

---

**Welcome to the AI Sandbox! Happy building!** 🚀
