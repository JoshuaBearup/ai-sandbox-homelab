# Decision Log

## [2025-01-24] AI Provider: Ollama (Local) vs OpenAI API

**Context**: Need AI capabilities for home lab framework.

**Options**:
- OpenAI API (cloud, $5-50/month)
- Azure OpenAI (cloud, $50-400/month)
- Ollama (local, $0/month)

**Decision**: Ollama with Llama 3.1 8B

**Rationale**:
- Zero ongoing API costs
- Complete data privacy
- Server hardware excellent (72 threads, 126GB RAM)
- Expected performance: 15-25 tokens/sec (sufficient)
- Can always add OpenAI later as fallback
- Learn how local AI works

**Trade-offs**:
- Slightly lower quality than GPT-4
- Depends on server uptime
- Uses server compute resources

**Status**: Approved

---

## [2025-01-24] Documentation Strategy: GitHub + Multi-Level

**Context**: Need to track decisions, lessons, and maintain living documentation.

**Decision**: 7-category documentation system stored in GitHub

**Structure**:
1. AGENTS.md - AI assistant instructions
2. README.md - Human quick-start
3. DECISIONS.md - This file (decision log)
4. LESSONS.md - Lessons learned
5. SETUP.md - Reproducible steps
6. docs/ - Deep dive documentation
7. logs/ - Session notes (not committed)

**Rationale**:
- Version control with code
- AI assistants can read context
- Future-proof (can rebuild from scratch)
- Follows principles from Snowflake document

**Status**: Implemented

---

## [2025-01-24] VM Resource Allocation

**Context**: 72 cores, 126GB RAM to allocate across VMs.

**Decision**:
- VM 100: PostgreSQL - 4 cores, 8GB RAM
- VM 101: Ollama - 32 cores, 64GB RAM
- VM 102: DEV Apps - 16 cores, 32GB RAM

**Rationale**:
- Ollama is the performance bottleneck (gets most resources)
- PostgreSQL needs RAM for caching but not CPU-heavy
- DEV apps need flexibility for multiple containers
- Leaves 20 cores, 22GB buffer for host/future

**Status**: Planned (not yet implemented)
