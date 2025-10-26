# Current Project Status

**Last Updated**: 2025-01-24 22:30
**Current Phase**: Phase 1 - Foundation (Documentation & Planning)
**Active Work**: Ready to begin VM creation
**Next Action**: Create VM 100 (PostgreSQL)

---

## Quick Context

Self-hosted AI development framework on home lab server.
- **Goal**: Enterprise-grade AI app platform, zero cloud costs
- **Based on**: Snowflake principles document (adapted for self-hosting)
- **AI Provider**: Ollama with Llama 3.1 8B (local, $0/month)

---

## Server Specs

- **Model**: Dell with Dual Intel Xeon E5-2699 v3
- **CPU**: 72 threads (36 physical cores, 2 sockets)
- **RAM**: 126GB
- **Storage**: 2.18TB (HDDStorage) + 237GB (local-lvm)
- **Platform**: Proxmox VE
- **Performance**: Excellent for local AI (15-25 tokens/sec expected)

---

## Completed ✓

### Infrastructure
- [x] Server specs assessed and documented
- [x] Storage configured (HDDStorage 2TB available)
- [x] Old VMs cleaned up (100, 101, 103 deleted)
- [x] Static IP confirmed
- [x] Proxmox ready for VM creation

### Documentation
- [x] GitHub repository created (ai-sandbox-homelab)
- [x] Directory structure established
- [x] AGENTS.md written (AI assistant instructions)
- [x] DECISIONS.md written (3 key decisions logged)
- [x] Session notes created (2025-01-24.md)
- [x] Documentation workflow established

### Decisions Made
- [x] Use Ollama (local) instead of OpenAI API (Decision 001)
- [x] VM resource allocation planned (Decision 002)
- [x] Documentation-first approach (Decision 003)

---

## In Progress 🔄

*Nothing currently in progress*

---

## Next Steps (Priority Order)

### Immediate (This Session or Next)
1. [ ] Create CURRENT_STATUS.md (this file)
2. [ ] Create VM 100: PostgreSQL
   - 4 cores, 8GB RAM, 100GB disk (HDDStorage)
   - Debian 12, static IP
3. [ ] Install Docker on VM 100
4. [ ] Deploy PostgreSQL 16 container
5. [ ] Test database connectivity

### Phase 2: AI Infrastructure (Next Session)
6. [ ] Create VM 101: Ollama AI Server
   - 32 cores, 64GB RAM, 200GB disk (HDDStorage)
   - Debian 12, static IP
7. [ ] Install Ollama
8. [ ] Download Llama 3.1 8B model
9. [ ] Test Ollama API endpoint
10. [ ] Document performance benchmarks

### Phase 3: Development Environment (Later)
11. [ ] Create VM 102: DEV Apps
12. [ ] Install Docker on VM 102
13. [ ] Build shared utilities (db.py, openai.py)
14. [ ] Create first test app (app1)

---

## Blocked/Issues ⚠️

*None currently*

---

## VM Allocation Plan

| VM ID | Purpose | Cores | RAM | Disk | Storage | IP | Status |
|-------|---------|-------|-----|------|---------|-------|--------|
| 100 | PostgreSQL | 4 | 8GB | 100GB | HDDStorage | TBD | Planned |
| 101 | Ollama AI | 32 | 64GB | 200GB | HDDStorage | TBD | Planned |
| 102 | DEV Apps | 16 | 32GB | 100GB | HDDStorage | TBD | Planned |

**Remaining Resources**: 20 cores, 22GB RAM (buffer for host/future)

---

## Important File Locations

### Key Documentation
- `AGENTS.md` - AI assistant instructions and conventions
- `DECISIONS.md` - Decision log with rationale
- `LESSONS.md` - Lessons learned (to be populated)
- `SETUP.md` - Step-by-step reproducible setup (to be written)

### Session Work
- `logs/session_notes/2025-01-24.md` - Latest session notes
- `logs/decisions/` - Archived decision records
- `logs/lessons/` - Archived lessons learned

### Code (Not Yet Created)
- `streamlit_apps/shared/` - Shared utilities
- `infrastructure/scripts/` - Automation scripts

---

## For New Claude Code Sessions

**Always start by reading these files in order:**

1. **CURRENT_STATUS.md** (this file) - What's done, what's next
2. **logs/session_notes/[latest].md** - Recent work details
3. **AGENTS.md** - Project conventions and patterns
4. **DECISIONS.md** - Context on why choices were made

**Starter prompt template:**
```
I'm continuing work on my AI sandbox home lab.

Read for context:
- CURRENT_STATUS.md
- logs/session_notes/2025-01-24.md
- AGENTS.md
- DECISIONS.md

I need help with: [your specific task]
```

---

## Project Principles (Quick Reference)

1. **AI-First Development** - Optimize code for AI assistants
2. **Convention Over Configuration** - Standard patterns, minimal config
3. **Validation Before Action** - Check before deploying
4. **Type Safety** - Pydantic for all data models
5. **Progressive Enhancement** - Core features always work, AI enhances
6. **Documentation as Code** - Docs version with code in git

---

## Tech Stack Summary

```
Platform: Proxmox VMs (Debian 12)
Database: PostgreSQL 16 (Docker)
AI: Ollama + Llama 3.1 8B (local)
Apps: Streamlit + Docker
ORM: SQLAlchemy
Language: Python 3.12
Version Control: GitHub (private repo)
```

---

## Session Log Summary

**2025-01-24**: Project kickoff
- Server assessment completed
- Storage configured
- Documentation system designed and implemented
- Ready to begin VM creation

---

*Update this file at the end of every work session*
