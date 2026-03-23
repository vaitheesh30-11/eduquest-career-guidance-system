#!/usr/bin/env python3
"""
Gemini client adapter for YatraAI.
Builds a Gemini client with API key rotation and redundancy support.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv

    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

genai = None
genai_module = None
is_new_api = False

try:
    # Try new SDK first (google-genai v0.4+)
    from google import genai as genai_new
    genai = genai_new
    genai_module = "google.genai"
    is_new_api = True
except (ImportError, AttributeError):
    try:
        # Fallback to older SDK (google-generativeai)
        from google import generativeai as genai_old
        genai = genai_old
        genai_module = "google.generativeai"
        is_new_api = False
    except ImportError:
        genai = None


def _get_all_api_keys() -> list:
    """
    Return all available Gemini API keys for rotation.
    Checks Streamlit secrets (GEMINI_API_KEY_1..4) then environment variables
    (GEMINI_API_KEY, GEMINI_API_KEY_1..4).
    """
    keys = []
    try:
        import streamlit as st

        for i in range(1, 5):
            try:
                key = st.secrets.get(f"GEMINI_API_KEY_{i}")
                if key:
                    keys.append(key)
            except Exception:
                pass
    except ImportError:
        pass

    # Also check environment variables
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key and env_key not in keys:
        keys.append(env_key)

    for i in range(1, 5):
        env_key_i = os.getenv(f"GEMINI_API_KEY_{i}")
        if env_key_i and env_key_i not in keys:
            keys.append(env_key_i)

    return keys


def _get_first_api_key() -> Optional[str]:
    """
    Return the first available Gemini API key (for backwards compatibility).
    """
    keys = _get_all_api_keys()
    return keys[0] if keys else None


def _clean_json_text(text: str) -> str:
    """
    Remove Markdown fences and surrounding whitespace from an LLM response.
    Keeps the content intact while making it easier to parse as JSON.
    """
    cleaned = text.strip()
    cleaned = str.replace(r"```json\s*", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = str.replace(r"```", "", cleaned, flags=re.MULTILINE)
    return cleaned.strip()


def _strip_trailing_commas(text: str) -> str:
    """
    Remove trailing commas before closing braces/brackets to repair minor JSON issues.
    This is a safe, conservative cleanup to handle common LLM formatting mistakes.
    """
    previous = None
    current = text
    while current != previous:
        previous = current
        current = str.replace(r",\s*([}\]])", r"\1", current)
    return current


def build_gemini_client():
    """
    Build a configured Gemini client. Raises when API key or library is missing.
    """
    api_key = _get_first_api_key()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

    if not api_key:
        raise ValueError("Gemini API key not found. Set GEMINI_API_KEY or GEMINI_API_KEY_1..4 in .env file")
    if genai is None:
        raise ImportError("google-generativeai or google-genai is not installed. Install with: pip install google-generativeai")

    # Only call configure for old API
    if not is_new_api:
        genai.configure(api_key=api_key)

    logger.info(f"Gemini client initialized with model {model_name} (using {genai_module})")
    return GeminiClient(model=model_name)


class GeminiClient:
    def __init__(self, model: str = "gemini-2.5-flash-lite"):
        self.model = model
        self.api_keys = _get_all_api_keys()
        self.current_key_index = 0
        self.client = None
        self.model_instance = None
        self.is_initialized = False
        
        # Try to initialize, but don't fail if API key is missing
        try:
            if self.api_keys:
                self._initialize_client()
                self.is_initialized = True
            else:
                logger.warning(f"No Gemini API keys found. Client will operate in mock mode.")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {str(e)}. Client will operate in mock mode.")

    def _initialize_client(self):
        """Initialize client with current API key"""
        if not self.api_keys or self.current_key_index >= len(self.api_keys):
            raise ValueError("No valid API keys available for Gemini")

        current_key = self.api_keys[self.current_key_index]

        if is_new_api:
            # New SDK (google-genai): Create client directly
            self.client = genai.Client(api_key=current_key)
            self.model_instance = self.client.models.generate_content
        else:
            # Old SDK (google-generativeai): Configure and create model
            genai.configure(api_key=current_key)
            self.client = genai.GenerativeModel(self.model)
            self.model_instance = self.client.generate_content

        logger.info(f"Initialized Gemini client with API key {self.current_key_index + 1}/{len(self.api_keys)} (API: {'new' if is_new_api else 'old'})")

    def _rotate_api_key(self):
        """Rotate to next available API key"""
        self.current_key_index += 1
        if self.current_key_index >= len(self.api_keys):
            raise ValueError("All API keys exhausted")
        self._initialize_client()
        logger.info(f"Rotated to API key {self.current_key_index + 1}/{len(self.api_keys)}")

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate content with automatic API key rotation on quota exceeded."""
        max_retries = len(self.api_keys)
        attempt = 0

        while attempt < max_retries:
            try:
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens
                }

                if is_new_api:
                    # New SDK: Call models.generate_content directly
                    response = self.client.models.generate_content(
                        model=self.model,
                        contents=prompt,
                        config=generation_config
                    )
                    response_text = response.text if hasattr(response, 'text') else str(response)
                else:
                    # Old SDK: Use GenerativeModel
                    response = self.client.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    response_text = response.text if hasattr(response, 'text') else str(response)

                if not response_text:
                    raise ValueError("Empty response from LLM")

                return response_text

            except Exception as e:
                error_str = str(e)

                # Check if it's a quota/rate limit error
                if any(quota_indicator in error_str for quota_indicator in [
                    "429", "quota", "rate limit", "exceeded", "per_minute", "per_day"
                ]):
                    logger.warning(f"Quota exceeded on key {self.current_key_index + 1}: {error_str}")
                    attempt += 1

                    if attempt < max_retries:
                        try:
                            self._rotate_api_key()
                            logger.info(f"Retrying with next API key ({self.current_key_index + 1}/{len(self.api_keys)})")
                            continue
                        except ValueError as rotate_error:
                            raise ValueError(f"All API keys exhausted or invalid: {rotate_error}")
                    else:
                        raise ValueError(f"All {len(self.api_keys)} API keys quota exceeded. Please wait before retrying.")
                else:
                    # Non-quota errors should fail immediately
                    logger.error(f"LLM API error: {error_str}")
                    raise ValueError(f"Failed to generate content from LLM: {error_str}")

        raise ValueError("Failed to generate content after all retries")

    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        try:
            cleaned = _clean_json_text(response_text)
            candidates = [cleaned]

            # If the response contains other text, try extracting the first JSON object
            json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if json_match:
                candidates.append(json_match.group(0))

            last_error = None
            for candidate in candidates:
                try:
                    repaired = _strip_trailing_commas(candidate)
                    parsed_json = json.loads(repaired)
                    if not isinstance(parsed_json, dict):
                        raise ValueError("LLM response is not a valid JSON object")
                    return parsed_json
                except json.JSONDecodeError as parse_error:
                    # Try to find nested JSON objects if main parsing fails
                    try:
                        # Find all { } pairs and try parsing from innermost
                        nested_matches = re.findall(r"\{[^{}]*\}", candidate)
                        for nested in nested_matches:
                            try:
                                parsed_json = json.loads(nested)
                                if isinstance(parsed_json, dict):
                                    return parsed_json
                            except json.JSONDecodeError:
                                continue
                    except Exception :
                        pass
                    last_error = parse_error
                    continue
                except Exception as parse_error:
                    last_error = parse_error
                    continue

            raise ValueError(f"Invalid JSON in LLM response: {last_error}")

        except Exception as e:
            logger.error(f"Response extraction error: {str(e)}")
            raise ValueError(f"Failed to extract JSON from LLM response: {str(e)}")

    def validate_response_fields(self, response: Dict[str, Any], required_fields: list) -> None:
        missing_fields = [field for field in required_fields if field not in response]

        if missing_fields:
            raise ValueError(f"LLM response missing required fields: {missing_fields}")

    def generate_structured_json(
        self,
        prompt: str,
        required_fields: list,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate and parse a JSON response with consistent validation and parsing safeguards.
        """
        response_text = self.generate_content(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        result = self.extract_json_from_response(response_text)
        self.validate_response_fields(result, required_fields)
        return result


def extract_json(text: str) -> Dict[str, Any]:
    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        return json.loads(json_match.group(0))
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")
