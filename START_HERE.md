# START HERE - New Claude Code Session Onboarding

**For AI Assistants**: Read this file first when starting a new session on this project.

---

## 🚀 Quick Project Summary

**AI Sandbox Home Lab** - A self-hosted AI development framework
- **Goal**: Build AI applications locally with zero cloud costs
- **Stack**: Streamlit + PostgreSQL + Ollama (or Mock AI for local dev)
- **Philosophy**: AI-first development, convention over configuration, type safety
- **Status**: Local development environment complete and tested ✅

---

## 📋 Session Startup Checklist

When starting any new Claude Code session, read these files **in order**:

### 1. **CURRENT_STATUS.md** (Read First!)
**Why**: Tells you what's done, what's next, and current blockers
**Contains**:
- Current phase and active work
- Completed tasks
- Next steps (priority order)
- Recent session summaries

### 2. **PROJECT_CONTEXT.md** (Read Second!)
**Why**: Complete mission, principles, and decision-making framework
**Contains**:
- The mission and success criteria
- 6 foundational principles
- System architecture
- Technology rationale
- Key patterns and conventions
- Decision-making framework

### 3. **logs/session_notes/[latest].md** (If Continuing Work)
**Why**: Understand what was done in the most recent session
**Look for**: Latest date in `logs/session_notes/`

### 4. **AGENTS.md** (If Writing Code)
**Why**: Coding conventions and patterns
**Contains**:
- File naming conventions
- Import patterns
- Code style guidelines
- Common patterns to follow

### 5. **DECISIONS.md** (If Questioning Choices)
**Why**: Understand why technical decisions were made
**Contains**: Rationale for major architectural choices

---

## 🎯 What You Need to Know

### Project Structure

```
ai-sandbox-homelab/
├── PROJECT_CONTEXT.md          ← Mission & principles
├── CURRENT_STATUS.md           ← What's done, what's next
├── START_HERE.md               ← This file (onboarding)
├── QUICKSTART.md               ← 5-minute setup guide
├── LOCAL_DEVELOPMENT.md        ← Complete dev guide
├── DEV_SCRIPTS.md              ← Helper scripts guide
├── AGENTS.md                   ← Coding conventions
├── DECISIONS.md                ← Decision log
├── LESSONS.md                  ← Lessons learned
├── SETUP.md                    ← Server infrastructure setup
│
├── .env.example                ← Configuration template
├── docker-compose.local.yml    ← Local PostgreSQL
├── dev.bat / dev.sh            ← Helper scripts
│
├── streamlit_apps/             ← Applications
│   ├── shared/                 ← Reusable utilities
│   │   ├── config.py           ← Configuration management
│   │   ├── db.py               ← Database utilities
│   │   ├── ai.py               ← AI client wrapper
│   │   └── models.py           ← Pydantic models
│   └── app1/                   ← First test app
│       ├── streamlit_main.py   ← Entry point
│       ├── requirements.txt    ← Dependencies
│       └── run.bat / run.sh    ← Launch scripts
│
├── infrastructure/             ← Infrastructure as code
│   ├── proxmox/                ← VM creation scripts
│   ├── docker/                 ← Docker configs
│   └── scripts/                ← Install scripts
│
├── docs/                       ← Architecture docs
└── logs/                       ← Session notes (not in git)
```

### Current Environment

**Local Development**:
- Environment: `local`
- Database: PostgreSQL in Docker (localhost:5432)
- AI Provider: `mock` (fake responses for testing)
- App: Streamlit on http://localhost:8501

**Server Deployment** (Future):
- VM 100: PostgreSQL (192.168.1.101)
- VM 101: Ollama AI (192.168.1.102)
- VM 102: Dev Apps (192.168.1.103)

### Key Technologies

- **Language**: Python 3.12
- **Web Framework**: Streamlit
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **AI**: Mock (local) → Ollama (server) → OpenAI (optional)
- **Containerization**: Docker
- **Platform**: Proxmox VE (server) / Laptop (local dev)

---

## 🛠️ Common Tasks

### User Wants to Start Development
1. Read CURRENT_STATUS.md to see what's next
2. Check if they have local environment set up
3. If not: Guide them through QUICKSTART.md
4. If yes: Use helper scripts (DEV_SCRIPTS.md)

### User Wants to Build a Feature
1. Check AGENTS.md for coding conventions
2. Follow shared utilities patterns
3. Use Pydantic for all AI responses
4. Implement progressive enhancement (core works without AI)
5. Update CURRENT_STATUS.md when done

### User Wants to Deploy to Server
1. Check SETUP.md for infrastructure steps
2. Use LOCAL_DEVELOPMENT.md for migration guide
3. Only .env needs to change - no code changes!

### User Has Questions About Decisions
1. Check DECISIONS.md for rationale
2. Refer to PROJECT_CONTEXT.md for principles

### User Asks "What Should I Build Next?"
1. Check CURRENT_STATUS.md "Next Steps" section
2. Suggest based on current phase:
   - Phase 1: Documentation ✅ COMPLETE
   - Phase 2: Local development ✅ COMPLETE
   - Phase 3: Server infrastructure (future)
   - Phase 4: Production apps (future)

---

## 🎨 Coding Principles (Quick Ref)

When writing code, always follow these:

1. **AI-First Development** - Rich docs, type hints, clear naming
2. **Convention Over Configuration** - Standard patterns, minimal config
3. **Validation Before Action** - Check before deploying
4. **Separation of Concerns** - Clear layer boundaries
5. **Progressive Enhancement** - Core works without AI
6. **Type Safety** - Pydantic for all data models

### Code Patterns to Follow

**Imports**:
```python
from shared.config import get_config
from shared.db import get_session
from shared.ai import get_ai_client, call_structured_llm
from shared.models import SimpleAIResponse
```

**AI Integration**:
```python
# 1. Define Pydantic model
class MyResponse(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)

# 2. Get client
client = get_ai_client()

# 3. Call with validation
response, call_id = call_structured_llm(
    client=client,
    response_model=MyResponse,
    user_prompt="question",
)

# 4. Handle gracefully
if response:
    use(response.answer)  # Type-safe!
else:
    # Core still works
    fallback()
```

---

## 📝 Documentation Update Protocol

After completing significant work:

1. **CURRENT_STATUS.md** - Move completed items, update next steps
2. **logs/session_notes/YYYY-MM-DD.md** - Create session notes
3. **DECISIONS.md** - Log any major decisions
4. **LESSONS.md** - Record lessons learned
5. **Git commit** - Commit all changes

### Session Ending Checklist
```
□ Update CURRENT_STATUS.md
□ Create/update session notes
□ Update DECISIONS.md (if decisions made)
□ Update LESSONS.md (if discoveries made)
□ Git commit and push
```

---

## 🚨 Important Reminders

### Security
- ⚠️ Never commit `.env` file (contains secrets)
- ✅ Always run apps with `--server.address=localhost` for local dev
- ✅ Mock AI provider is default (zero cost, instant, safe)

### Conventions
- ⚠️ App entry point MUST be `streamlit_main.py`
- ⚠️ Apps MUST be in `streamlit_apps/appN/` format
- ⚠️ Always import from `shared.*` (never cross-app imports)
- ⚠️ Dependencies in `requirements.txt` (not `environment.yml` - we changed this)

### Testing
- ✅ Test with mock AI locally before deploying
- ✅ Verify database connectivity
- ✅ Check that core features work without AI
- ✅ Run helper scripts to ensure they work

---

## 🎯 User Intent Recognition

### "I want to work on the project"
→ Read CURRENT_STATUS.md and suggest next priority task

### "I want to build [feature]"
→ Check if infrastructure is ready, guide through implementation

### "How do I [setup/run/deploy]?"
→ Point to relevant guide:
- Setup: QUICKSTART.md
- Run: DEV_SCRIPTS.md
- Deploy: LOCAL_DEVELOPMENT.md (migration section)

### "Why did we [make decision]?"
→ Check DECISIONS.md, explain rationale

### "Something isn't working"
→ Check helper scripts, verify environment, troubleshoot

### "What's the status?"
→ Read CURRENT_STATUS.md and summarize

---

## 💡 Pro Tips for AI Assistants

1. **Always check CURRENT_STATUS.md first** - It's the source of truth
2. **Use TodoWrite tool** for multi-step tasks (track progress)
3. **Update documentation** as you work (don't batch it all at the end)
4. **Follow the principles** in PROJECT_CONTEXT.md religiously
5. **Test locally** before suggesting server deployment
6. **Commit frequently** with clear messages
7. **Ask clarifying questions** if user intent is ambiguous
8. **Reference file paths** with line numbers when explaining code

---

## 🔗 Quick Links

**For Users**:
- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [DEV_SCRIPTS.md](DEV_SCRIPTS.md) - Helper commands
- [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Complete dev guide

**For AI Assistants**:
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) - Complete mission & principles
- [CURRENT_STATUS.md](CURRENT_STATUS.md) - What's done, what's next
- [AGENTS.md](AGENTS.md) - Coding conventions

**Infrastructure**:
- [SETUP.md](SETUP.md) - Server infrastructure setup
- [infrastructure/](infrastructure/) - Scripts and configs

---

## ✅ You're Ready!

With this context, you should be able to:
- ✅ Understand the project's mission and principles
- ✅ Know what's been completed and what's next
- ✅ Follow coding conventions and patterns
- ✅ Help users with setup, development, and deployment
- ✅ Make decisions aligned with project principles
- ✅ Update documentation properly

**Welcome to the AI Sandbox Home Lab project!** 🚀

---

*Last updated: 2025-01-29*
*Review this file at the start of every new Claude Code session*
