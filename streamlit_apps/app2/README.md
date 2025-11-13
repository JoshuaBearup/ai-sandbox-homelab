# App2 - Project Coordinator Command Center

**Status**: Phase 1 - Foundation In Progress

AI-powered project tracking system for managing multiple public sector projects.

## Features (Planned)

- Project CRUD operations with manual structured input
- Budget tracking with transaction history
- Dashboard with project metrics
- Document upload with AI analysis (future)
- Daily AI briefing generation (future)

## Current Status

**Foundation created:**
- Directory structure ✓
- Pydantic models added to shared/models.py ✓
- Requirements.txt ✓
- README ✓

**To Be Built:**
- Database schema in shared/db.py
- Streamlit application
- CRUD operations
- Dashboard

## Running

```bash
# From project root
dev.bat app2        # Windows
./dev.sh app2       # Mac/Linux
```

## Next Steps

See PROJECT_BRIEFING_APP2.md for complete requirements and implementation plan.

Continue building:
1. Add database models to shared/db.py
2. Create streamlit_main.py
3. Implement Projects CRUD
4. Add Budget tracking
5. Build Dashboard

## Architecture

Follows same patterns as app1:
- Manual structured input (forms, dropdowns)
- Type-safe Pydantic models
- PostgreSQL storage
- Progressive enhancement (AI features added later)
