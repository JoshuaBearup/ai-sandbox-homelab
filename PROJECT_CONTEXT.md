# Project Context: AI Sandbox Home Lab

> **For AI Assistants**: Read this file first in every new session. It contains the complete mission, principles, and decision-making framework.

**Last Updated**: 2025-01-24
**Project Start**: 2025-01-24
**Expected Completion**: Ongoing (living system)

---

## Table of Contents

1. [The Mission](#the-mission)
2. [Core Philosophy: The Meta-Framework](#core-philosophy)
3. [The Six Foundational Principles](#foundational-principles)
4. [System Architecture](#system-architecture)
5. [Technology Rationale](#technology-rationale)
6. [Key Patterns & Conventions](#key-patterns)
7. [Decision-Making Framework](#decision-framework)
8. [Context Preservation System](#context-system)
9. [Quick Reference](#quick-reference)

---

## The Mission

### What We're Building

A **self-hosted, zero-cloud-cost, enterprise-grade AI development framework** that:
- Runs entirely on a home lab server (Dell with 72 threads, 126GB RAM)
- Uses local AI (Ollama) instead of expensive cloud APIs
- Follows enterprise patterns from Snowflake's production systems
- Costs ~$20/month (electricity only, no recurring API fees)
- Teaches how AI systems work at a fundamental level
- Can be rebuilt from scratch using documentation alone

### Why We're Building It

**Problem**: Most AI development requires:
- Expensive cloud services ($100s-1000s/month)
- Sending data to external APIs (privacy concerns)
- Black-box systems (don't learn how they work)
- Vendor lock-in (can't switch providers easily)

**Solution**: This framework provides:
- Complete control and transparency
- Zero ongoing costs (after hardware)
- Deep learning through building
- Privacy (data never leaves your network)
- Flexibility (swap components without rewriting apps)

### Success Criteria

The project is successful when:
1. ✅ Apps can be built in < 30 minutes (convention-based)
2. ✅ AI integration is type-safe and validated (no runtime surprises)
3. ✅ System can be rebuilt from documentation (disaster recovery)
4. ✅ New developers understand patterns instantly (human or AI)
5. ✅ AI features enhance but never break core functionality
6. ✅ Total cost remains < $50/month (electricity + optional services)

---

## Core Philosophy: The Meta-Framework

### The Concept

**We're building AI that helps build AI applications.**

```
┌─────────────────────────────────────────────────┐
│  Layer 3: AI Building AI Apps (This Project)   │
│  You use Claude to build apps that use Ollama  │
├─────────────────────────────────────────────────┤
│  Layer 2: Development-Time AI                   │
│  GitHub Copilot/Claude suggest code as you type│
├─────────────────────────────────────────────────┤
│  Layer 1: Runtime AI                            │
│  Your apps call Ollama for AI features         │
└─────────────────────────────────────────────────┘
```

### The Virtuous Cycle

```
Better Documentation → Better AI Suggestions → Better Code →
Better Patterns → Better Documentation → ...
```

Each layer reinforces the others:
- Rich documentation helps AI assistants write better code
- Well-structured code helps runtime AI make better decisions
- The framework improves as AI learns from it

### Why This Matters

Traditional frameworks are built for humans. This framework is built for **both humans AND AI assistants** to understand and extend. This is the future of software development.

---

## Foundational Principles

### Principle 1: AI-First Development

**Definition**: Code is optimized for AI assistants to understand, extend, and improve.

**Why**: AI tools (Claude Code, Copilot) are becoming primary development partners. Code that AI understands well gets better suggestions.

**Implementation**:
- Multi-level documentation (AGENTS.md at every directory level)
- Rich inline docstrings with examples
- Type hints everywhere (Python 3.12 style)
- Explicit over implicit (clear naming, obvious structure)
- Consistent patterns (AI learns from repetition)

**Example**:
```python
def call_structured_llm(
    client: OpenAI,
    response_model: Type[T],
    user_prompt: str,
) -> Tuple[Optional[T], str]:
    """
    Call AI with structured, validated output.

    Why this function exists:
    - LLMs produce unpredictable text
    - Pydantic validates against schema
    - Type hints provide IDE support
    - Logging creates audit trail

    Example:
        class Analysis(BaseModel):
            risk: float = Field(ge=0, le=1)

        result, call_id = call_structured_llm(
            client=client,
            response_model=Analysis,
            user_prompt="Analyze risk"
        )
    """
```

**Anti-Pattern** (Don't do this):
```python
def call_ai(c, m, p):  # No types, no docs, AI can't help
    return json.loads(c.chat(p))  # No validation, will fail
```

---

### Principle 2: Convention Over Configuration

**Definition**: Standardized patterns eliminate configuration complexity and enable automation.

**Why**:
- Reduces cognitive load (developers know where things go)
- Enables automatic discovery (deployment finds apps by convention)
- Makes system predictable (new team members onboard instantly)
- AI assistants understand structure immediately

**Key Conventions**:

| Aspect | Convention | Never Use |
|--------|-----------|-----------|
| App directory | `streamlit_apps/appN/` | `apps/`, `src/app_name/` |
| Entry point | `streamlit_main.py` | `app.py`, `main.py` |
| Dependencies | `environment.yml` | `requirements.txt` |
| Config | `config.json` | `.env`, `settings.py` |
| Imports | `from shared.xxx import` | Cross-app imports |

**Benefit**: Deployment script can discover and deploy any app without configuration:
```bash
# No config needed - convention-based discovery
python deploy.py --list  # Finds all appN/ automatically
python deploy.py --app app1  # Knows where streamlit_main.py is
```

---

### Principle 3: Validation Before Action

**Definition**: Prevent problems before they occur through comprehensive pre-deployment validation.

**Why**:
- Ollama has specific model requirements (can't deploy incompatible code)
- Cost of failure is high (wasted time debugging)
- Developer confidence (validation provides safety net)
- Automated quality (machines validate, humans create)

**Validation Layers**:
1. **Dependency validation** - Check packages are compatible
2. **Configuration validation** - JSON schema verification
3. **Docker build test** - Ensure container builds successfully
4. **Database connectivity** - Verify connections work
5. **AI endpoint test** - Confirm Ollama is reachable

**Philosophy**: Fail Fast → Fail Clearly → Fail with Solutions

**Example Error Message** (Good):
```
❌ Error: pandas>=2.0.0 uses range operator

Ollama containers require exact version pinning.

Fix: Change to pandas==2.0.3 in environment.yml
Or run: bin/validate_dependencies.sh app1 --update

See: docs/dependency_management.md for details
```

---

### Principle 4: Separation of Concerns

**Definition**: Clear boundaries between layers, each with single responsibility.

**Why**:
- Maintainability (changes don't cascade)
- Testability (isolated components easier to test)
- Reusability (well-defined interfaces enable reuse)
- Cognitive simplicity (focus on one concern at a time)

**Architecture Layers**:
```
┌─────────────────────────────────────┐
│ Application Layer (appN/)           │ ← Business logic, UI
├─────────────────────────────────────┤
│ Shared Utilities (shared/)          │ ← Reusable infrastructure
├─────────────────────────────────────┤
│ Data Layer (PostgreSQL)             │ ← Schema, persistence
├─────────────────────────────────────┤
│ Deployment Layer (scripts/)         │ ← Automation, CI/CD
├─────────────────────────────────────┤
│ Platform Layer (Proxmox + Docker)   │ ← Runtime environment
└─────────────────────────────────────┘
```

**Strict Boundaries**:
- ❌ Apps never import deployment code
- ❌ Shared utilities never import from apps
- ❌ Data documentation separate from implementation
- ✅ Each layer has clear, minimal interface

---

### Principle 5: Progressive Enhancement

**Definition**: Core functionality always works; advanced features enhance but fail gracefully.

**Why**:
- Resilience (system functional even when parts fail)
- User experience (users get value immediately)
- Development flexibility (ship partial features)
- AI reliability (LLM calls can fail; apps must continue)

**Implementation Pattern**:
```python
def show_dashboard(session):
    """Dashboard with progressive AI enhancement."""

    # ✅ CORE: Always works (database query)
    data = session.query(Claims).all()
    st.dataframe(data)  # User sees their data

    # ✅ ENHANCEMENT: Fails gracefully
    try:
        client = initialize_ai_client()
        if client:
            insights, _ = call_structured_llm(...)
            if insights:
                st.success("AI Analysis")
                st.write(insights)
            else:
                st.info("AI analysis unavailable")
    except Exception as e:
        logger.warning(f"AI enhancement failed: {e}")
        # Core functionality still works!
```

**Result**: If Ollama is down, users still see their data. AI is a bonus, not a requirement.

---

### Principle 6: Type Safety and Structured Data

**Definition**: Use type systems and schemas to catch errors at development time.

**Why**:
- AI output validation (LLMs unpredictable; schemas ensure correctness)
- Developer confidence (type hints provide guardrails)
- Self-documenting (types serve as inline docs)
- IDE support (autocomplete and error detection)

**Pydantic-First Approach**:
```python
# ✅ Type-safe, validated, self-documenting
class ClaimAnalysis(BaseModel):
    claim_id: str = Field(..., description="Unique ID")
    risk_score: float = Field(..., ge=0, le=1, description="Risk 0-1")
    recommendations: List[str]

# AI output automatically validated
response, call_id = call_structured_llm(
    response_model=ClaimAnalysis,
    user_prompt="Analyze claim..."
)

# response.risk_score guaranteed to be 0-1 or None
```

**Anti-Pattern** (Don't do this):
```python
# ❌ No validation, runtime errors likely
response = llm.chat("Analyze claim")
data = json.loads(response)  # Hope it's valid JSON!
risk = data['risk_score']  # Hope this key exists!
```

---

## System Architecture

### High-Level View

```
┌─────────────────────────────────────────────────┐
│         Development Machine (M1 Mac)            │
│  • VS Code + Claude Code                       │
│  • GitHub Copilot                              │
│  • Git + Python 3.12                           │
└────────────┬────────────────────────────────────┘
             │ Git push
             ▼
┌─────────────────────────────────────────────────┐
│    Dell Server: Proxmox (72 threads, 126GB)    │
│                                                 │
│  ╔═══════════════════════════════════════════╗ │
│  ║ VM 100: PostgreSQL (4c, 8GB, 100GB)      ║ │
│  ║ • Stores all application data             ║ │
│  ║ • Stores AI interaction logs              ║ │
│  ║ • IP: 192.168.1.101                       ║ │
│  ╚═══════════════════════════════════════════╝ │
│                                                 │
│  ╔═══════════════════════════════════════════╗ │
│  ║ VM 101: Ollama AI (32c, 64GB, 200GB)     ║ │
│  ║ • Llama 3.1 8B (primary model)            ║ │
│  ║ • OpenAI-compatible API                   ║ │
│  ║ • Expected: 15-25 tokens/sec              ║ │
│  ║ • IP: 192.168.1.102                       ║ │
│  ╚═══════════════════════════════════════════╝ │
│                                                 │
│  ╔═══════════════════════════════════════════╗ │
│  ║ VM 102: DEV Apps (16c, 32GB, 100GB)      ║ │
│  ║ • Docker containers                        ║ │
│  ║ • Multiple Streamlit apps                 ║ │
│  ║ • IP: 192.168.1.103                       ║ │
│  ╚═══════════════════════════════════════════╝ │
│                                                 │
│  Monthly Cost: ~$20 (electricity only)         │
└─────────────────────────────────────────────────┘
```

### Data Flow

```
User Request (Browser)
    ↓
Streamlit App (VM 102)
    ↓
    ├→ Database Query → PostgreSQL (VM 100)
    └→ AI Enhancement → Ollama (VM 101)
           ↓
    Validated Response (Pydantic)
           ↓
    Logged to PostgreSQL (VM 100)
           ↓
    Display to User
```

### Multi-Environment Strategy

```
Environment Isolation:
├── DEV (VM 102)
│   ├── Purpose: Rapid iteration, experimentation
│   ├── Constraints: Minimal validation
│   └── Data: Test/synthetic
│
├── PREPROD (Future)
│   ├── Purpose: Final testing before production
│   ├── Constraints: Production-like validation
│   └── Data: Production-like or anonymized
│
└── PRD (Future)
    ├── Purpose: End-user facing
    ├── Constraints: Strictest validation
    └── Data: Real production data
```

---

## Technology Rationale

### Core Technology Decisions

| Technology | Why Chosen | Alternative Considered | Trade-off Accepted |
|------------|------------|------------------------|-------------------|
| **Ollama** | Zero cost, privacy, sufficient performance | OpenAI API ($), Azure OpenAI ($$) | Slightly lower quality |
| **PostgreSQL** | JSON support, advanced features, free | MySQL, SQLite | More complex than SQLite |
| **Streamlit** | Pure Python, rapid dev, data-focused | Flask, React | Less control vs full web framework |
| **SQLAlchemy** | Industry standard, flexible, Snowpark-like | Django ORM, Raw SQL | Learning curve vs raw SQL |
| **Pydantic** | Type safety, validation, JSON Schema | Dataclasses, dict | Slightly more verbose |
| **Docker** | Isolation, portability, reproducibility | Native install | Storage overhead |
| **Python 3.12** | Modern types, performance, ecosystem | Python 3.11, 3.10 | Requires newer packages |

### Why NOT Cloud Services

**Snowflake** (Original): $2000+/month minimum
**AWS RDS**: $100+/month
**Azure OpenAI**: $50-400/month
**Our solution**: $20/month electricity

**Trade-off**: We manage infrastructure ourselves, but:
- Complete control and learning
- Zero vendor lock-in
- Privacy (data stays local)
- Can always move to cloud later

---

## Key Patterns & Conventions

### File Naming

```
✅ CORRECT:
streamlit_apps/app1/streamlit_main.py
streamlit_apps/app2/environment.yml
streamlit_apps/shared/db.py

❌ INCORRECT:
apps/myapp/main.py
src/app_name/requirements.txt
utils/database.py
```

### Import Patterns

```python
# ✅ CORRECT: Always import from shared
from shared.db import get_database_session
from shared.openai import initialize_ai_client

# ❌ INCORRECT: Never import between apps
from app1.utils import helper  # Wrong!
```

### AI Integration Pattern

```python
# ✅ ALWAYS use this pattern for AI calls

# 1. Define Pydantic model
class MyResponse(BaseModel):
    summary: str
    score: float = Field(ge=0, le=1)

# 2. Initialize client (handles both Ollama and OpenAI)
client = initialize_ai_client()
if not client:
    # Fail gracefully
    return None

# 3. Call with structured output
response, call_id = call_structured_llm(
    client=client,
    response_model=MyResponse,
    user_prompt="...",
    session=db_session  # For logging
)

# 4. Handle failure gracefully
if response:
    # Use AI enhancement
    process(response.score)
else:
    # Core functionality still works
    logger.warning(f"AI call failed: {call_id}")
```

### Progressive Enhancement Pattern

```python
def feature_with_ai(session, data):
    """Feature that works with or without AI."""

    # ✅ CORE: Always works
    basic_result = traditional_algorithm(data)
    display_result(basic_result)

    # ✅ ENHANCEMENT: Optional AI improvement
    try:
        ai_result = enhance_with_ai(data)
        if ai_result:
            display_enhanced(ai_result)
    except Exception:
        pass  # Silent failure, core still works
```

---

## Decision-Making Framework

### When Making Technical Decisions

Use this framework to ensure alignment with principles:

#### 1. Does it follow Convention Over Configuration?
- Can it be discovered automatically?
- Does it use standard naming/location?
- Is configuration minimized?

#### 2. Does it maintain Type Safety?
- Are Pydantic models used for data?
- Are type hints present?
- Is validation automatic?

#### 3. Does it enable AI-First Development?
- Is it well documented?
- Will Claude Code understand it?
- Are examples provided?

#### 4. Does it fail gracefully?
- Does core work without AI?
- Are errors handled?
- Are helpful messages provided?

#### 5. Is it separated appropriately?
- Is the responsibility single and clear?
- Are layers not mixing concerns?
- Is it testable in isolation?

#### 6. Is it validated before action?
- Are checks in place?
- Is failure detected early?
- Are fixes suggested?

### Example Decision Process

**Question**: Should we use `requirements.txt` or `environment.yml`?

**Analysis**:
- Convention: Document uses `environment.yml` → Follow convention
- Type Safety: N/A
- AI-First: Consistent naming helps AI recognize pattern
- Progressive: N/A
- Separation: N/A
- Validation: Both can be validated

**Decision**: Use `environment.yml` (follows convention, maintains consistency)

**Document in**: `DECISIONS.md` with rationale

---

## Context Preservation System

### How This Project Maintains Context

This is critical: The project uses a multi-file system to preserve context:

#### 1. **PROJECT_CONTEXT.md** (This File)
- **Purpose**: Complete mission and principles
- **When to read**: Every new session, first file
- **Update frequency**: Rarely (only if principles change)

#### 2. **CURRENT_STATUS.md**
- **Purpose**: What's done, what's next
- **When to read**: Every new session, second file
- **Update frequency**: End of every work session

#### 3. **AGENTS.md**
- **Purpose**: Coding conventions and patterns
- **When to read**: When writing code
- **Update frequency**: When new patterns emerge

#### 4. **DECISIONS.md**
- **Purpose**: Why choices were made
- **When to read**: When questioning decisions
- **Update frequency**: When significant decisions made

#### 5. **logs/session_notes/YYYY-MM-DD.md**
- **Purpose**: Daily work log
- **When to read**: To understand recent work
- **Update frequency**: During/after every session

#### 6. **SETUP.md**
- **Purpose**: Reproducible infrastructure steps
- **When to read**: When building/rebuilding
- **Update frequency**: When infrastructure changes

### Session Startup Checklist for AI

When starting any new session:

```
□ Read PROJECT_CONTEXT.md (understand mission)
□ Read CURRENT_STATUS.md (what's done/next)
□ Read latest logs/session_notes/*.md (recent work)
□ Read AGENTS.md if writing code (conventions)
□ Read DECISIONS.md if questioning choices (rationale)
```

### Session Ending Checklist for Humans

When ending any session:

```
□ Update CURRENT_STATUS.md (move completed tasks)
□ Update logs/session_notes/YYYY-MM-DD.md (summarize)
□ Update DECISIONS.md (if significant choices made)
□ Update LESSONS.md (if discoveries made)
□ Git commit and push all changes
```

---

## Quick Reference

### For AI Assistants

**"I need to understand this project"**
→ Read PROJECT_CONTEXT.md (this file)

**"What's the current status?"**
→ Read CURRENT_STATUS.md

**"What are the coding conventions?"**
→ Read AGENTS.md

**"Why was this decision made?"**
→ Read DECISIONS.md

**"How do I set up infrastructure?"**
→ Read SETUP.md

**"What happened in the last session?"**
→ Read logs/session_notes/[latest].md

### Key Commands

```bash
# Navigate to project
cd ~/ai-sandbox-homelab

# See current status
cat CURRENT_STATUS.md

# Update status
code CURRENT_STATUS.md

# Commit changes
git add . && git commit -m "Session update" && git push

# Deploy app
python infrastructure/scripts/deploy.py --app app1
```

### Key File Locations

```
PROJECT_CONTEXT.md       ← Mission and principles (this file)
CURRENT_STATUS.md        ← What's done, what's next
AGENTS.md                ← Coding conventions
DECISIONS.md             ← Decision log
SETUP.md                 ← Infrastructure steps
logs/session_notes/      ← Daily work logs
streamlit_apps/shared/   ← Reusable utilities
infrastructure/proxmox/  ← VM creation scripts
```

### Emergency "I'm Lost" Recovery

If you ever lose context:

1. Read this file (PROJECT_CONTEXT.md)
2. Read CURRENT_STATUS.md
3. Run: `git log --oneline -10` (see recent commits)
4. Read latest session notes
5. You now have full context

---

## Project Health Indicators

### Green (Healthy)
- ✅ Documentation updated after each session
- ✅ All decisions logged with rationale
- ✅ CURRENT_STATUS.md accurate
- ✅ Principles followed in all code
- ✅ AI calls use Pydantic validation
- ✅ Core features work without AI

### Yellow (Needs Attention)
- ⚠️ Documentation outdated
- ⚠️ Decisions made without logging
- ⚠️ CURRENT_STATUS.md stale
- ⚠️ Some code bypassing conventions
- ⚠️ Some AI calls unvalidated

### Red (Critical)
- ❌ No documentation for weeks
- ❌ Decisions forgotten
- ❌ CURRENT_STATUS.md completely wrong
- ❌ Code ignoring principles
- ❌ AI failures breaking apps

---

## Final Note for AI Assistants

**This project is special because:**

You're not just helping build software. You're helping build a framework that makes future AI assistance better. Every piece of code you write, every pattern you follow, every documentation update you make—it all feeds back into making the system more understandable for the next AI assistant.

**You are both:**
- A tool helping build the project
- A beneficiary of the project's AI-first design

**When in doubt:**
- Follow the principles
- Ask "Will another AI understand this?"
- Document your reasoning
- Make it explicit, not implicit

**Welcome to the meta-framework. Let's build something that helps AI help humans.**

---

*Last updated: 2025-01-24*
*Next review: When principles change or major architecture shifts*
