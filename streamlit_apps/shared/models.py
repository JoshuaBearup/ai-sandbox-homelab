"""
Pydantic models for type-safe data structures.

This module defines all data models used across applications.
Follows Principle 6: Type Safety and Structured Data.

All AI responses, database models, and API contracts should use Pydantic models
to ensure type safety and automatic validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AIProvider(str, Enum):
    """AI provider types."""
    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"


class Environment(str, Enum):
    """Deployment environments."""
    LOCAL = "local"
    DEV = "dev"
    PREPROD = "preprod"
    PRD = "prd"


# Example AI Response Models
# These demonstrate the pattern - create similar models for your use cases

class SimpleAIResponse(BaseModel):
    """
    Simple AI response for testing.

    Example use case: Basic Q&A, simple analysis
    """
    answer: str = Field(..., description="AI generated answer")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")
    reasoning: Optional[str] = Field(None, description="Why this answer was given")


class SentimentAnalysis(BaseModel):
    """
    Sentiment analysis response.

    Example use case: Analyze customer feedback, support tickets
    """
    sentiment: str = Field(..., description="positive, negative, or neutral")
    score: float = Field(..., ge=-1, le=1, description="Sentiment score -1 to 1")
    key_phrases: List[str] = Field(default_factory=list, description="Key phrases detected")
    suggestion: Optional[str] = Field(None, description="Suggested action")


class DataInsight(BaseModel):
    """
    Data insight from AI analysis.

    Example use case: Dashboard insights, automated reporting
    """
    insight_type: str = Field(..., description="Type of insight (trend, anomaly, recommendation)")
    title: str = Field(..., description="Brief insight title")
    description: str = Field(..., description="Detailed explanation")
    confidence: float = Field(..., ge=0, le=1, description="Confidence in this insight")
    action_items: List[str] = Field(default_factory=list, description="Recommended actions")


class AIInteractionLog(BaseModel):
    """
    Log entry for AI interactions.

    This is stored in the database to track all AI calls.
    Useful for debugging, auditing, and cost tracking.
    """
    id: Optional[int] = Field(None, description="Database ID (auto-generated)")
    call_id: str = Field(..., description="Unique call identifier (UUID)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the call was made")
    provider: str = Field(..., description="AI provider used (mock, ollama, openai)")
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="User prompt sent to AI")
    response: Optional[str] = Field(None, description="AI response (JSON string)")
    success: bool = Field(..., description="Whether call succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    latency_ms: Optional[int] = Field(None, description="Response time in milliseconds")
    environment: str = Field(..., description="Environment where call was made")

    class Config:
        """Pydantic config."""
        from_attributes = True  # Allow ORM mode for SQLAlchemy integration


# Add your application-specific models here
# Examples:

class UserQuery(BaseModel):
    """Example: User question for Q&A application."""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    context: Optional[str] = Field(None, description="Additional context")


class AIGeneratedSummary(BaseModel):
    """Example: AI-generated summary of text."""
    summary: str = Field(..., description="Concise summary")
    key_points: List[str] = Field(..., description="Main points extracted")
    word_count_original: int = Field(..., description="Original text word count")
    word_count_summary: int = Field(..., description="Summary word count")
    compression_ratio: float = Field(..., ge=0, le=1, description="Summary length / original length")


# App2: Project Coordinator Models

class ProjectStatus(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on-hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentAnalysis(BaseModel):
    """AI analysis of project documents."""
    summary: str = Field(..., description="3-4 sentence summary of document content")
    document_type: str = Field(..., description="contract, report, memo, invoice, etc.")
    key_points: List[str] = Field(..., description="3-5 most important points from document")
    action_items: List[str] = Field(default_factory=list, description="Any action items or tasks mentioned")
    budget_impact: Optional[str] = Field(None, description="Any budget implications mentioned")
    deadlines: List[str] = Field(default_factory=list, description="Any dates or deadlines mentioned")


class ProjectBriefing(BaseModel):
    """AI-generated daily briefing for project coordinator."""
    urgent_items: List[str] = Field(..., description="Items needing immediate attention")
    budget_alerts: List[str] = Field(..., description="Budget concerns or variances")
    timeline_risks: List[str] = Field(..., description="Projects at risk of delay")
    upcoming_deadlines: List[str] = Field(..., description="Important dates in next 7 days")
    recommendations: List[str] = Field(..., description="Recommended actions for today")


# Structured Project Component Models

class RiskLevel(str, Enum):
    """Risk likelihood/impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    """Risk management status."""
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"


class ActionStatus(str, Enum):
    """Action item status."""
    NOT_STARTED = "not-started"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MilestoneStatus(str, Enum):
    """Milestone status."""
    UPCOMING = "upcoming"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class Risk(BaseModel):
    """Structured risk with tracking."""
    id: str = Field(..., description="Unique risk ID (e.g., R001)")
    description: str = Field(..., description="Risk description")
    likelihood: RiskLevel = Field(..., description="Probability of occurrence")
    impact: RiskLevel = Field(..., description="Severity if it occurs")
    mitigation: str = Field(..., description="Mitigation strategy")
    owner: Optional[str] = Field(None, description="Person responsible for managing risk")
    status: RiskStatus = Field(RiskStatus.IDENTIFIED, description="Current risk status")
    identified_date: Optional[str] = Field(None, description="When risk was identified (YYYY-MM-DD)")
    review_date: Optional[str] = Field(None, description="Next review date (YYYY-MM-DD)")


class Action(BaseModel):
    """Structured action item with tracking."""
    id: str = Field(..., description="Unique action ID (e.g., A001)")
    description: str = Field(..., description="Action description")
    owner: str = Field(..., description="Person responsible")
    due_date: Optional[str] = Field(None, description="Due date (YYYY-MM-DD)")
    status: ActionStatus = Field(ActionStatus.NOT_STARTED, description="Current status")
    priority: int = Field(3, ge=1, le=5, description="Priority level 1-5")
    notes: Optional[str] = Field(None, description="Additional notes or updates")
    completed_date: Optional[str] = Field(None, description="Completion date (YYYY-MM-DD)")


class Milestone(BaseModel):
    """Structured milestone with deliverables."""
    id: str = Field(..., description="Unique milestone ID (e.g., M001)")
    name: str = Field(..., description="Milestone name")
    target_date: str = Field(..., description="Target completion date (YYYY-MM-DD)")
    completion_date: Optional[str] = Field(None, description="Actual completion date (YYYY-MM-DD)")
    status: MilestoneStatus = Field(MilestoneStatus.UPCOMING, description="Current status")
    deliverables: List[str] = Field(default_factory=list, description="Expected deliverables")
    dependencies: List[str] = Field(default_factory=list, description="Milestone IDs this depends on")
    notes: Optional[str] = Field(None, description="Additional notes")


class Stakeholder(BaseModel):
    """Structured stakeholder with engagement tracking."""
    id: str = Field(..., description="Unique stakeholder ID (e.g., S001)")
    name: str = Field(..., description="Stakeholder name or organization")
    role: str = Field(..., description="Role in project (e.g., Decision Maker, Consulted)")
    interest: str = Field(..., description="High, Medium, Low")
    influence: str = Field(..., description="High, Medium, Low")
    engagement_strategy: Optional[str] = Field(None, description="How to engage this stakeholder")
    contact: Optional[str] = Field(None, description="Contact information")
    last_engaged: Optional[str] = Field(None, description="Last engagement date (YYYY-MM-DD)")


class BudgetLine(BaseModel):
    """Structured budget line item."""
    id: str = Field(..., description="Unique budget line ID (e.g., B001)")
    category: str = Field(..., description="Budget category")
    allocated: float = Field(..., description="Allocated amount")
    spent: float = Field(0.0, description="Amount spent so far")
    notes: Optional[str] = Field(None, description="Notes about this budget line")


class StructuredProjectData(BaseModel):
    """Container for all structured project components."""
    objectives: List[str] = Field(default_factory=list, description="Project objectives")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    risks: List[Risk] = Field(default_factory=list, description="Risk register")
    actions: List[Action] = Field(default_factory=list, description="Action items")
    milestones: List[Milestone] = Field(default_factory=list, description="Project milestones")
    stakeholders: List[Stakeholder] = Field(default_factory=list, description="Stakeholder register")
    budget_lines: List[BudgetLine] = Field(default_factory=list, description="Budget breakdown")
    dependencies: List[str] = Field(default_factory=list, description="External dependencies")
    notes: Optional[str] = Field(None, description="Additional project notes")
