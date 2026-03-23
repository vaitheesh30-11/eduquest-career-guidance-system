"""Profile Extractor Node - extracts structured profile from free text."""

from typing import Dict, Any
from state import EduQuestState
from agents.profile_extractor_llm import ProfileExtractorLLMAgent


def profile_extractor_node(state : EduQuestState , client) -> dict:
    """Return only modified fields."""
    try:
        agent = ProfileExtractorLLMAgent(client)
        raw = state.get("raw_inputs",{})
        result = agent.extract_profile(raw)
        
        return {"extracted_profile": result}

    except Exception as e:
        return {"extracted_profile": {"status" : "error" , "message" : str(e)}}
