"""Shared LangSmith observability helpers for ML workflows."""

from __future__ import annotations

import os
from contextlib import nullcontext
from typing import Any, Dict, Iterable

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

try:
    from langsmith.run_helpers import trace, tracing_context
except Exception:  # pragma: no cover
    trace = None
    tracing_context = None


def _load_env() -> None:
    if load_dotenv is not None:
        load_dotenv()


def _is_truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def langsmith_enabled() -> bool:
    _load_env()
    tracing_flag = _is_truthy(os.getenv("LANGSMITH_TRACING")) or _is_truthy(
        os.getenv("LANGCHAIN_TRACING_V2")
    )
    return bool(
        trace is not None
        and tracing_context is not None
        and tracing_flag
        and os.getenv("LANGSMITH_API_KEY")
    )


def langsmith_project(default: str = "eduquest-ml-training") -> str:
    _load_env()
    return os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT") or default


def _clean_dict(payload: Dict[str, Any] | None) -> Dict[str, Any]:
    if not payload:
        return {}
    clean: Dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            clean[key] = value
        elif isinstance(value, (list, tuple)):
            clean[key] = [str(item) for item in value]
        else:
            clean[key] = str(value)
    return clean


def tracing_session(
    *,
    project_name: str | None = None,
    tags: Iterable[str] | None = None,
    metadata: Dict[str, Any] | None = None,
):
    if not langsmith_enabled():
        return nullcontext()
    return tracing_context(
        enabled=True,
        project_name=project_name or langsmith_project(),
        tags=list(tags or []),
        metadata=_clean_dict(metadata),
    )


def trace_block(
    name: str,
    *,
    run_type: str = "chain",
    inputs: Dict[str, Any] | None = None,
    tags: Iterable[str] | None = None,
    metadata: Dict[str, Any] | None = None,
    project_name: str | None = None,
):
    if not langsmith_enabled():
        return nullcontext()
    return trace(
        name=name,
        run_type=run_type,
        project_name=project_name or langsmith_project(),
        inputs=_clean_dict(inputs),
        tags=list(tags or []),
        metadata=_clean_dict(metadata),
    )
