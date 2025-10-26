# AI Sandbox Home Lab - Guide for AI Assistants

## Project Overview
Self-hosted AI development framework on Dell server (Proxmox).
Zero recurring costs. Based on enterprise principles.

**Server**: Dual Xeon E5-2699 v3 (72 threads), 126GB RAM, 2TB storage
**Stage**: Phase 1 - Documentation & Planning
**AI**: Ollama with Llama 3.1 8B (local)

## Core Principles

1. **AI-First Development** - Code optimized for AI to read
2. **Convention Over Configuration** - Standard patterns
3. **Validation Before Action** - Check before deploying
4. **Type Safety** - Pydantic for all data models
5. **Progressive Enhancement** - Core works, AI enhances
6. **Documentation as Code** - Docs version with code

## Technology Stack
```
Platform: Proxmox VMs
Database: PostgreSQL 16
AI: Ollama (Llama 3.1 8B)
Apps: Streamlit + Docker
Data Access: SQLAlchemy
Language: Python 3.12
```

## Key Conventions

- Apps: `streamlit_apps/appN/` (app1, app2...)
- Entry: Always `streamlit_main.py`
- Dependencies: Always `environment.yml` (exact versions)
- Config: Always `config.json`
- Imports: Always `from shared.xxx import`

## Current Status

**Active**: Phase 1 - Foundation
- Documentation structure created
- Server specs assessed
- VM allocation planned

**Next**: Phase 2 - Infrastructure
- Create VMs (100: PostgreSQL, 101: Ollama, 102: DEV)
- Install and configure services
- Test Ollama models

## When Generating Code

**DO**:
- Follow established patterns exactly
- Add comprehensive docstrings
- Use type hints everywhere
- Include error handling
- Update DECISIONS.md for choices

**DON'T**:
- Use requirements.txt (use environment.yml)
- Hardcode values
- Skip docstrings
- Make AI features required

## Documentation

- Today's work: `logs/session_notes/2025-01-24.md`
- Decisions: `DECISIONS.md`
- Setup steps: `SETUP.md` (to be written)
- Architecture: `docs/00_architecture.md` (to be written)
