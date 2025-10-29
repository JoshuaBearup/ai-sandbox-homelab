"""
Shared utilities for AI Sandbox applications.

This package provides reusable infrastructure components:
- config: Configuration management
- db: Database connection and models
- ai: AI client wrapper (Mock, Ollama, OpenAI)
- models: Pydantic models for type safety

Import examples:
    from shared.config import get_config
    from shared.db import get_session, init_database
    from shared.ai import get_ai_client, call_structured_llm
    from shared.models import SimpleAIResponse, SentimentAnalysis
"""

__version__ = "0.1.0"
