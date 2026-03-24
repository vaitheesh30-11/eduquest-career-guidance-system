"""Career Viability Scorer Node - ML predictions."""

import time

from state import EduQuestState
from agents.career_viability_scorer_ml import CareerViabilityScorerMLAgent
from utils.logging_utils import get_logger, log_event
try:
    from ml.observability import trace_block
except ModuleNotFoundError:
    from observability import trace_block

logger = get_logger(__name__)


def career_viability_scorer_node(state: EduQuestState)->dict:
    """Return only modified fields to avoid concurrent update conflicts."""
    profile=state.get("extracted_profile",{})
    started = time.perf_counter()
    with trace_block(
        "career_viability_prediction",
        run_type="tool",
        inputs={"request_id": state.get("request_id"), "career_field": profile.get("career_field", "")},
        tags=["ml", "inference", "viability"],
        metadata={"node": "career_viability_scorer_node"},
    ) as run:
        try: 
            agent=CareerViabilityScorerMLAgent()
            log_event(logger, 20, "viability_prediction_started", request_id=state.get("request_id"), career_field=profile.get("career_field", ""))
            
            result=agent.predict_viability(profile)
            latency_seconds = round(time.perf_counter() - started, 4)
            monitoring = {
                "node": "career_viability_scorer_node",
                "model_name": type(agent.model).__name__ if agent.model is not None else "rule_based_fallback",
                "used_trained_model": bool(agent.model is not None),
                "status": result.get("status"),
                "latency_seconds": latency_seconds,
                "prediction": result.get("viability_score"),
            }
            
            log_event(logger, 20, "viability_prediction_completed", request_id=state.get("request_id"), career_field=profile.get("career_field", ""), result=result, monitoring=monitoring)
            
            if run is not None:
                run.end(outputs=monitoring)

            return {
                "viability_score": result.get("viability_score"),
                "viability_status": result.get("status"),
                "viability_ml_observability": monitoring,
            }

        except Exception as e:
            latency_seconds = round(time.perf_counter() - started, 4)
            log_event(logger, 40, "viability_prediction_failed", request_id=state.get("request_id"), career_field=profile.get("career_field", ""), error=str(e), latency_seconds=latency_seconds)
            monitoring = {
                "node": "career_viability_scorer_node",
                "model_name": "unknown",
                "used_trained_model": False,
                "status": "error",
                "latency_seconds": latency_seconds,
                "prediction": None,
                "error": str(e),
            }
            if run is not None:
                run.end(error=str(e), outputs=monitoring)
            return {
                "viability_score": None,
                "viability_status": "error",
                "viability_error": str(e),
                "viability_ml_observability": monitoring,
            }
