from contextlib import contextmanager

import graph as graph_module


class DummyRun:
    def end(self, *args, **kwargs):
        return None


@contextmanager
def dummy_trace_block(*args, **kwargs):
    yield DummyRun()


@contextmanager
def dummy_tracing_session(*args, **kwargs):
    yield None


class DummyClient:
    def reset_session_metrics(self, **kwargs):
        return None

    def debug_status(self):
        return {"status": "ok"}

    def get_session_metrics(self):
        return {
            "request_id": "dummy",
            "workflow_name": "eduquest_assessment",
            "model": "mock",
            "sdk": "mock",
            "llm_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "total_latency_seconds": 0.0,
            "cache_hits": 0,
            "cache_hit_rate": 0.0,
            "structured_cache_hits": 0,
            "structured_cache_hit_rate": 0.0,
            "success_rate": 0.0,
        }


class DummyCompiledGraph:
    def __init__(self, tracker):
        self.tracker = tracker

    def invoke(self, state):
        self.tracker["invoke_count"] += 1
        return {
            "request_id": state.get("request_id"),
            "analysis_timestamp": state.get("analysis_timestamp"),
            "path_taken": "LIGHT_PATH",
            "viability_score": 0.55,
            "academic_fit_score": 67.0,
            "overall_feasibility": 0.61,
            "aggregated_output": {"summary": "cached assessment"},
            "viability_ml_observability": {
                "node": "career_viability_scorer_node",
                "status": "success",
                "latency_seconds": 0.01,
                "prediction": 0.55,
                "model_name": "Pipeline",
                "used_trained_model": True,
            },
            "academic_ml_observability": {
                "node": "academic_career_matcher_node",
                "status": "success",
                "latency_seconds": 0.02,
                "prediction": 67.0,
                "model_name": "Pipeline",
                "used_trained_model": True,
            },
        }


def test_assessment_cache_skips_second_graph_invoke(monkeypatch):
    tracker = {"invoke_count": 0}
    graph_module._assessment_cache.clear()

    monkeypatch.setattr(graph_module, "trace_block", dummy_trace_block)
    monkeypatch.setattr(graph_module, "tracing_session", dummy_tracing_session)
    monkeypatch.setattr(graph_module, "GeminiClient", lambda: DummyClient())
    monkeypatch.setattr(graph_module, "build_eduquest_graph", lambda client: DummyCompiledGraph(tracker))
    monkeypatch.setattr(graph_module, "get_initial_state", lambda form_data: dict(form_data))

    form_data = {
        "dream_career": "Software Engineer",
        "current_academics": "B.Tech CSE",
        "constraints": "Moderate budget",
        "interests": "AI, backend systems",
        "other_concerns": "Need stable income",
    }

    first = graph_module.assess_career(dict(form_data))
    second = graph_module.assess_career(dict(form_data))

    assert tracker["invoke_count"] == 1
    assert first["performance_summary"]["served_from_assessment_cache"] is False
    assert second["performance_summary"]["served_from_assessment_cache"] is True
    assert second["workflow_observability"]["served_from_assessment_cache"] is True
    assert second["aggregated_output"] == first["aggregated_output"]

    graph_module._assessment_cache.clear()
