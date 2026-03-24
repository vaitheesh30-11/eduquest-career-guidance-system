"""Alternative Explorer Node - HARD path only."""

from state import EduQuestState
from agents.alternative_explorer_llm import AlternativeExplorerLLMAgent
from utils.logging_utils import get_logger, log_event

logger = get_logger(__name__)


def alternative_explorer_node(state: EduQuestState, client)-> dict:
    """Return only modified fields."""
    try:
        agent=AlternativeExplorerLLMAgent(client)
        profile=state.get("extracted_profile",{})
        viability_score=state.get("viability_score", 0)
        career_field = profile.get("career_field", "")
        log_event(
            logger,
            20,
            "alternative_explorer_started",
            request_id=state.get("request_id"),
            career_field=career_field,
            viability_score=viability_score,
        )

        result=agent.explore_alternatives(profile, {"viability_score": viability_score})
        alternatives = result.get("alternatives", [])
        log_event(
            logger,
            20,
            "alternative_explorer_completed",
            request_id=state.get("request_id"),
            career_field=career_field,
            preview=[alt.get("career") for alt in alternatives[:2]],
            response_source=result.get("response_source"),
        )
        
        return {"alternatives_output": result}
        
    except Exception as e:
        log_event(logger, 40, "alternative_explorer_failed", request_id=state.get("request_id"), error=str(e))
        return {"alternatives_output": {"status":"error","message":str(e)}}
