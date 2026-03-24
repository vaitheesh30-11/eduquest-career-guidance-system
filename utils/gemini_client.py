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
import time
import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, Optional
from utils.cache_utils import TTLCache
from utils.logging_utils import log_event

logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv

    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

try:
    from ml.observability import trace_block
except ModuleNotFoundError:
    from observability import trace_block

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
    cleaned = re.sub(r"```json\s*", "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    cleaned = re.sub(r"```", "", cleaned, flags=re.MULTILINE)
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
        current = re.sub(r",\s*([}\]])", r"\1", current)
    return current


def _safe_int(value: Any) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def _truncate_text(text: str, limit: int = 1200) -> str:
    if not isinstance(text, str):
        return str(text)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}... [truncated {len(text) - limit} chars]"


def _extract_usage_metrics(response: Any) -> Dict[str, Optional[int]]:
    usage_candidates = []
    for attr_name in ("usage_metadata", "usage"):
        usage_obj = getattr(response, attr_name, None)
        if usage_obj is not None:
            usage_candidates.append(usage_obj)

    for serializer_name in ("to_dict", "model_dump"):
        serializer = getattr(response, serializer_name, None)
        if callable(serializer):
            try:
                payload = serializer()
                if isinstance(payload, dict):
                    usage_candidates.append(payload.get("usage_metadata"))
                    usage_candidates.append(payload.get("usage"))
                    usage_candidates.append(payload)
            except Exception:
                pass

    def _lookup(source: Any, *keys: str) -> Optional[int]:
        if source is None:
            return None
        if isinstance(source, dict):
            for key in keys:
                value = source.get(key)
                parsed = _safe_int(value)
                if parsed is not None:
                    return parsed
            return None
        for key in keys:
            value = getattr(source, key, None)
            parsed = _safe_int(value)
            if parsed is not None:
                return parsed
        return None

    prompt_tokens = None
    completion_tokens = None
    total_tokens = None
    thought_tokens = None
    cached_tokens = None
    for candidate in usage_candidates:
        prompt_tokens = prompt_tokens or _lookup(
            candidate,
            "prompt_token_count",
            "input_token_count",
            "input_tokens",
            "prompt_tokens",
        )
        completion_tokens = completion_tokens or _lookup(
            candidate,
            "candidates_token_count",
            "output_token_count",
            "output_tokens",
            "completion_tokens",
        )
        total_tokens = total_tokens or _lookup(
            candidate,
            "total_token_count",
            "total_tokens",
        )
        thought_tokens = thought_tokens or _lookup(
            candidate,
            "thoughts_token_count",
            "reasoning_token_count",
            "reasoning_tokens",
        )
        cached_tokens = cached_tokens or _lookup(
            candidate,
            "cached_content_token_count",
            "cached_tokens",
        )

    if total_tokens is None and (prompt_tokens is not None or completion_tokens is not None):
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "thought_tokens": thought_tokens,
        "cached_tokens": cached_tokens,
    }


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
    _response_cache = TTLCache(
        ttl_seconds=max(0, int(os.getenv("EDUQUEST_LLM_CACHE_TTL_SECONDS", "1800"))),
        max_entries=max(1, int(os.getenv("EDUQUEST_LLM_CACHE_MAX_ENTRIES", "256"))),
    )
    _structured_response_cache = TTLCache(
        ttl_seconds=max(0, int(os.getenv("EDUQUEST_STRUCTURED_CACHE_TTL_SECONDS", os.getenv("EDUQUEST_LLM_CACHE_TTL_SECONDS", "1800")))),
        max_entries=max(1, int(os.getenv("EDUQUEST_STRUCTURED_CACHE_MAX_ENTRIES", os.getenv("EDUQUEST_LLM_CACHE_MAX_ENTRIES", "256")))),
    )

    def __init__(self, model: str = "gemini-2.5-flash-lite"):
        self.model = model
        self.api_keys = _get_all_api_keys()
        self.current_key_index = 0
        self.client = None
        self.model_instance = None
        self.is_initialized = False
        self.last_error = None
        self._session_metrics = self._new_session_metrics()
        
        # Try to initialize, but don't fail if API key is missing
        try:
            if self.api_keys:
                self._initialize_client()
                self.is_initialized = True
                self.last_error = None
            else:
                self.last_error = "No Gemini API keys found"
                logger.warning(f"No Gemini API keys found. Client will operate in mock mode.")
                log_event(logger, 30, "gemini_mock_mode", reason="no_api_keys")
        except Exception as e:
            self.last_error = str(e)
            logger.warning(f"Failed to initialize Gemini client: {str(e)}. Client will operate in mock mode.")
            log_event(logger, 30, "gemini_init_failed", error=str(e))

    def _new_session_metrics(self) -> Dict[str, Any]:
        return {
            "request_id": None,
            "workflow_name": None,
            "model": self.model,
            "sdk": genai_module,
            "session_started_at": None,
            "llm_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency_seconds": 0.0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "total_thought_tokens": 0,
            "total_cached_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "structured_cache_hits": 0,
            "structured_cache_misses": 0,
            "calls": [],
        }

    def reset_session_metrics(
        self,
        *,
        request_id: str | None = None,
        workflow_name: str | None = None,
    ) -> None:
        self._session_metrics = self._new_session_metrics()
        self._session_metrics["request_id"] = request_id
        self._session_metrics["workflow_name"] = workflow_name
        self._session_metrics["session_started_at"] = time.time()
        if self.api_keys:
            self.current_key_index = 0
            try:
                self._initialize_client()
            except Exception as exc:
                self.last_error = str(exc)

    def get_session_metrics(self) -> Dict[str, Any]:
        metrics = deepcopy(self._session_metrics)
        llm_calls = metrics.get("llm_calls", 0) or 0
        successful_calls = metrics.get("successful_calls", 0) or 0
        session_started_at = metrics.get("session_started_at")
        metrics["cache_hit_rate"] = round((metrics.get("cache_hits", 0) / llm_calls), 4) if llm_calls else 0.0
        structured_checks = (metrics.get("structured_cache_hits", 0) + metrics.get("structured_cache_misses", 0))
        metrics["structured_cache_hit_rate"] = round((metrics.get("structured_cache_hits", 0) / structured_checks), 4) if structured_checks else 0.0
        metrics["success_rate"] = round((successful_calls / llm_calls), 4) if llm_calls else 0.0
        metrics["average_latency_seconds"] = round((metrics.get("total_latency_seconds", 0.0) / llm_calls), 4) if llm_calls else 0.0
        metrics["average_tokens_per_call"] = round((metrics.get("total_tokens", 0) / llm_calls), 2) if llm_calls else 0.0
        metrics["response_cache"] = GeminiClient._response_cache.stats()
        metrics["structured_cache"] = GeminiClient._structured_response_cache.stats()
        if session_started_at:
            metrics["session_elapsed_seconds"] = round(time.time() - float(session_started_at), 4)
        else:
            metrics["session_elapsed_seconds"] = 0.0
        return metrics

    def _record_call_metrics(self, call_summary: Dict[str, Any]) -> None:
        usage = call_summary.get("usage", {})
        self._session_metrics["llm_calls"] += 1
        if call_summary.get("status") == "success":
            self._session_metrics["successful_calls"] += 1
        else:
            self._session_metrics["failed_calls"] += 1
        self._session_metrics["total_latency_seconds"] = round(
            self._session_metrics["total_latency_seconds"] + float(call_summary.get("latency_seconds", 0.0)),
            4,
        )
        self._session_metrics["total_prompt_tokens"] += usage.get("prompt_tokens") or 0
        self._session_metrics["total_completion_tokens"] += usage.get("completion_tokens") or 0
        self._session_metrics["total_tokens"] += usage.get("total_tokens") or 0
        self._session_metrics["total_thought_tokens"] += usage.get("thought_tokens") or 0
        self._session_metrics["total_cached_tokens"] += usage.get("cached_tokens") or 0
        if call_summary.get("cache_hit"):
            self._session_metrics["cache_hits"] += 1
        else:
            self._session_metrics["cache_misses"] += 1
        self._session_metrics["calls"].append(call_summary)

    def _cache_enabled(self) -> bool:
        return GeminiClient._response_cache.ttl_seconds > 0 and GeminiClient._response_cache.max_entries > 0

    def _structured_cache_enabled(self) -> bool:
        return (
            GeminiClient._structured_response_cache.ttl_seconds > 0
            and GeminiClient._structured_response_cache.max_entries > 0
        )

    def _build_cache_key(
        self,
        *,
        prompt: str,
        temperature: float,
        max_tokens: int,
        trace_metadata: Dict[str, Any],
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "agent_name": trace_metadata.get("agent_name"),
            "operation": trace_metadata.get("operation"),
            "response_format": trace_metadata.get("response_format"),
        }
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

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
        log_event(logger, 20, "gemini_initialized", key_index=self.current_key_index + 1, total_keys=len(self.api_keys), model=self.model, sdk=genai_module)

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
        *,
        trace_name: str | None = None,
        trace_tags: list[str] | None = None,
        trace_metadata: Dict[str, Any] | None = None,
    ) -> str:
        """Generate content with automatic API key rotation on quota exceeded."""
        if self.api_keys and self.current_key_index >= len(self.api_keys):
            self.current_key_index = 0
            self._initialize_client()

        max_retries = len(self.api_keys)
        attempt = 0
        trace_name = trace_name or "gemini_generate_content"
        trace_tags = list(trace_tags or [])
        trace_metadata = dict(trace_metadata or {})
        trace_metadata.update(
            {
                "llm_provider": "google_gemini",
                "model": self.model,
                "sdk": genai_module,
                "max_retries": max_retries,
            }
        )
        cache_key = self._build_cache_key(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            trace_metadata=trace_metadata,
        )

        with trace_block(
            trace_name,
            run_type="llm",
            inputs={
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            tags=["llm", "gemini", *trace_tags],
            metadata=trace_metadata,
        ) as run:
            if self._cache_enabled():
                cached_payload = GeminiClient._response_cache.get(cache_key)
                if cached_payload is not None:
                    response_text = cached_payload["response_text"]
                    usage = dict(cached_payload.get("usage") or {})
                    latency_seconds = 0.0
                    call_summary = {
                        "trace_name": trace_name,
                        "status": "success",
                        "attempt_count": 0,
                        "latency_seconds": latency_seconds,
                        "model": self.model,
                        "sdk": genai_module,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "prompt_chars": len(prompt),
                        "response_chars": len(response_text),
                        "usage": usage,
                        "agent_name": trace_metadata.get("agent_name"),
                        "operation": trace_metadata.get("operation"),
                        "cache_hit": True,
                    }
                    self._record_call_metrics(call_summary)
                    log_event(
                        logger,
                        20,
                        "gemini_cache_hit",
                        model=self.model,
                        trace_name=trace_name,
                        agent_name=trace_metadata.get("agent_name"),
                        operation=trace_metadata.get("operation"),
                    )
                    if run is not None:
                        run.end(
                            outputs={
                                "response_text": response_text,
                                "response_preview": _truncate_text(response_text, 800),
                                "usage": usage,
                                "latency_seconds": latency_seconds,
                                "attempt_count": 0,
                                "response_chars": len(response_text),
                                "cache_hit": True,
                            }
                        )
                    return response_text

            started_at = time.perf_counter()
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

                    latency_seconds = round(time.perf_counter() - started_at, 4)
                    usage = _extract_usage_metrics(response)
                    call_summary = {
                        "trace_name": trace_name,
                        "status": "success",
                        "attempt_count": attempt + 1,
                        "latency_seconds": latency_seconds,
                        "model": self.model,
                        "sdk": genai_module,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "prompt_chars": len(prompt),
                        "response_chars": len(response_text),
                        "usage": usage,
                        "agent_name": trace_metadata.get("agent_name"),
                        "operation": trace_metadata.get("operation"),
                        "cache_hit": False,
                    }
                    self._record_call_metrics(call_summary)
                    self.last_error = None
                    if self._cache_enabled():
                        GeminiClient._response_cache.set(
                            cache_key,
                            {
                                "response_text": response_text,
                                "usage": usage,
                            },
                        )
                        log_event(
                            logger,
                            20,
                            "gemini_cache_store",
                            model=self.model,
                            trace_name=trace_name,
                            agent_name=trace_metadata.get("agent_name"),
                            operation=trace_metadata.get("operation"),
                        )
                    if run is not None:
                        run.end(
                            outputs={
                                "response_text": response_text,
                                "response_preview": _truncate_text(response_text, 800),
                                "usage": usage,
                                "latency_seconds": latency_seconds,
                                "attempt_count": attempt + 1,
                                "response_chars": len(response_text),
                            }
                        )
                    return response_text

                except Exception as e:
                    error_str = str(e)
                    recoverable_key_error = any(indicator in error_str for indicator in [
                        "API_KEY_INVALID",
                        "API key not valid",
                        "invalid api key",
                        "invalid argument",
                    ])

                    # Check if it's a quota/rate limit error
                    if any(quota_indicator in error_str for quota_indicator in [
                        "429", "quota", "rate limit", "exceeded", "per_minute", "per_day"
                    ]) or recoverable_key_error:
                        self.last_error = error_str
                        logger.warning(f"Recoverable Gemini key error on key {self.current_key_index + 1}: {error_str}")
                        log_event(logger, 30, "gemini_recoverable_key_issue", key_index=self.current_key_index + 1, error=error_str)
                        attempt += 1

                        if attempt < max_retries:
                            try:
                                self._rotate_api_key()
                                logger.info(f"Retrying with next API key ({self.current_key_index + 1}/{len(self.api_keys)})")
                                continue
                            except ValueError as rotate_error:
                                error_str = f"All API keys exhausted or invalid: {rotate_error}"
                        else:
                            error_str = f"All {len(self.api_keys)} API keys were exhausted, invalid, or quota-limited. Please update your keys or retry later."
                    else:
                        # Non-quota errors should fail immediately
                        self.last_error = error_str
                        logger.error(f"LLM API error: {error_str}")
                        log_event(logger, 40, "gemini_api_call_failed", key_index=self.current_key_index + 1, error=error_str)
                        error_str = f"Failed to generate content from LLM: {error_str}"

                    latency_seconds = round(time.perf_counter() - started_at, 4)
                    call_summary = {
                        "trace_name": trace_name,
                        "status": "error",
                        "attempt_count": attempt + 1,
                        "latency_seconds": latency_seconds,
                        "model": self.model,
                        "sdk": genai_module,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "prompt_chars": len(prompt),
                        "response_chars": 0,
                        "usage": _extract_usage_metrics(None),
                        "agent_name": trace_metadata.get("agent_name"),
                        "operation": trace_metadata.get("operation"),
                        "error": error_str,
                        "cache_hit": False,
                    }
                    self._record_call_metrics(call_summary)
                    if run is not None:
                        run.end(
                            error=error_str,
                            outputs={
                                "latency_seconds": latency_seconds,
                                "attempt_count": attempt + 1,
                            },
                        )
                    raise ValueError(error_str)

        raise ValueError("Failed to generate content after all retries")

    def debug_status(self) -> Dict[str, Any]:
        return {
            "is_initialized": self.is_initialized,
            "model": self.model,
            "sdk": genai_module,
            "api_keys_detected": len(self.api_keys),
            "current_key_index": self.current_key_index + 1 if self.api_keys else 0,
            "last_error": self.last_error,
        }

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
        max_tokens: int = 2000,
        *,
        trace_name: str | None = None,
        trace_tags: list[str] | None = None,
        trace_metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Generate and parse a JSON response with consistent validation and parsing safeguards.
        """
        trace_name = trace_name or "gemini_generate_structured_json"
        trace_tags = list(trace_tags or [])
        trace_metadata = dict(trace_metadata or {})
        structured_trace_metadata = {
            **trace_metadata,
            "response_format": "json",
        }
        cache_key = self._build_cache_key(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            trace_metadata=structured_trace_metadata,
        )
        with trace_block(
            trace_name,
            run_type="chain",
            inputs={
                "required_fields": required_fields,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            tags=["llm", "structured-json", *trace_tags],
            metadata=trace_metadata,
        ) as run:
            if self._structured_cache_enabled():
                cached_result = GeminiClient._structured_response_cache.get(cache_key)
                if cached_result is not None:
                    self._session_metrics["structured_cache_hits"] += 1
                    if run is not None:
                        run.end(
                            outputs={
                                "structured_response": cached_result,
                                "required_fields": required_fields,
                                "validated_field_count": len(required_fields),
                                "cache_hit": True,
                            }
                        )
                    log_event(
                        logger,
                        20,
                        "gemini_structured_cache_hit",
                        trace_name=trace_name,
                        agent_name=trace_metadata.get("agent_name"),
                    )
                    return deepcopy(cached_result)

                self._session_metrics["structured_cache_misses"] += 1
            response_text = self.generate_content(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                trace_name=f"{trace_name}.raw_generation",
                trace_tags=trace_tags,
                trace_metadata={
                    **trace_metadata,
                    "operation": "raw_generation",
                    "response_format": "json",
                },
            )
            result = self.extract_json_from_response(response_text)
            self.validate_response_fields(result, required_fields)
            if self._structured_cache_enabled():
                GeminiClient._structured_response_cache.set(cache_key, deepcopy(result))
                log_event(
                    logger,
                    20,
                    "gemini_structured_cache_store",
                    trace_name=trace_name,
                    agent_name=trace_metadata.get("agent_name"),
                )
            if run is not None:
                run.end(
                    outputs={
                        "structured_response": result,
                        "required_fields": required_fields,
                        "validated_field_count": len(required_fields),
                        "cache_hit": False,
                    }
                )
            return result


def extract_json(text: str) -> Dict[str, Any]:
    try:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        return json.loads(json_match.group(0))
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")
