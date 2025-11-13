# Project Briefing: App2 - Project Coordinator Command Center (Phase 1)

## Context & Setup

I'm continuing work on my AI sandbox home lab project. This is a self-hosted AI development framework running on local infrastructure (Dell server with Ollama AI).

**Read for context first:**
- `CURRENT_STATUS.md` - Current project state
- `AGENTS.md` - Project conventions and patterns  
- `PROJECT_CONTEXT.md` - Mission and principles
- `streamlit_apps/app1/` - Example of framework patterns

## Mission: Build App2 - Project Tracking Intelligence

### The Use Case
I'm a public sector project coordinator who manages multiple projects simultaneously. I need an AI-powered project tracking system that helps me:

1. **Track project status** across multiple initiatives
2. **Monitor budgets** and predict overruns before they happen
3. **Manage timelines** with risk assessment and early warnings
4. **Process documents** automatically (contracts, reports, memos)
5. **Generate daily briefings** with AI analysis of what needs attention

### Key Requirements

**Security & Privacy:**
- All sensitive project data stays on local infrastructure
- Uses Ollama (local AI) to process confidential information
- No external API calls for sensitive data processing

**Technical Requirements:**
- Follow existing framework patterns from `streamlit_apps/shared/`
- Use PostgreSQL for data storage
- Pydantic models for type safety
- Progressive enhancement (works without AI, better with AI)
- Follow all conventions from `AGENTS.md`

## Phase 1 Scope (Start Here)

### Core Features to Build:
1. **Project CRUD Operations** - Add, edit, view, delete projects
2. **Basic Dashboard** - Overview of all projects with status
3. **Budget Tracking** - Input transactions, track spending vs. allocated
4. **Document Upload & AI Analysis** - Upload docs, get AI summaries
5. **Simple Daily Briefing** - AI-generated status report

### Database Schema Needed:

```sql
-- Core projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL, -- planning, active, on-hold, completed, cancelled
    budget_allocated DECIMAL(12,2),
    budget_spent DECIMAL(12,2) DEFAULT 0,
    start_date DATE,
    expected_end_date DATE,
    actual_end_date DATE,
    priority_level INTEGER CHECK (priority_level BETWEEN 1 AND 5),
    department VARCHAR(100),
    project_manager VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Budget transactions
CREATE TABLE budget_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    transaction_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    vendor VARCHAR(200),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Project documents
CREATE TABLE project_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    document_type VARCHAR(50), -- contract, report, memo, invoice, etc.
    file_path TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT NOW(),
    ai_summary TEXT,
    key_points JSONB
);
```

### Pydantic Models Needed:

```python
class Project(BaseModel):
    id: Optional[UUID] = None
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(regex="^(planning|active|on-hold|completed|cancelled)$")
    budget_allocated: Optional[Decimal] = Field(ge=0)
    budget_spent: Optional[Decimal] = Field(ge=0, default=0)
    start_date: Optional[date] = None
    expected_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    priority_level: Optional[int] = Field(ge=1, le=5)
    department: Optional[str] = Field(max_length=100)
    project_manager: Optional[str] = Field(max_length=100)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BudgetTransaction(BaseModel):
    id: Optional[UUID] = None
    project_id: UUID
    transaction_date: date
    amount: Decimal = Field(description="Positive for expenses, negative for refunds")
    category: Optional[str] = Field(max_length=100)
    vendor: Optional[str] = Field(max_length=200) 
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class DocumentAnalysis(BaseModel):
    summary: str = Field(description="3-4 sentence summary of document content")
    document_type: str = Field(description="contract, report, memo, invoice, etc.")
    key_points: List[str] = Field(description="3-5 most important points from document")
    action_items: List[str] = Field(description="Any action items or tasks mentioned")
    budget_impact: Optional[str] = Field(description="Any budget implications mentioned")
    deadlines: List[str] = Field(description="Any dates or deadlines mentioned")

class ProjectBriefing(BaseModel):
    urgent_items: List[str] = Field(description="Items needing immediate attention")
    budget_alerts: List[str] = Field(description="Budget concerns or variances")
    timeline_risks: List[str] = Field(description="Projects at risk of delay")
    upcoming_deadlines: List[str] = Field(description="Important dates in next 7 days")
    recommendations: List[str] = Field(description="Recommended actions for today")
```

### Streamlit App Structure:

**Create: `streamlit_apps/app2/`**
- `streamlit_main.py` - Main application file
- `environment.yml` - Dependencies (copy from app1 and modify)
- `README.md` - App documentation

**Pages/Tabs needed:**
1. **Dashboard** - Overview of all projects, key metrics
2. **Projects** - CRUD operations for projects
3. **Budget Tracking** - Add transactions, view spending
4. **Documents** - Upload and view documents with AI analysis  
5. **Daily Briefing** - AI-generated status summary

### Key Implementation Guidelines:

1. **Follow App1 Patterns:**
   - Use same import structure: `from shared.xxx import`
   - Use same error handling and progressive enhancement
   - Use same database session management
   - Follow same logging patterns

2. **AI Integration:**
   - Use `call_structured_llm()` for document analysis
   - Use `call_structured_llm()` for daily briefing generation
   - All AI calls must use Pydantic response models
   - Handle AI failures gracefully (app works without AI)

3. **Database Operations:**
   - Use SQLAlchemy with session management from `shared.db`
   - Add new models to `shared/models.py` or create new model file
   - Use transactions for multi-table operations
   - Include proper error handling

4. **File Handling:**
   - Store uploaded files in `uploads/app2/` directory
   - Use secure filename handling
   - Support common document types (PDF, DOC, TXT, etc.)
   - Extract text for AI analysis

5. **UI/UX Guidelines:**
   - Use Streamlit's native components
   - Responsive column layouts
   - Progress indicators for AI operations  
   - Clear success/error messaging
   - Consistent with app1 styling

## Success Criteria:

**MVP Definition (Phase 1 Complete):**
- [ ] Can add/edit/delete projects with all fields
- [ ] Dashboard shows project overview with status metrics
- [ ] Can add budget transactions and see spending vs. allocated
- [ ] Can upload documents and get AI-generated summaries
- [ ] Daily briefing tab generates AI analysis of project status
- [ ] All features work with mock AI provider
- [ ] Database schema properly implemented
- [ ] Follows all framework conventions from `AGENTS.md`

## Getting Started:

1. **Create the app2 directory structure** following app1 patterns
2. **Set up database models** in shared/models.py or new file
3. **Create database initialization** with schema creation
4. **Build basic CRUD operations** for projects
5. **Add Streamlit interface** with multiple tabs
6. **Implement AI document analysis** using existing patterns
7. **Test thoroughly** with both mock and real AI

## Files to Reference:

- `streamlit_apps/app1/streamlit_main.py` - UI patterns and structure
- `streamlit_apps/shared/` - All utility functions to reuse
- `AGENTS.md` - Coding conventions and requirements
- `PROJECT_CONTEXT.md` - Understanding the framework principles

## Questions to Consider:

1. Should project documents be stored in database or file system?
2. How should we handle file uploads securely?
3. What budget categories should we support?
4. How detailed should the daily briefing be?
5. Should we add project templates for common project types?

**Ready to start building!** Focus on getting the basic CRUD operations working first, then layer on the AI features. Remember: core functionality must work without AI, AI enhances the experience.