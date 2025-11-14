"""
Project Coordinator Command Center - App2

AI-powered project management system for public sector coordinators.

Features:
- Multi-project tracking with status and timeline management
- Budget tracking with variance alerts
- Document upload with AI-powered analysis
- Daily briefing with AI recommendations
- Progressive enhancement (works without AI)

This app demonstrates:
1. Complex database operations with relationships
2. File upload and processing
3. Advanced AI integration for analysis
4. Real-world workflow automation
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
from typing import Optional
import uuid
import os
import io

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import get_config
from shared.db import (
    init_database, get_session, test_connection,
    ProjectDB, BudgetTransactionDB, ProjectDocumentDB
)
from shared.ai import get_ai_client, call_structured_llm, test_ai_connection
from shared.models import DocumentAnalysis, ProjectBriefing, ProjectStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Project Coordinator Command Center",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Upload directory
UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads" / "app2"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def show_dashboard():
    """Display project overview dashboard."""
    st.header("📊 Project Dashboard")
    
    try:
        with get_session() as session:
            # Get all projects
            projects = session.query(ProjectDB).all()
            
            if not projects:
                st.info("No projects yet. Go to the 'Projects' tab to add your first project!")
                return
            
            # Overview metrics
            st.subheader("Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            active_projects = [p for p in projects if p.status == "active"]
            completed_projects = [p for p in projects if p.status == "completed"]
            total_budget = sum([p.budget_allocated or 0 for p in projects])
            total_spent = sum([p.budget_spent or 0 for p in projects])
            
            with col1:
                st.metric("Total Projects", len(projects))
            with col2:
                st.metric("Active Projects", len(active_projects))
            with col3:
                st.metric("Total Budget", f"${total_budget:,.2f}")
            with col4:
                budget_used_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0
                st.metric("Budget Used", f"{budget_used_pct:.1f}%")
            
            # Projects by status
            st.subheader("Projects by Status")
            status_counts = {}
            for p in projects:
                status_counts[p.status] = status_counts.get(p.status, 0) + 1
            
            col1, col2 = st.columns([1, 2])
            with col1:
                for status, count in status_counts.items():
                    st.metric(status.replace("-", " ").title(), count)
            
            # Recent projects
            st.subheader("Recent Projects")
            recent_projects = sorted(projects, key=lambda p: p.updated_at, reverse=True)[:5]
            
            for proj in recent_projects:
                with st.expander(f"📁 {proj.name} - {proj.status.upper()}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Department:** {proj.department or 'N/A'}")
                        st.markdown(f"**Manager:** {proj.project_manager or 'N/A'}")
                        st.markdown(f"**Priority:** {proj.priority_level or 'N/A'}")
                    
                    with col2:
                        if proj.budget_allocated:
                            spent_pct = (proj.budget_spent / proj.budget_allocated * 100) if proj.budget_allocated > 0 else 0
                            st.markdown(f"**Budget:** ${proj.budget_allocated:,.2f}")
                            st.markdown(f"**Spent:** ${proj.budget_spent:,.2f} ({spent_pct:.1f}%)")
                        
                        if proj.expected_end_date:
                            st.markdown(f"**Due:** {proj.expected_end_date}")
                    
                    if proj.description:
                        st.markdown(f"**Description:** {proj.description}")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        logger.error(f"Dashboard error: {e}")


def show_projects():
    """Manage projects - CRUD operations."""
    st.header("📁 Projects")
    
    # Initialize session state for tab selection
    if 'active_project_tab' not in st.session_state:
        st.session_state.active_project_tab = 0
    
    # Check if we should show success message
    if 'project_created' in st.session_state and st.session_state.project_created:
        st.success(f"✅ Project '{st.session_state.project_name}' created successfully!")
        st.session_state.project_created = False
        st.session_state.active_project_tab = 0  # Switch to View Projects tab
    
    tab1, tab2 = st.tabs(["View Projects", "Add/Edit Project"])
    
    with tab1:
        show_project_list()
    
    with tab2:
        show_project_form()


def show_project_list():
    """Display list of all projects with actions."""
    try:
        with get_session() as session:
            projects = session.query(ProjectDB).order_by(ProjectDB.updated_at.desc()).all()
            
            if not projects:
                st.info("No projects yet. Use the 'Add/Edit Project' tab to create one!")
                return
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_status = st.selectbox(
                    "Filter by Status",
                    ["All"] + [s.value for s in ProjectStatus]
                )
            with col2:
                filter_dept = st.selectbox(
                    "Filter by Department",
                    ["All"] + list(set([p.department for p in projects if p.department]))
                )
            
            # Apply filters
            filtered = projects
            if filter_status != "All":
                filtered = [p for p in filtered if p.status == filter_status]
            if filter_dept != "All":
                filtered = [p for p in filtered if p.department == filter_dept]
            
            st.markdown(f"**Showing {len(filtered)} of {len(projects)} projects**")
            
            # Display projects
            for proj in filtered:
                with st.expander(f"📁 {proj.name} - {proj.status.upper()}", expanded=False):
                    # === HEADER WITH ACTIONS ===
                    col_main, col_action = st.columns([5, 1])
                    
                    with col_action:
                        if st.button(f"🗑️ Delete", key=f"del_{proj.id}", type="secondary", use_container_width=True):
                            if delete_project(proj.id):
                                st.success("Project deleted!")
                                st.rerun()
                            else:
                                st.error("Delete failed")
                    
                    with col_main:
                        # Basic metadata
                        meta_col1, meta_col2, meta_col3 = st.columns(3)
                        with meta_col1:
                            st.markdown(f"**Department:** {proj.department or 'N/A'}")
                            st.markdown(f"**Manager:** {proj.project_manager or 'N/A'}")
                        with meta_col2:
                            if proj.start_date:
                                st.markdown(f"**Start:** {proj.start_date}")
                            if proj.expected_end_date:
                                st.markdown(f"**Due:** {proj.expected_end_date}")
                        with meta_col3:
                            priority_emoji = "🔥" * proj.priority_level if proj.priority_level else ""
                            st.markdown(f"**Priority:** {priority_emoji} ({proj.priority_level or 'N/A'})")
                        
                        # Budget summary
                        if proj.budget_allocated:
                            spent_pct = float(proj.budget_spent / proj.budget_allocated * 100) if proj.budget_allocated > 0 else 0.0
                            st.progress(float(spent_pct / 100))
                            st.markdown(f"💰 **Budget:** ${proj.budget_allocated:,.2f} | **Spent:** ${proj.budget_spent:,.2f} ({spent_pct:.1f}%)")
                    
                    st.markdown("---")
                    
                    # === STRUCTURED DATA SECTIONS ===
                    if proj.structured_data:
                        data = proj.structured_data
                        
                        # Objectives & Context
                        if data.get("objectives") or proj.description:
                            with st.container():
                                st.markdown("#### 🎯 Objectives & Context")
                                if proj.description:
                                    st.markdown(f"**Background:** {proj.description}")
                                if data.get("objectives"):
                                    st.markdown("**Key Objectives:**")
                                    st.markdown(data["objectives"])
                                if data.get("success_criteria"):
                                    st.markdown("**Success Criteria:**")
                                    st.markdown(data["success_criteria"])
                        
                        # Stakeholders
                        if data.get("stakeholders"):
                            with st.container():
                                st.markdown("#### 👥 Stakeholders")
                                st.markdown(data["stakeholders"])
                        
                        # Timeline & Milestones
                        if data.get("milestones"):
                            with st.container():
                                st.markdown("#### 📅 Key Milestones")
                                st.markdown(data["milestones"])
                        
                        # Budget Details
                        if data.get("budget_breakdown") or data.get("funding_source"):
                            with st.container():
                                st.markdown("#### 💰 Budget Details")
                                if data.get("funding_source"):
                                    st.markdown(f"**Funding Source:** {data['funding_source']}")
                                if data.get("budget_breakdown"):
                                    st.markdown("**Breakdown:**")
                                    st.markdown(data["budget_breakdown"])
                        
                        # Risks & Dependencies
                        if data.get("risks") or data.get("dependencies"):
                            with st.container():
                                st.markdown("#### ⚠️ Risks & Dependencies")
                                
                                # Display structured risks
                                if data.get("risks") and isinstance(data["risks"], list):
                                    st.markdown("**Risk Register:**")
                                    for risk in data["risks"]:
                                        risk_color = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
                                        likelihood_icon = risk_color.get(risk.get("likelihood", "medium"), "⚪")
                                        impact_icon = risk_color.get(risk.get("impact", "medium"), "⚪")
                                        
                                        with st.expander(f"{risk.get('id', 'N/A')}: {risk.get('description', 'No description')[:60]}..."):
                                            col1, col2 = st.columns(2)
                                            with col1:
                                                st.markdown(f"**Likelihood:** {likelihood_icon} {risk.get('likelihood', 'N/A').upper()}")
                                                st.markdown(f"**Impact:** {impact_icon} {risk.get('impact', 'N/A').upper()}")
                                                st.markdown(f"**Status:** {risk.get('status', 'identified').upper()}")
                                            with col2:
                                                st.markdown(f"**Owner:** {risk.get('owner', 'Unassigned')}")
                                                if risk.get('review_date'):
                                                    st.markdown(f"**Review Date:** {risk['review_date']}")
                                            
                                            st.markdown("**Description:**")
                                            st.markdown(risk.get('description', 'No description'))
                                            st.markdown("**Mitigation Strategy:**")
                                            st.markdown(risk.get('mitigation', 'No mitigation defined'))
                                
                                # Fallback for old text-based risks
                                elif data.get("risks") and isinstance(data["risks"], str):
                                    st.markdown("**Risks & Mitigation:**")
                                    st.markdown(data["risks"])
                                
                                # Dependencies
                                if data.get("dependencies"):
                                    st.markdown("**Dependencies & Constraints:**")
                                    st.markdown(data["dependencies"])
                        
                        # Activities
                        if data.get("activities"):
                            with st.container():
                                st.markdown("#### ✅ Key Activities")
                                st.markdown(data["activities"])
                        
                        # Additional Notes
                        if data.get("notes"):
                            with st.container():
                                st.markdown("#### 📝 Additional Notes")
                                st.markdown(data["notes"])
                    
                    else:
                        # Legacy projects without structured data
                        if proj.description:
                            st.markdown(f"**Description:** {proj.description}")
    
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        logger.error(f"Project list error: {e}")


def show_project_form():
    """Comprehensive structured form to capture all project context."""
    st.subheader("📋 New Project - Structured Intake Form")
    st.markdown("*Complete this form to ensure all critical project aspects are documented.*")
    
    # Quick test project button
    col_test, col_spacer = st.columns([1, 3])
    with col_test:
        if st.button("🧪 Create Test Project", type="secondary", help="Quickly create a sample project with all fields populated"):
            test_project_data = {
                "name": "Downtown Revitalization Initiative - Test",
                "description": "Major urban renewal project to revitalize the downtown core. This initiative responds to declining foot traffic, aging infrastructure, and community feedback requesting improved public spaces. The project aims to transform Main Street into a vibrant, pedestrian-friendly corridor that supports local businesses and enhances quality of life.",
                "status": "planning",
                "department": "Public Works & Development",
                "project_manager": "Sarah Johnson",
                "priority_level": 4,
                "budget_allocated": Decimal("250000.00"),
                "start_date": date(2025, 1, 15),
                "expected_end_date": date(2025, 12, 15),
                "structured_data": {
                    "objectives": """• Increase pedestrian foot traffic by 30%
• Improve safety with better lighting and crosswalks
• Support local businesses through streetscape improvements
• Create welcoming public gathering spaces
• Upgrade aging infrastructure (water, sewer, utilities)""",
                    "success_criteria": """• 30% increase in pedestrian counts (baseline vs. 6 months post-completion)
• Zero serious pedestrian incidents in project area
• 20% increase in business revenue (survey-based)
• 80% positive community satisfaction rating
• Complete within $250K budget (±5%)
• No critical infrastructure failures in first year""",
                    "stakeholders": """• City Council (Approval authority, budget allocation)
• Downtown Business Association (Primary beneficiary, input on design)
• Public Works Department (Implementation, maintenance)
• Planning Department (Zoning, permits, compliance)
• Local Community Groups (Consultation, feedback)
• Emergency Services (Access requirements during construction)
• Utilities Companies (Coordination on underground work)""",
                    "milestones": """• Q1 2025: Complete community consultation and design finalization
• March 2025: Secure City Council approval and funding
• Q2 2025: Tender and award construction contracts
• May-June 2025: Phase 1 - Utility upgrades
• July-Sept 2025: Phase 2 - Streetscape construction
• Oct 2025: Phase 3 - Finishing touches (lighting, furniture, landscaping)
• Nov 2025: Grand opening event
• Dec 2025: Post-completion evaluation""",
                    "budget_breakdown": """• Design & Engineering: $30,000
• Construction Management: $20,000
• Streetscape Materials: $80,000
• Lighting & Electrical: $35,000
• Underground Utilities: $40,000
• Landscaping & Trees: $25,000
• Contingency (10%): $20,000
Total: $250,000""",
                    "funding_source": "Capital Budget (60%) + Provincial Infrastructure Grant (40%)",
                    "risks": [
                        {
                            "id": "R001",
                            "description": "Weather delays could impact construction schedule, particularly in fall/winter months",
                            "likelihood": "high",
                            "impact": "medium",
                            "mitigation": "Built 3-week buffer into schedule; flexible phase timing to work around weather windows",
                            "owner": "Sarah Johnson",
                            "status": "mitigating",
                            "identified_date": "2025-01-10",
                            "review_date": "2025-03-01"
                        },
                        {
                            "id": "R002",
                            "description": "Budget overruns due to unforeseen site conditions or material cost increases",
                            "likelihood": "medium",
                            "impact": "high",
                            "mitigation": "10% contingency allocated; value engineering options identified; monthly budget reviews",
                            "owner": "Finance Manager",
                            "status": "monitoring",
                            "identified_date": "2025-01-10",
                            "review_date": "2025-02-15"
                        },
                        {
                            "id": "R003",
                            "description": "Stakeholder opposition from business owners concerned about construction disruption",
                            "likelihood": "medium",
                            "impact": "critical",
                            "mitigation": "Early and ongoing consultation; design incorporates community feedback; business support fund allocated",
                            "owner": "Community Liaison",
                            "status": "mitigating",
                            "identified_date": "2025-01-08",
                            "review_date": "2025-02-01"
                        },
                        {
                            "id": "R004",
                            "description": "Utility conflicts discovered during excavation causing delays and cost increases",
                            "likelihood": "low",
                            "impact": "high",
                            "mitigation": "Pre-construction GPR survey completed; coordinated with utility companies; as-built drawings reviewed",
                            "owner": "Engineering Lead",
                            "status": "monitoring",
                            "identified_date": "2025-01-12",
                            "review_date": "2025-04-01"
                        }
                    ],
                    "dependencies": """• Requires City Council approval (March 2025 meeting)
• Must coordinate with Water Department trunk main replacement (May 2025)
• Provincial grant funding confirmation needed by Feb 2025
• Construction restricted to May-October due to weather
• Business consultation required before finalizing traffic management plan
• Emergency vehicle access must be maintained throughout construction""",
                    "activities": """• Community Consultation & Engagement
• Detailed Design & Engineering
• Permitting & Regulatory Approvals
• Procurement & Contract Management
• Phase 1: Underground Utility Work
• Phase 2: Surface Construction (pavement, sidewalks)
• Phase 3: Amenities Installation (lighting, furniture, landscaping)
• Traffic Management & Business Liaison
• Quality Assurance & Inspections
• Post-Construction Monitoring & Evaluation""",
                    "notes": "This is a flagship project for the municipality with high visibility and political importance. Strong community support exists but requires careful management of business concerns during construction. Coordination with upcoming water main replacement project is critical - failure to align could result in tearing up new pavement. Consider public art component if budget allows."
                }
            }
            
            if create_project(**test_project_data):
                st.success("✅ Test project created successfully!")
                st.session_state.project_created = True
                st.session_state.project_name = test_project_data["name"]
                st.rerun()
            else:
                st.error("Failed to create test project")
    
    # === RISK MANAGEMENT (OUTSIDE FORM) ===
    st.markdown("---")
    st.markdown("### ⚠️ Risk Register")
    st.caption("Track and manage project risks with structured risk register")
    
    # Initialize risks in session state
    if "project_risks" not in st.session_state:
        st.session_state.project_risks = []
    
    # Display existing risks
    if st.session_state.project_risks:
        st.markdown("**Current Risks:**")
        for idx, risk in enumerate(st.session_state.project_risks):
            with st.expander(f"🔴 {risk['id']}: {risk['description'][:50]}...", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**Likelihood:** {risk['likelihood']}")
                    st.markdown(f"**Impact:** {risk['impact']}")
                    st.markdown(f"**Status:** {risk['status']}")
                with col2:
                    st.markdown(f"**Owner:** {risk.get('owner', 'Unassigned')}")
                    if risk.get('review_date'):
                        st.markdown(f"**Review Date:** {risk['review_date']}")
                with col3:
                    if st.button("🗑️", key=f"del_risk_{idx}"):
                        st.session_state.project_risks.pop(idx)
                        st.rerun()
                
                st.markdown(f"**Description:** {risk['description']}")
                st.markdown(f"**Mitigation:** {risk['mitigation']}")
    
    # Add new risk form
    with st.expander("➕ Add New Risk", expanded=len(st.session_state.project_risks) == 0):
        risk_id = st.text_input("Risk ID*", placeholder="R001", key="risk_id")
        risk_desc = st.text_area("Risk Description*", placeholder="Describe the risk...", key="risk_desc", height=80)
        
        col1, col2 = st.columns(2)
        with col1:
            risk_likelihood = st.selectbox("Likelihood*", ["low", "medium", "high", "critical"], key="risk_likelihood")
            risk_impact = st.selectbox("Impact*", ["low", "medium", "high", "critical"], key="risk_impact")
        with col2:
            risk_owner = st.text_input("Owner", placeholder="John Doe", key="risk_owner")
            risk_status = st.selectbox("Status*", ["identified", "mitigating", "monitoring", "closed"], key="risk_status")
        
        risk_mitigation = st.text_area("Mitigation Strategy*", placeholder="How will you manage this risk?", key="risk_mitigation", height=80)
        
        col3, col4 = st.columns(2)
        with col3:
            risk_identified = st.date_input("Identified Date", value=None, key="risk_identified")
        with col4:
            risk_review = st.date_input("Review Date", value=None, key="risk_review")
        
        if st.button("✅ Add Risk", type="primary"):
            if risk_id and risk_desc and risk_mitigation:
                new_risk = {
                    "id": risk_id,
                    "description": risk_desc,
                    "likelihood": risk_likelihood,
                    "impact": risk_impact,
                    "mitigation": risk_mitigation,
                    "owner": risk_owner or None,
                    "status": risk_status,
                    "identified_date": str(risk_identified) if risk_identified else None,
                    "review_date": str(risk_review) if risk_review else None
                }
                st.session_state.project_risks.append(new_risk)
                st.success(f"✅ Risk {risk_id} added!")
                st.rerun()
            else:
                st.error("Please fill in all required fields (Risk ID, Description, Mitigation)")
    
    st.markdown("---")
    
    # === MAIN PROJECT FORM ===
    with st.form("project_form"):
        # === BASIC INFO ===
        st.markdown("### 🎯 Basic Information")
        name = st.text_input("Project Name*", placeholder="Downtown Revitalization Initiative")
        
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox("Current Status*", [s.value for s in ProjectStatus])
            department = st.text_input("Department/Division", placeholder="Public Works")
        with col2:
            priority = st.slider("Priority Level (1=Low, 5=Critical)", 1, 5, 3)
            project_manager = st.text_input("Project Manager", placeholder="John Doe")
        
        st.markdown("---")
        
        # === OBJECTIVES & CONTEXT ===
        st.markdown("### 🎪 Objectives & Context")
        st.caption("What are you trying to achieve and why does it matter?")
        
        description = st.text_area(
            "Project Description & Background*",
            placeholder="Provide high-level overview, context, and why this project is needed...",
            help="Explain the problem, opportunity, or mandate driving this project",
            height=100
        )
        
        objectives = st.text_area(
            "Key Objectives",
            placeholder="• Objective 1: Improve pedestrian safety\n• Objective 2: Increase economic activity\n• Objective 3: Enhance community engagement",
            help="List specific, measurable objectives (one per line)",
            height=100
        )
        
        success_criteria = st.text_area(
            "Success Criteria",
            placeholder="• Reduce incidents by 30%\n• Increase foot traffic by 20%\n• Complete within budget",
            help="How will you measure success? What are the key metrics?",
            height=80
        )
        
        st.markdown("---")
        
        # === STAKEHOLDERS ===
        st.markdown("### 👥 Stakeholders & Participants")
        st.caption("Who needs to be involved or informed?")
        
        stakeholders = st.text_area(
            "Key Stakeholders",
            placeholder="• City Council (Decision maker)\n• Local Business Association (Affected party)\n• Engineering Team (Implementation)\n• Community Groups (Consulted)",
            help="List stakeholders with their role/interest",
            height=100
        )
        
        st.markdown("---")
        
        # === TIMELINE & MILESTONES ===
        st.markdown("### 📅 Timeline & Milestones")
        st.caption("Key dates and major checkpoints")
        
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("Start Date", value=None)
        with col4:
            expected_end_date = st.date_input("Expected Completion Date", value=None)
        
        milestones = st.text_area(
            "Key Milestones",
            placeholder="• Q1 2025: Complete planning phase\n• Q2 2025: Secure approvals\n• Q3 2025: Begin implementation\n• Q4 2025: Launch and evaluation",
            help="List major milestones with target dates",
            height=100
        )
        
        st.markdown("---")
        
        # === BUDGET ===
        st.markdown("### 💰 Budget & Resources")
        
        col5, col6 = st.columns(2)
        with col5:
            budget_allocated = st.number_input("Total Budget Allocated ($)", min_value=0.0, step=1000.0, format="%.2f")
        with col6:
            funding_source = st.text_input("Funding Source", placeholder="Capital Budget, Grant, etc.")
        
        budget_breakdown = st.text_area(
            "Budget Breakdown (Optional)",
            placeholder="• Personnel: $50,000\n• Materials: $30,000\n• Contractors: $100,000\n• Contingency: $20,000",
            help="Break down budget by category if known",
            height=80
        )
        
        st.markdown("---")
        
        # === RISKS & DEPENDENCIES ===
        st.markdown("### ⚠️ Dependencies & Constraints")
        st.caption("Note: Risks are managed in the separate Risk Register section above")
        
        # Dependencies (keep as text for now)
        dependencies = st.text_area(
            "Dependencies & Constraints",
            placeholder="• Requires approval from City Council\n• Must coordinate with Water Department project\n• Construction only during summer months",
            help="What needs to happen first? What are the constraints?",
            height=80
        )
        
        st.markdown("---")
        
        # === ACTIVITIES & TASKS ===
        st.markdown("### ✅ Key Activities & Work Streams")
        st.caption("Major work packages or task categories")
        
        activities = st.text_area(
            "Key Activities",
            placeholder="• Planning & Design\n• Stakeholder Consultation\n• Permitting & Approvals\n• Procurement\n• Implementation\n• Monitoring & Evaluation",
            help="List major work streams or phases",
            height=100
        )
        
        st.markdown("---")
        
        # === NOTES ===
        st.markdown("### 📝 Additional Notes")
        
        notes = st.text_area(
            "Additional Context (Optional)",
            placeholder="Any other relevant information, history, or context...",
            height=80
        )
        
        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button("✅ Create Project", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not name:
                st.error("❌ Project name is required!")
                return
            if not description:
                st.error("❌ Project description is required! Please provide context for this project.")
                return
            
            # Prepare structured data
            structured_data = {
                "objectives": objectives or None,
                "success_criteria": success_criteria or None,
                "stakeholders": stakeholders or None,
                "milestones": milestones or None,
                "budget_breakdown": budget_breakdown or None,
                "funding_source": funding_source or None,
                "risks": st.session_state.project_risks if st.session_state.project_risks else None,  # Structured risks
                "dependencies": dependencies or None,
                "activities": activities or None,
                "notes": notes or None
            }
            
            if create_project(
                name=name,
                description=description,
                status=status,
                department=department or None,
                project_manager=project_manager or None,
                priority_level=priority,
                budget_allocated=Decimal(str(budget_allocated)) if budget_allocated > 0 else None,
                start_date=start_date,
                expected_end_date=expected_end_date,
                structured_data=structured_data
            ):
                # Clear risks from session state
                st.session_state.project_risks = []
                # Set session state to show success message
                st.session_state.project_created = True
                st.session_state.project_name = name
                st.rerun()
            else:
                st.error("❌ Failed to create project. Check logs for details.")


def create_project(**kwargs) -> bool:
    """Create a new project in database."""
    try:
        with get_session() as session:
            project = ProjectDB(**kwargs)
            session.add(project)
            session.commit()
            logger.info(f"Created project: {kwargs.get('name')}")
            return True
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        return False


def delete_project(project_id: uuid.UUID) -> bool:
    """Delete a project from database."""
    try:
        with get_session() as session:
            project = session.query(ProjectDB).filter(ProjectDB.id == project_id).first()
            if project:
                session.delete(project)
                session.commit()
                logger.info(f"Deleted project: {project_id}")
                return True
            return False
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        return False


def show_budget_tracking():
    """Budget tracking and transaction management."""
    st.header("💰 Budget Tracking")
    
    # Select project
    try:
        with get_session() as session:
            projects = session.query(ProjectDB).order_by(ProjectDB.name).all()
            
            if not projects:
                st.info("No projects yet. Create a project first!")
                return
            
            project_options = {f"{p.name}": p.id for p in projects}
            selected_name = st.selectbox("Select Project", list(project_options.keys()))
            selected_id = project_options[selected_name]
            
            # Get selected project fresh in this session
            project = session.query(ProjectDB).filter(ProjectDB.id == selected_id).first()
            
            if not project:
                st.error("Project not found")
                return
            
            # Budget overview
            st.subheader("Budget Overview")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Allocated", f"${project.budget_allocated or 0:,.2f}")
            with col2:
                st.metric("Spent", f"${project.budget_spent or 0:,.2f}")
            with col3:
                remaining = (project.budget_allocated or 0) - (project.budget_spent or 0)
                st.metric("Remaining", f"${remaining:,.2f}")
            
            if project.budget_allocated and project.budget_allocated > 0:
                spent_pct = float(project.budget_spent / project.budget_allocated * 100)
                st.progress(min(float(spent_pct / 100), 1.0))
                st.caption(f"{spent_pct:.1f}% of budget used")
            
            # Add transaction
            st.subheader("Add Transaction")
            with st.form("transaction_form"):
                col1, col2 = st.columns(2)
                with col1:
                    trans_date = st.date_input("Date", value=date.today())
                    amount = st.number_input("Amount ($)", step=100.0, format="%.2f")
                with col2:
                    category = st.text_input("Category", placeholder="Equipment, Labor, Materials...")
                    vendor = st.text_input("Vendor", placeholder="Company name")
                
                description = st.text_area("Description", placeholder="Transaction details...")
                
                submitted = st.form_submit_button("Add Transaction", type="primary")
                
                if submitted:
                    if amount == 0:
                        st.error("Amount cannot be zero")
                    else:
                        if add_transaction(
                            project_id=selected_id,
                            transaction_date=trans_date,
                            amount=Decimal(str(amount)),
                            category=category or None,
                            vendor=vendor or None,
                            description=description or None,
                        ):
                            st.success("Transaction added!")
                            st.rerun()
                        else:
                            st.error("Failed to add transaction")
            
            # Transaction history
            st.subheader("Transaction History")
            transactions = session.query(BudgetTransactionDB)\
                .filter(BudgetTransactionDB.project_id == selected_id)\
                .order_by(BudgetTransactionDB.transaction_date.desc())\
                .all()
            
            if not transactions:
                st.info("No transactions yet for this project.")
            else:
                for trans in transactions:
                    with st.expander(f"{trans.transaction_date} - ${trans.amount:,.2f} - {trans.category or 'Uncategorized'}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Amount:** ${trans.amount:,.2f}")
                            st.markdown(f"**Category:** {trans.category or 'N/A'}")
                        with col2:
                            st.markdown(f"**Vendor:** {trans.vendor or 'N/A'}")
                            st.markdown(f"**Date:** {trans.transaction_date}")
                        
                        if trans.description:
                            st.markdown(f"**Description:** {trans.description}")
    
    except Exception as e:
        st.error(f"Error in budget tracking: {e}")
        logger.error(f"Budget tracking error: {e}")


def add_transaction(**kwargs) -> bool:
    """Add a budget transaction and update project budget_spent."""
    try:
        with get_session() as session:
            # Create transaction
            transaction = BudgetTransactionDB(**kwargs)
            session.add(transaction)
            
            # Update project budget_spent
            project = session.query(ProjectDB).filter(ProjectDB.id == kwargs['project_id']).first()
            if project:
                project.budget_spent = (project.budget_spent or 0) + kwargs['amount']
                project.updated_at = datetime.utcnow()
            
            session.commit()
            logger.info(f"Added transaction: {kwargs.get('amount')}")
            return True
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        return False


def show_documents():
    """Document upload and AI analysis."""
    st.header("📄 Documents")
    
    config = get_config()
    
    st.markdown("""
    Upload project documents and get AI-powered analysis:
    - Automatic summary generation
    - Key points extraction
    - Action item identification
    - Budget impact analysis
    """)
    
    # Select project
    try:
        with get_session() as session:
            projects = session.query(ProjectDB).order_by(ProjectDB.name).all()
            
            if not projects:
                st.info("No projects yet. Create a project first!")
                return
            
            project_options = {f"{p.name}": p.id for p in projects}
            selected_name = st.selectbox("Select Project", list(project_options.keys()))
            selected_id = project_options[selected_name]
            
            # Upload section
            st.subheader("Upload Document")
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["txt", "pdf", "doc", "docx"],
                help="Supported formats: TXT, PDF, DOC, DOCX"
            )
            
            if uploaded_file:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.info(f"**File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)")
                with col2:
                    if st.button("Process Document", type="primary"):
                        process_document(uploaded_file, selected_id)
                        st.rerun()
            
            # Documents list
            st.subheader("Project Documents")
            documents = session.query(ProjectDocumentDB)\
                .filter(ProjectDocumentDB.project_id == selected_id)\
                .order_by(ProjectDocumentDB.upload_date.desc())\
                .all()
            
            if not documents:
                st.info("No documents uploaded yet for this project.")
            else:
                for doc in documents:
                    with st.expander(f"📄 {doc.filename} - {doc.upload_date.strftime('%Y-%m-%d')}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Type:** {doc.document_type or 'Unknown'}")
                            st.markdown(f"**Uploaded:** {doc.upload_date.strftime('%Y-%m-%d %H:%M')}")
                            
                            if doc.ai_summary:
                                st.markdown("**AI Summary:**")
                                st.info(doc.ai_summary)
                            
                            if doc.key_points:
                                st.markdown("**Key Points:**")
                                for point in doc.key_points:
                                    st.markdown(f"- {point}")
                        
                        with col2:
                            if st.button("Delete", key=f"del_doc_{doc.id}"):
                                delete_document(doc.id, doc.file_path)
                                st.rerun()
    
    except Exception as e:
        st.error(f"Error managing documents: {e}")
        logger.error(f"Documents error: {e}")


def process_document(uploaded_file, project_id: uuid.UUID):
    """Process uploaded document with AI analysis."""
    try:
        # Save file
        file_id = uuid.uuid4()
        file_ext = uploaded_file.name.split('.')[-1]
        safe_filename = f"{file_id}.{file_ext}"
        file_path = UPLOAD_DIR / safe_filename
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract text (simplified - just read if TXT)
        text_content = ""
        if file_ext == "txt":
            text_content = uploaded_file.getvalue().decode("utf-8")
        else:
            text_content = f"[{file_ext.upper()} file - text extraction not implemented yet]"
        
        # AI Analysis (progressive enhancement)
        ai_summary = None
        key_points = None
        doc_type = None
        
        client = get_ai_client()
        if client and text_content:
            with st.spinner("Analyzing document with AI..."):
                response, call_id = call_structured_llm(
                    client=client,
                    response_model=DocumentAnalysis,
                    user_prompt=f"Analyze this document:\n\n{text_content[:2000]}",  # Limit text size
                    system_prompt="You are a document analysis expert. Extract key information, identify document type, and summarize.",
                )
                
                if response:
                    ai_summary = response.summary
                    key_points = response.key_points
                    doc_type = response.document_type
                    st.success("AI analysis complete!")
                else:
                    st.warning("AI analysis unavailable, but document saved.")
        
        # Save to database
        with get_session() as session:
            document = ProjectDocumentDB(
                project_id=project_id,
                filename=uploaded_file.name,
                document_type=doc_type,
                file_path=str(file_path),
                ai_summary=ai_summary,
                key_points=key_points,
            )
            session.add(document)
            session.commit()
        
        st.success(f"Document '{uploaded_file.name}' uploaded successfully!")
    
    except Exception as e:
        st.error(f"Failed to process document: {e}")
        logger.error(f"Document processing error: {e}")


def delete_document(doc_id: uuid.UUID, file_path: str):
    """Delete document from database and filesystem."""
    try:
        # Delete file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        with get_session() as session:
            doc = session.query(ProjectDocumentDB).filter(ProjectDocumentDB.id == doc_id).first()
            if doc:
                session.delete(doc)
                session.commit()
                logger.info(f"Deleted document: {doc_id}")
    
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")


def show_daily_briefing():
    """Generate AI-powered daily briefing."""
    st.header("📋 Daily Briefing")
    
    st.markdown(f"**Date:** {date.today().strftime('%A, %B %d, %Y')}")
    
    try:
        with get_session() as session:
            projects = session.query(ProjectDB).all()
            
            if not projects:
                st.info("No projects yet. Create some projects to get a daily briefing!")
                return
            
            # Manual briefing (always works)
            st.subheader("Quick Summary")
            
            active_count = len([p for p in projects if p.status == "active"])
            overbudget = [p for p in projects if p.budget_allocated and p.budget_spent and p.budget_spent > p.budget_allocated]
            upcoming_deadlines = [p for p in projects if p.expected_end_date and p.expected_end_date <= date.today() + timedelta(days=7)]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Active Projects", active_count)
            with col2:
                st.metric("Over Budget", len(overbudget), delta="Alert" if overbudget else None, delta_color="inverse" if overbudget else "off")
            with col3:
                st.metric("Upcoming Deadlines", len(upcoming_deadlines))
            
            # AI Briefing (enhancement)
            client = get_ai_client()
            if client:
                if st.button("Generate AI Briefing", type="primary"):
                    with st.spinner("Analyzing all projects..."):
                        # Prepare project summary
                        project_summary = []
                        for p in projects:
                            summary = f"Project: {p.name}, Status: {p.status}"
                            if p.budget_allocated:
                                spent_pct = (p.budget_spent / p.budget_allocated * 100) if p.budget_allocated > 0 else 0
                                summary += f", Budget: ${p.budget_allocated:,.0f} ({spent_pct:.0f}% spent)"
                            if p.expected_end_date:
                                days_until = (p.expected_end_date - date.today()).days
                                summary += f", Due in {days_until} days"
                            project_summary.append(summary)
                        
                        prompt = "Generate a daily briefing for a project coordinator based on these projects:\n\n"
                        prompt += "\n".join(project_summary[:20])  # Limit to prevent token overflow
                        
                        response, call_id = call_structured_llm(
                            client=client,
                            response_model=ProjectBriefing,
                            user_prompt=prompt,
                            system_prompt="You are an AI assistant for project coordinators. Analyze the projects and provide actionable insights.",
                        )
                        
                        if response:
                            st.success("AI Briefing Generated!")
                            
                            if response.urgent_items:
                                st.subheader("🚨 Urgent Items")
                                for item in response.urgent_items:
                                    st.error(f"• {item}")
                            
                            if response.budget_alerts:
                                st.subheader("💰 Budget Alerts")
                                for alert in response.budget_alerts:
                                    st.warning(f"• {alert}")
                            
                            if response.timeline_risks:
                                st.subheader("⏰ Timeline Risks")
                                for risk in response.timeline_risks:
                                    st.warning(f"• {risk}")
                            
                            if response.upcoming_deadlines:
                                st.subheader("📅 Upcoming Deadlines")
                                for deadline in response.upcoming_deadlines:
                                    st.info(f"• {deadline}")
                            
                            if response.recommendations:
                                st.subheader("💡 Recommendations")
                                for rec in response.recommendations:
                                    st.success(f"• {rec}")
                        else:
                            st.error("AI briefing generation failed. See manual summary above.")
            else:
                st.info("AI provider not configured. Using manual summary only.")
    
    except Exception as e:
        st.error(f"Error generating briefing: {e}")
        logger.error(f"Briefing error: {e}")


def show_system_status():
    """Display system status (from app1 pattern)."""
    st.header("⚙️ System Status")
    
    config = get_config()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Environment", config.environment.upper())
        st.metric("AI Provider", config.ai_provider.upper())
    
    with col2:
        st.metric("AI Model", config.ai_model)
        st.metric("Log Level", config.log_level)
    
    with col3:
        db_status = test_connection()
        ai_status = test_ai_connection()
        
        st.metric(
            "Database",
            "Connected" if db_status else "Disconnected",
            delta="OK" if db_status else "ERROR",
            delta_color="normal" if db_status else "inverse"
        )
        st.metric(
            "AI Service",
            "Available" if ai_status else "Unavailable",
            delta="OK" if ai_status else "DEGRADED",
            delta_color="normal" if ai_status else "inverse"
        )


def main():
    """Main application."""
    # Title
    st.title("📊 Project Coordinator Command Center")
    st.markdown("*AI-powered project management for public sector coordinators*")
    
    # Initialize database
    try:
        init_database()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()
    
    # Get all projects for sidebar
    try:
        with get_session() as session:
            projects_db = session.query(ProjectDB).order_by(ProjectDB.name).all()
            # Convert to list of dicts to avoid DetachedInstanceError
            all_projects = [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "status": p.status
                }
                for p in projects_db
            ]
    except Exception as e:
        st.error(f"Failed to load projects: {e}")
        all_projects = []
    
    # Sidebar navigation
    st.sidebar.title("🏠 Navigation")
    
    # Master Pages
    st.sidebar.markdown("### 📋 Master Pages")
    page = st.sidebar.radio(
        "Main Views:",
        ["📊 All Projects Overview", "➕ Create New Project", "📁 Documents", "📰 Daily Briefing", "⚙️ System Status"],
        label_visibility="collapsed"
    )
    
    # Individual Projects
    if all_projects:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🎯 Your Projects")
        st.sidebar.caption(f"{len(all_projects)} active project(s)")
        
        # Initialize selected project in session state
        if "selected_project_id" not in st.session_state:
            st.session_state.selected_project_id = None
        
        for proj in all_projects:
            # Status emoji
            status_emoji = {
                "planning": "📝",
                "active": "🔄",
                "on-hold": "⏸️",
                "completed": "✅",
                "cancelled": "❌"
            }.get(proj["status"], "📁")
            
            # Create button for each project
            if st.sidebar.button(
                f"{status_emoji} {proj['name']}",
                key=f"proj_{proj['id']}",
                use_container_width=True
            ):
                st.session_state.selected_project_id = uuid.UUID(proj['id'])
                page = "PROJECT_DETAIL"
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 💡 About
    AI-powered project management system with:
    - Structured risk tracking
    - Budget monitoring
    - Document analysis
    - Daily AI briefings
    
    **Security**: All data processed locally.
    """)
    
    # Route to pages
    if page == "📊 All Projects Overview":
        show_all_projects_overview()
    elif page == "➕ Create New Project":
        show_project_form()
    elif page == "📁 Documents":
        show_documents()
    elif page == "📰 Daily Briefing":
        show_daily_briefing()
    elif page == "⚙️ System Status":
        show_system_status()
    elif page == "PROJECT_DETAIL" and st.session_state.selected_project_id:
        show_project_detail(st.session_state.selected_project_id)


def show_all_projects_overview():
    """Master overview of all projects."""
    st.header("📊 All Projects Overview")
    
    try:
        with get_session() as session:
            projects_db = session.query(ProjectDB).all()
            
            if not projects_db:
                st.info("🎯 No projects yet! Click '➕ Create New Project' in the sidebar to get started.")
                return
            
            # Convert to dicts to avoid DetachedInstanceError
            projects = [
                {
                    "id": str(p.id),
                    "name": p.name,
                    "status": p.status,
                    "description": p.description,
                    "budget_allocated": float(p.budget_allocated) if p.budget_allocated else None,
                    "budget_spent": float(p.budget_spent) if p.budget_spent else 0.0,
                    "expected_end_date": p.expected_end_date
                }
                for p in projects_db
            ]
        
        # Now work with the plain dicts outside the session
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Projects", len(projects))
        with col2:
            active = len([p for p in projects if p["status"] == "active"])
            st.metric("Active", active)
        with col3:
            total_budget = sum([p["budget_allocated"] or 0 for p in projects])
            st.metric("Total Budget", f"${total_budget:,.0f}")
        with col4:
            completed = len([p for p in projects if p["status"] == "completed"])
            st.metric("Completed", completed)
        
        st.markdown("---")
        
        # Projects by status
        st.subheader("Projects by Status")
        
        status_groups = {}
        for proj in projects:
            status = proj["status"] or "unknown"
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(proj)
        
        for status, projs in status_groups.items():
            status_emoji = {
                "planning": "📝",
                "active": "🔄",
                "on-hold": "⏸️",
                "completed": "✅",
                "cancelled": "❌"
            }.get(status, "📁")
            
            with st.expander(f"{status_emoji} {status.upper()} ({len(projs)})", expanded=(status == "active")):
                for proj in projs:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.markdown(f"**{proj['name']}**")
                        if proj["description"]:
                            st.caption(proj["description"][:100] + "..." if len(proj["description"]) > 100 else proj["description"])
                    with col2:
                        if proj["budget_allocated"]:
                            spent_pct = (proj["budget_spent"] / proj["budget_allocated"] * 100) if proj["budget_allocated"] > 0 else 0.0
                            st.progress(float(spent_pct / 100))
                            st.caption(f"Budget: {spent_pct:.0f}% spent")
                        if proj["expected_end_date"]:
                            st.caption(f"Due: {proj['expected_end_date']}")
                    with col3:
                        if st.button("View", key=f"view_{proj['id']}"):
                            st.session_state.selected_project_id = uuid.UUID(proj['id'])
                            st.rerun()
                    
                    st.markdown("---")
    
    except Exception as e:
        st.error(f"Error loading projects: {e}")
        logger.error(f"Projects overview error: {e}")


def show_project_detail(project_id):
    """Detailed view of a single project."""
    try:
        with get_session() as session:
            project = session.query(ProjectDB).filter(ProjectDB.id == project_id).first()
            
            if not project:
                st.error("Project not found")
                st.session_state.selected_project_id = None
                return
            
            # Access all needed attributes while in session
            # This prevents DetachedInstanceError
            project_name = project.name
            project_status = project.status
            project_manager = project.project_manager
            project_id_val = project.id
            
            # Header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.header(f"📁 {project_name}")
                st.caption(f"Status: {project_status.upper()} | Manager: {project_manager or 'Unassigned'}")
            with col2:
                if st.button("🗑️ Delete Project", type="secondary"):
                    if delete_project(project_id_val):
                        st.success("Project deleted!")
                        st.session_state.selected_project_id = None
                        st.rerun()
            
            # Tabs for different sections - pass session and project
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "💰 Budget", "⚠️ Risks", "📄 Documents"])
            
            with tab1:
                show_project_overview_tab(project, session)
            
            with tab2:
                show_project_budget_tab(project, session)
            
            with tab3:
                show_project_risks_tab(project, session)
            
            with tab4:
                show_project_documents_tab(project, session)
    
    except Exception as e:
        st.error(f"Error loading project: {e}")
        logger.error(f"Project detail error: {e}")


def show_project_overview_tab(project, session):
    """Overview tab for project detail."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Basic Information")
        st.markdown(f"**Department:** {project.department or 'N/A'}")
        st.markdown(f"**Priority:** {'🔥' * project.priority_level if project.priority_level else 'N/A'}")
        st.markdown(f"**Start Date:** {project.start_date or 'Not set'}")
        st.markdown(f"**Expected End:** {project.expected_end_date or 'Not set'}")
    
    with col2:
        st.markdown("### 💰 Budget Summary")
        if project.budget_allocated:
            spent_pct = float(project.budget_spent / project.budget_allocated * 100) if project.budget_allocated > 0 else 0.0
            st.progress(float(spent_pct / 100))
            st.markdown(f"**Allocated:** ${project.budget_allocated:,.2f}")
            st.markdown(f"**Spent:** ${project.budget_spent:,.2f}")
            st.markdown(f"**Remaining:** ${(project.budget_allocated - project.budget_spent):,.2f}")
        else:
            st.info("No budget allocated")
    
    st.markdown("---")
    
    if project.description:
        st.markdown("### 📖 Description")
        st.markdown(project.description)
    
    # Structured data
    if project.structured_data:
        data = project.structured_data
        
        if data.get("objectives"):
            st.markdown("### 🎯 Objectives")
            st.markdown(data["objectives"])
        
        if data.get("success_criteria"):
            st.markdown("### ✅ Success Criteria")
            st.markdown(data["success_criteria"])
        
        if data.get("stakeholders"):
            st.markdown("### 👥 Stakeholders")
            st.markdown(data["stakeholders"])
        
        if data.get("milestones"):
            st.markdown("### 📅 Milestones")
            st.markdown(data["milestones"])


def show_project_budget_tab(project, session):
    """Budget tab for project detail."""
    st.markdown("### 💰 Budget Tracking")
    
    # Budget overview
    if project.budget_allocated:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Allocated", f"${project.budget_allocated:,.2f}")
        with col2:
            st.metric("Spent", f"${project.budget_spent:,.2f}")
        with col3:
            remaining = project.budget_allocated - project.budget_spent
            st.metric("Remaining", f"${remaining:,.2f}")
        
        spent_pct = float(project.budget_spent / project.budget_allocated * 100)
        st.progress(float(spent_pct / 100))
        st.caption(f"{spent_pct:.1f}% of budget used")
    
    st.markdown("---")
    
    # Add transaction
    st.subheader("Add Transaction")
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input("Amount ($)", min_value=0.0, step=100.0, format="%.2f")
            category = st.text_input("Category", placeholder="Materials, Labor, etc.")
        with col2:
            vendor = st.text_input("Vendor/Payee", placeholder="Vendor name")
            transaction_date = st.date_input("Transaction Date", value=date.today())
        
        description = st.text_area("Description", placeholder="Details about this transaction...")
        
        submitted = st.form_submit_button("Add Transaction", type="primary")
        
        if submitted and amount > 0:
            if add_transaction(
                project_id=project.id,
                amount=Decimal(str(amount)),
                category=category or None,
                vendor=vendor or None,
                description=description or None,
                transaction_date=transaction_date
            ):
                st.success("Transaction added!")
                st.rerun()
    
    # Transaction history
    st.markdown("---")
    st.subheader("Transaction History")
    
    if project.transactions:
        for txn in sorted(project.transactions, key=lambda x: x.transaction_date, reverse=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{txn.transaction_date}** - {txn.category or 'Uncategorized'}")
                if txn.description:
                    st.caption(txn.description)
            with col2:
                st.markdown(f"**Vendor:** {txn.vendor or 'N/A'}")
            with col3:
                st.markdown(f"**${txn.amount:,.2f}**")
            st.markdown("---")
    else:
        st.info("No transactions yet")


def show_project_risks_tab(project, session):
    """Risks tab for project detail."""
    st.markdown("### ⚠️ Risk Register")
    
    if project.structured_data and project.structured_data.get("risks"):
        risks = project.structured_data["risks"]
        
        if isinstance(risks, list):
            # Display structured risks
            for risk in risks:
                risk_color = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
                likelihood_icon = risk_color.get(risk.get("likelihood", "medium"), "⚪")
                impact_icon = risk_color.get(risk.get("impact", "medium"), "⚪")
                
                with st.expander(f"{risk.get('id', 'N/A')}: {risk.get('description', 'No description')[:60]}..."):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Likelihood:** {likelihood_icon} {risk.get('likelihood', 'N/A').upper()}")
                        st.markdown(f"**Impact:** {impact_icon} {risk.get('impact', 'N/A').upper()}")
                        st.markdown(f"**Status:** {risk.get('status', 'identified').upper()}")
                    with col2:
                        st.markdown(f"**Owner:** {risk.get('owner', 'Unassigned')}")
                        if risk.get('review_date'):
                            st.markdown(f"**Review Date:** {risk['review_date']}")
                    
                    st.markdown("**Description:**")
                    st.markdown(risk.get('description', 'No description'))
                    st.markdown("**Mitigation Strategy:**")
                    st.markdown(risk.get('mitigation', 'No mitigation defined'))
        else:
            # Legacy text-based risks
            st.markdown(risks)
    else:
        st.info("No risks registered for this project")
    
    # Dependencies
    if project.structured_data and project.structured_data.get("dependencies"):
        st.markdown("---")
        st.markdown("### 🔗 Dependencies & Constraints")
        st.markdown(project.structured_data["dependencies"])


def show_project_documents_tab(project, session):
    """Documents tab for project detail."""
    st.markdown("### 📄 Project Documents")
    
    # Upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "pdf", "doc", "docx"],
        help="Upload project documents for AI analysis"
    )
    
    if uploaded_file:
        if st.button("📤 Upload & Analyze", type="primary"):
            with st.spinner("Processing document..."):
                result = process_document(uploaded_file, project.id)
                if result:
                    st.success("✅ Document uploaded and analyzed!")
                    st.rerun()
                else:
                    st.error("Failed to process document")
    
    st.markdown("---")
    
    # Document list
    st.subheader("Document Library")
    
    if project.documents:
        for doc in sorted(project.documents, key=lambda x: x.uploaded_at, reverse=True):
            with st.expander(f"📄 {doc.filename} ({doc.file_type})"):
                st.markdown(f"**Uploaded:** {doc.uploaded_at}")
                st.markdown(f"**Size:** {doc.file_size:,} bytes")
                
                if doc.ai_analysis:
                    st.markdown("**AI Analysis:**")
                    analysis = doc.ai_analysis
                    if isinstance(analysis, dict):
                        if analysis.get("summary"):
                            st.markdown(f"*{analysis['summary']}*")
                        if analysis.get("key_points"):
                            st.markdown("**Key Points:**")
                            for point in analysis["key_points"]:
                                st.markdown(f"• {point}")
    else:
        st.info("No documents uploaded yet")


if __name__ == "__main__":
    main()
