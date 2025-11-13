# AI Sandbox Home Lab

A self-hosted AI development framework with zero cloud costs.

**New to this project?** Start here:
- 👤 **For Users**: [QUICKSTART.md](QUICKSTART.md) - Get running in 5 minutes
- 🤖 **For AI Assistants**: [START_HERE.md](START_HERE.md) - New session onboarding

## Overview

This repository contains a complete local development environment for building AI-powered applications:
- **Stack**: Streamlit + PostgreSQL + Ollama (or Mock AI for local dev)
- **Cost**: ~$20/month (electricity only, no API fees)
- **Philosophy**: AI-first development, convention over configuration, type safety

## Structure

- `docs/` - Detailed documentation
- `logs/` - Decision logs, lessons learned, and session notes
- `streamlit_apps/` - Streamlit applications and shared components
- `infrastructure/` - Infrastructure as code and deployment scripts
  - `proxmox/` - Proxmox VM configurations
  - `docker/` - Docker compose files and configurations
  - `scripts/` - Automation and utility scripts

## Quick Start

**Local Development** (laptop):
1. [QUICKSTART.md](QUICKSTART.md) - 5-minute setup
2. [DEV_SCRIPTS.md](DEV_SCRIPTS.md) - Helper commands
3. [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) - Complete guide

**Server Deployment** (future):
- [SETUP.md](SETUP.md) - Infrastructure setup

## Documentation

**For AI Assistants**:
- [START_HERE.md](START_HERE.md) - New session onboarding (read this first!)
- [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) - Mission, principles, decision framework
- [CURRENT_STATUS.md](CURRENT_STATUS.md) - What's done, what's next
- [AGENTS.md](AGENTS.md) - Coding conventions

**Architecture**:
- [docs/00_architecture.md](docs/00_architecture.md) - System architecture
- [docs/01_infrastructure.md](docs/01_infrastructure.md) - Infrastructure details
- [docs/02_development.md](docs/02_development.md) - Development guide

**Project History**:
- [DECISIONS.md](DECISIONS.md) - Why we made certain choices
- [LESSONS.md](LESSONS.md) - What we learned
- [logs/session_notes/](logs/session_notes/) - Daily work logs
