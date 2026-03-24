"""Profile Extractor Node - extracts structured profile from free text."""

from typing import Dict, Any
from state import EduQuestState
from agents.profile_extractor_llm import ProfileExtractorLLMAgent
from utils.logging_utils import get_logger, log_event

logger = get_logger(__name__)


def profile_extractor_node(state : EduQuestState , client) -> dict:
    """Return only modified fields."""
    try:
        agent = ProfileExtractorLLMAgent(client)
        raw = state.get("raw_inputs",{})
        dream_career = raw.get("dream_career", "")
        log_event(logger, 20, "profile_extraction_started", request_id=state.get("request_id"), career_field=dream_career)
        
        result = agent.extract_profile(raw)
        log_event(
            logger,
            20,
            "profile_extraction_completed",
            request_id=state.get("request_id"),
            career_field=result.get("career_field", ""),
            extracted_profile=result,
        )
        
        return {"extracted_profile": result}

    except Exception as e:
        log_event(logger, 40, "profile_extraction_failed", request_id=state.get("request_id"), error=str(e))
        return {"extracted_profile": {"status" : "error" , "message" : str(e)}}
