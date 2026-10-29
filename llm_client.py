"""
llm_client.py – WatsonX AI LLM client wrapper.
Uses Meta Llama 3.3 70B Instruct via IBM WatsonX AI.
Handles authentication, model initialisation, and text generation.
"""

import logging
from typing import Optional

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

from config import (
    IBM_API_KEY,
    IBM_PROJECT_ID,
    IBM_URL,
    GRANITE_MODEL_ID,
    GENERATION_PARAMS,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Singleton wrapper around the WatsonX AI model inference endpoint."""

    _instance: Optional["LLMClient"] = None
    _model: Optional[ModelInference] = None

    def __new__(cls) -> "LLMClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ── Initialisation ──────────────────────────────────────────────────────
    def initialise(self) -> None:
        """Create the WatsonX credentials and model inference object."""
        if self._model is not None:
            return  # already initialised
        try:
            credentials = Credentials(
                url=IBM_URL,
                api_key=IBM_API_KEY,
            )
            # Build params dict — decoding_method uses the string value directly
            # to avoid enum compatibility issues across SDK versions.
            params = {
                "decoding_method": "sample",
                **GENERATION_PARAMS,
            }
            self._model = ModelInference(
                model_id=GRANITE_MODEL_ID,
                credentials=credentials,
                project_id=IBM_PROJECT_ID,
                params=params,
            )
            logger.info("LLM client initialised: %s", GRANITE_MODEL_ID)
        except Exception as exc:
            logger.error("Failed to initialise LLM client: %s", exc)
            raise RuntimeError(
                f"Could not connect to IBM WatsonX. Check your API key and project ID.\n{exc}"
            ) from exc

    # ── Generation ──────────────────────────────────────────────────────────
    def generate(self, prompt: str, max_new_tokens: Optional[int] = None) -> str:
        """
        Send a prompt to the model and return the generated text.
        Uses the chat endpoint (/ml/v1/text/chat) which is the current
        recommended API for instruction-tuned models on WatsonX.

        Args:
            prompt: The full prompt string (treated as user turn).
            max_new_tokens: Override the default max_new_tokens if provided.

        Returns:
            The model's generated text as a string.
        """
        if self._model is None:
            self.initialise()

        try:
            params = {}
            if max_new_tokens:
                params["max_tokens"] = max_new_tokens

            messages = [{"role": "user", "content": prompt}]

            response = self._model.chat(
                messages=messages,
                params=params if params else None,
            )
            # chat() returns a dict with choices[0].message.content
            if isinstance(response, dict):
                choices = response.get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    return msg.get("content", "").strip()
                # Fallback: try results key (older SDK shape)
                results = response.get("results", [{}])
                return results[0].get("generated_text", "").strip()
            return str(response).strip()
        except Exception as exc:
            logger.error("LLM generation error: %s", exc)
            raise RuntimeError(
                f"LLM generation failed. The model may be temporarily unavailable.\n{exc}"
            ) from exc

    # ── Health check ────────────────────────────────────────────────────────
    def health_check(self) -> bool:
        """Return True if the model can respond to a minimal prompt."""
        try:
            result = self.generate("Hello. Reply with one word: Ready", max_new_tokens=10)
            return bool(result)
        except Exception:
            return False


# Module-level singleton — kept as `granite_client` for backwards compatibility
# with all agent imports that already reference this name.
granite_client = LLMClient()
