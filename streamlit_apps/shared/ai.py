"""
AI client wrapper with support for Mock, Ollama, and OpenAI.

This module provides a unified interface for AI interactions.
Follows Principle 5: Progressive Enhancement - AI features fail gracefully.

Providers:
    - Mock: Returns fake responses for testing (no real AI)
    - Ollama: Local AI server (use on server deployment)
    - OpenAI: Cloud API (optional fallback)

Usage:
    from shared.ai import get_ai_client, call_structured_llm
    from shared.models import SimpleAIResponse

    # Get client (automatically uses configured provider)
    client = get_ai_client()

    # Call AI with structured output
    response, call_id = call_structured_llm(
        client=client,
        response_model=SimpleAIResponse,
        user_prompt="What is 2+2?",
        system_prompt="You are a helpful math tutor."
    )

    if response:
        print(response.answer)  # Type-safe access

Configuration Changes for Server:
    1. Change AI_PROVIDER from "mock" to "ollama" in .env
    2. Update AI_BASE_URL to "http://192.168.1.102:11434"
    3. Keep same code - no changes needed!
"""

from typing import Type, TypeVar, Tuple, Optional
from pydantic import BaseModel
import json
import logging
import time
import uuid
from datetime import datetime

from shared.config import get_config
from shared.db import log_ai_interaction

logger = logging.getLogger(__name__)

# Type variable for generic response models
T = TypeVar('T', bound=BaseModel)


class MockAIClient:
    """
    Mock AI client for local development and testing.

    Returns realistic fake responses based on the response model schema.
    No actual AI calls are made - instant responses, zero cost.
    """

    def __init__(self):
        self.model = "mock-model"
        logger.info("Initialized Mock AI client")

    def generate_mock_response(self, response_model: Type[T]) -> T:
        """
        Generate a mock response matching the Pydantic model schema.

        Args:
            response_model: Pydantic model class defining response structure

        Returns:
            Instance of response_model with fake data
        """
        # Import here to avoid circular dependency
        from shared.models import SimpleAIResponse, SentimentAnalysis, DataInsight

        # Generate appropriate mock data based on model type
        if response_model == SimpleAIResponse:
            return SimpleAIResponse(
                answer="This is a mock AI response. The mock provider returns fake data for testing.",
                confidence=0.95,
                reasoning="Mock AI always returns high confidence responses for testing purposes."
            )

        elif response_model == SentimentAnalysis:
            return SentimentAnalysis(
                sentiment="positive",
                score=0.8,
                key_phrases=["great product", "highly recommend", "excellent service"],
                suggestion="Continue current approach - customer feedback is very positive."
            )

        elif response_model == DataInsight:
            return DataInsight(
                insight_type="trend",
                title="Mock Trend Detected",
                description="This is a mock insight. In production, real AI would analyze data and provide meaningful insights.",
                confidence=0.85,
                action_items=[
                    "Monitor this trend over next 7 days",
                    "Compare with historical patterns",
                    "Consider adjusting strategy if trend continues"
                ]
            )

        else:
            # Generic mock response - try to instantiate with minimal valid data
            try:
                # Get model fields and create minimal valid instance
                mock_data = {}
                for field_name, field in response_model.__fields__.items():
                    if field.required:
                        # Provide sensible defaults based on type
                        if field.outer_type_ == str:
                            mock_data[field_name] = f"Mock {field_name}"
                        elif field.outer_type_ == int:
                            mock_data[field_name] = 42
                        elif field.outer_type_ == float:
                            mock_data[field_name] = 0.75
                        elif field.outer_type_ == bool:
                            mock_data[field_name] = True
                        elif field.outer_type_ == list:
                            mock_data[field_name] = ["mock_item_1", "mock_item_2"]

                return response_model(**mock_data)

            except Exception as e:
                logger.error(f"Failed to generate mock response for {response_model.__name__}: {e}")
                raise


class OllamaClient:
    """
    Ollama AI client for local AI server.

    Connects to Ollama server (typically on VM 101 in production).
    Uses OpenAI-compatible API.
    """

    def __init__(self, base_url: str, model: str):
        """
        Initialize Ollama client.

        Args:
            base_url: Ollama server URL (e.g., http://192.168.1.102:11434)
            model: Model name (e.g., llama3.1:8b)
        """
        try:
            from openai import OpenAI

            self.client = OpenAI(
                base_url=f"{base_url}/v1",
                api_key="ollama",  # Ollama doesn't use API keys
            )
            self.model = model
            logger.info(f"Initialized Ollama client: {base_url} with model {model}")

        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            raise

    def create_completion(
        self,
        messages: list,
        response_format: dict | None = None,
        temperature: float = 0.7,
    ) -> dict:
        """
        Create chat completion.

        Args:
            messages: List of message dicts with role and content
            response_format: Response format specification (JSON schema)
            temperature: Sampling temperature 0-1

        Returns:
            API response dict
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = self.client.chat.completions.create(**kwargs)
        return response


class OpenAIClient:
    """
    OpenAI API client for cloud AI.

    Uses official OpenAI API. Requires API key.
    """

    def __init__(self, api_key: str, model: str):
        """
        Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model name (e.g., gpt-4o-mini)
        """
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info(f"Initialized OpenAI client with model {model}")

        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            raise

    def create_completion(
        self,
        messages: list,
        response_format: dict | None = None,
        temperature: float = 0.7,
    ) -> dict:
        """
        Create chat completion.

        Args:
            messages: List of message dicts with role and content
            response_format: Response format specification (JSON schema)
            temperature: Sampling temperature 0-1

        Returns:
            API response dict
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if response_format:
            kwargs["response_format"] = response_format

        response = self.client.chat.completions.create(**kwargs)
        return response


def get_ai_client() -> MockAIClient | OllamaClient | OpenAIClient | None:
    """
    Get AI client based on configuration.

    Returns appropriate client based on AI_PROVIDER setting:
    - "mock": MockAIClient (for local testing)
    - "ollama": OllamaClient (for server deployment)
    - "openai": OpenAIClient (for cloud API)

    Returns:
        AI client instance or None if initialization fails

    Example:
        >>> from shared.ai import get_ai_client
        >>> client = get_ai_client()
        >>> if client:
        ...     # Use client for AI calls
        ...     pass
        ... else:
        ...     # Handle gracefully - core app still works
        ...     pass
    """
    try:
        config = get_config()

        if config.ai_provider == "mock":
            return MockAIClient()

        elif config.ai_provider == "ollama":
            return OllamaClient(
                base_url=config.ai_base_url,
                model=config.ai_model
            )

        elif config.ai_provider == "openai":
            if not config.openai_api_key:
                logger.error("OpenAI API key not configured")
                return None

            return OpenAIClient(
                api_key=config.openai_api_key,
                model=config.ai_model
            )

        else:
            logger.error(f"Unknown AI provider: {config.ai_provider}")
            return None

    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}")
        return None


def call_structured_llm(
    client: MockAIClient | OllamaClient | OpenAIClient,
    response_model: Type[T],
    user_prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    temperature: float = 0.7,
    log_to_db: bool = True,
) -> Tuple[Optional[T], str]:
    """
    Call AI with structured, validated output.

    This is the main function for AI interactions. It:
    1. Calls AI (mock, Ollama, or OpenAI)
    2. Validates response against Pydantic model
    3. Logs interaction to database
    4. Returns validated response

    Follows Principle 6: Type Safety and Structured Data.

    Args:
        client: AI client (from get_ai_client())
        response_model: Pydantic model for response validation
        user_prompt: User's question/prompt
        system_prompt: System instructions for AI
        temperature: Sampling temperature 0-1
        log_to_db: Whether to log interaction to database

    Returns:
        Tuple of (validated_response, call_id)
        validated_response is None if call fails

    Example:
        >>> from shared.ai import get_ai_client, call_structured_llm
        >>> from shared.models import SimpleAIResponse
        >>>
        >>> client = get_ai_client()
        >>> if client:
        ...     response, call_id = call_structured_llm(
        ...         client=client,
        ...         response_model=SimpleAIResponse,
        ...         user_prompt="What is Python?",
        ...     )
        ...     if response:
        ...         print(response.answer)  # Type-safe!
        ...         print(f"Confidence: {response.confidence}")
    """
    call_id = str(uuid.uuid4())
    config = get_config()
    start_time = time.time()

    try:
        logger.info(f"AI call started: {call_id}")

        # Handle mock client separately
        if isinstance(client, MockAIClient):
            response_obj = client.generate_mock_response(response_model)
            response_json = response_obj.json()
            latency_ms = int((time.time() - start_time) * 1000)

            logger.info(f"AI call completed (mock): {call_id} in {latency_ms}ms")

            # Log to database
            if log_to_db:
                log_ai_interaction(
                    call_id=call_id,
                    provider="mock",
                    model="mock-model",
                    prompt=user_prompt,
                    response=response_json,
                    success=True,
                    latency_ms=latency_ms,
                    environment=config.environment,
                )

            return response_obj, call_id

        # Handle real AI clients (Ollama, OpenAI)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        # For structured output, add JSON schema hint
        schema_prompt = f"\n\nRespond with valid JSON matching this schema:\n{response_model.schema_json(indent=2)}"
        messages[1]["content"] += schema_prompt

        # Call AI
        response = client.create_completion(
            messages=messages,
            temperature=temperature,
        )

        # Extract response text
        response_text = response.choices[0].message.content
        latency_ms = int((time.time() - start_time) * 1000)

        # Parse and validate against Pydantic model
        try:
            # Try to parse as JSON
            response_dict = json.loads(response_text)
            response_obj = response_model(**response_dict)

            logger.info(f"AI call completed: {call_id} in {latency_ms}ms")

            # Log success
            if log_to_db:
                log_ai_interaction(
                    call_id=call_id,
                    provider=config.ai_provider,
                    model=config.ai_model,
                    prompt=user_prompt,
                    response=response_obj.json(),
                    success=True,
                    latency_ms=latency_ms,
                    environment=config.environment,
                )

            return response_obj, call_id

        except json.JSONDecodeError as e:
            logger.error(f"AI response not valid JSON: {e}")
            logger.error(f"Response text: {response_text}")

            # Log failure
            if log_to_db:
                log_ai_interaction(
                    call_id=call_id,
                    provider=config.ai_provider,
                    model=config.ai_model,
                    prompt=user_prompt,
                    response=response_text,
                    success=False,
                    error_message=f"Invalid JSON: {str(e)}",
                    latency_ms=latency_ms,
                    environment=config.environment,
                )

            return None, call_id

        except Exception as e:
            logger.error(f"AI response validation failed: {e}")

            # Log failure
            if log_to_db:
                log_ai_interaction(
                    call_id=call_id,
                    provider=config.ai_provider,
                    model=config.ai_model,
                    prompt=user_prompt,
                    response=response_text,
                    success=False,
                    error_message=f"Validation error: {str(e)}",
                    latency_ms=latency_ms,
                    environment=config.environment,
                )

            return None, call_id

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(f"AI call failed: {call_id} - {e}")

        # Log failure
        if log_to_db:
            log_ai_interaction(
                call_id=call_id,
                provider=config.ai_provider,
                model=config.ai_model,
                prompt=user_prompt,
                response=None,
                success=False,
                error_message=str(e),
                latency_ms=latency_ms,
                environment=config.environment,
            )

        return None, call_id


def test_ai_connection() -> bool:
    """
    Test AI connection with a simple call.

    Returns:
        bool: True if AI is working, False otherwise

    Example:
        >>> from shared.ai import test_ai_connection
        >>> if test_ai_connection():
        ...     print("AI is ready!")
        ... else:
        ...     print("AI not available - app will work without AI features")
    """
    try:
        from shared.models import SimpleAIResponse

        client = get_ai_client()
        if not client:
            return False

        response, call_id = call_structured_llm(
            client=client,
            response_model=SimpleAIResponse,
            user_prompt="Say hello",
            log_to_db=False,  # Don't log test calls
        )

        if response:
            logger.info("AI connection test: SUCCESS")
            return True
        else:
            logger.warning("AI connection test: FAILED (no response)")
            return False

    except Exception as e:
        logger.error(f"AI connection test: FAILED - {e}")
        return False
