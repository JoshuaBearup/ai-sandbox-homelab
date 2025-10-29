"""
AI Sandbox - Test Application 1

This is a demonstration app showcasing all core framework patterns:
- Database connectivity (PostgreSQL)
- AI integration (Mock/Ollama/OpenAI)
- Type-safe responses (Pydantic)
- Progressive enhancement (works without AI)
- Configuration management

This app demonstrates:
1. Database CRUD operations
2. AI-powered Q&A with structured responses
3. Viewing AI interaction logs
4. System health checks
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.config import get_config
from shared.db import init_database, get_session, test_connection, AIInteractionLogDB
from shared.ai import get_ai_client, call_structured_llm, test_ai_connection
from shared.models import SimpleAIResponse, SentimentAnalysis
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="AI Sandbox - Test App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def show_system_status():
    """Display system status and configuration."""
    st.header("System Status")

    config = get_config()

    # Configuration
    st.subheader("Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Environment", config.environment.upper())
        st.metric("AI Provider", config.ai_provider.upper())

    with col2:
        st.metric("AI Model", config.ai_model)
        st.metric("Log Level", config.log_level)

    with col3:
        # Test connections
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

    # Connection strings (sanitized)
    st.subheader("Connection Details")
    db_url = config.database_url.split('@')[0] + '@***'  # Hide host/password
    st.code(f"Database: {db_url}\nAI Base URL: {config.ai_base_url}", language="text")

    # AI Provider Info
    if config.ai_provider == "mock":
        st.info("""
        **Mock AI Provider Active**

        You're using simulated AI responses for testing. This is perfect for local development:
        - Zero cost
        - Instant responses
        - No internet required

        To use real AI:
        1. Change `AI_PROVIDER=ollama` in .env (for server deployment)
        2. Or change `AI_PROVIDER=openai` and add your API key (for cloud)

        See LOCAL_DEVELOPMENT.md for details.
        """)


def show_ai_qa():
    """AI-powered Q&A interface with progressive enhancement."""
    st.header("AI Question & Answer")

    st.markdown("""
    Ask a question and get an AI-powered response with confidence scoring.

    **Features demonstrated:**
    - Structured AI responses (Pydantic validation)
    - Progressive enhancement (works even if AI fails)
    - Automatic logging to database
    - Type-safe response handling
    """)

    # User input
    question = st.text_area(
        "Your Question:",
        placeholder="What is Python?",
        height=100
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        ask_button = st.button("Ask AI", type="primary", use_container_width=True)

    if ask_button and question:
        with st.spinner("Thinking..."):
            # Get AI client
            client = get_ai_client()

            if not client:
                st.error("""
                AI client not available. Check your configuration:
                - Is AI_PROVIDER set correctly in .env?
                - If using Ollama, is it running?
                - If using OpenAI, is your API key valid?
                """)
                return

            # Call AI with structured response
            response, call_id = call_structured_llm(
                client=client,
                response_model=SimpleAIResponse,
                user_prompt=question,
                system_prompt="You are a helpful AI assistant. Provide clear, accurate answers.",
            )

            if response:
                # Display response
                st.success("Response received!")

                # Answer
                st.markdown("### Answer")
                st.write(response.answer)

                # Metadata
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Confidence", f"{response.confidence * 100:.1f}%")
                with col2:
                    st.metric("Call ID", call_id[:8] + "...")

                # Reasoning (if provided)
                if response.reasoning:
                    with st.expander("AI Reasoning"):
                        st.write(response.reasoning)

            else:
                st.error(f"""
                AI call failed (Call ID: {call_id[:8]}...).

                The app still works - this demonstrates **progressive enhancement**.
                Check the AI Logs tab to see what went wrong.
                """)


def show_sentiment_analysis():
    """Sentiment analysis demo."""
    st.header("Sentiment Analysis")

    st.markdown("""
    Analyze the sentiment of text (customer feedback, reviews, etc.).
    """)

    text = st.text_area(
        "Text to analyze:",
        placeholder="This product is amazing! I love it and would highly recommend it to anyone.",
        height=150
    )

    if st.button("Analyze Sentiment", type="primary"):
        with st.spinner("Analyzing..."):
            client = get_ai_client()

            if not client:
                st.error("AI client not available.")
                return

            # Call AI
            response, call_id = call_structured_llm(
                client=client,
                response_model=SentimentAnalysis,
                user_prompt=f"Analyze the sentiment of this text and provide key phrases:\n\n{text}",
                system_prompt="You are a sentiment analysis expert. Provide accurate sentiment scores.",
            )

            if response:
                # Display results
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Sentiment", response.sentiment.upper())
                    st.metric("Score", f"{response.score:.2f}")

                with col2:
                    st.metric("Call ID", call_id[:8] + "...")

                # Key phrases
                if response.key_phrases:
                    st.markdown("### Key Phrases")
                    for phrase in response.key_phrases:
                        st.markdown(f"- {phrase}")

                # Suggestion
                if response.suggestion:
                    st.info(f"**Suggestion:** {response.suggestion}")

            else:
                st.error(f"Sentiment analysis failed (Call ID: {call_id[:8]}...)")


def show_ai_logs():
    """View AI interaction logs from database."""
    st.header("AI Interaction Logs")

    st.markdown("""
    All AI calls are logged to the database for auditing and debugging.
    """)

    # Fetch logs
    try:
        with get_session() as session:
            logs = session.query(AIInteractionLogDB)\
                .order_by(AIInteractionLogDB.timestamp.desc())\
                .limit(50)\
                .all()

        if not logs:
            st.info("No AI interactions logged yet. Try the Q&A or Sentiment Analysis tabs!")
            return

        # Display count
        st.metric("Total Logs (last 50)", len(logs))

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_provider = st.selectbox(
                "Provider",
                ["All"] + list(set([log.provider for log in logs]))
            )
        with col2:
            filter_success = st.selectbox(
                "Status",
                ["All", "Success", "Failed"]
            )

        # Filter logs
        filtered_logs = logs
        if filter_provider != "All":
            filtered_logs = [log for log in filtered_logs if log.provider == filter_provider]
        if filter_success == "Success":
            filtered_logs = [log for log in filtered_logs if log.success]
        elif filter_success == "Failed":
            filtered_logs = [log for log in filtered_logs if not log.success]

        # Display logs
        for log in filtered_logs:
            with st.expander(
                f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - "
                f"{log.provider}/{log.model} - "
                f"{'✅ Success' if log.success else '❌ Failed'}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Call ID:** `{log.call_id}`")
                    st.markdown(f"**Provider:** {log.provider}")
                    st.markdown(f"**Model:** {log.model}")
                    st.markdown(f"**Environment:** {log.environment}")

                with col2:
                    st.markdown(f"**Success:** {'Yes' if log.success else 'No'}")
                    if log.latency_ms:
                        st.markdown(f"**Latency:** {log.latency_ms}ms")
                    if log.error_message:
                        st.markdown(f"**Error:** {log.error_message}")

                st.markdown("**Prompt:**")
                st.code(log.prompt, language="text")

                if log.response:
                    st.markdown("**Response:**")
                    st.code(log.response, language="json")

    except Exception as e:
        st.error(f"Failed to load logs: {e}")
        logger.error(f"Log loading error: {e}")


def main():
    """Main application."""
    # Title
    st.title("🤖 AI Sandbox - Test Application")
    st.markdown("*Demonstrating the AI Sandbox framework patterns*")

    # Initialize database (safe to call multiple times)
    try:
        init_database()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        st.stop()

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page:",
        ["System Status", "AI Q&A", "Sentiment Analysis", "AI Logs"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### About This App

    This is a test application demonstrating:
    - Database integration
    - AI provider abstraction
    - Type-safe responses
    - Progressive enhancement
    - Configuration management

    See `streamlit_apps/app1/` for code.
    """)

    # Route to selected page
    if page == "System Status":
        show_system_status()
    elif page == "AI Q&A":
        show_ai_qa()
    elif page == "Sentiment Analysis":
        show_sentiment_analysis()
    elif page == "AI Logs":
        show_ai_logs()


if __name__ == "__main__":
    main()
