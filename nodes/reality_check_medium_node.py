"""Reality Check Medium Node - MEDIUM path."""

from state import EduQuestState
from agents.reality_check_medium_llm import RealityCheckMediumLLMAgent


def reality_check_medium_node(state:EduQuestState,client)->dict:
    """Return only modified fields."""
    try:
        agent = RealityCheckMediumLLMAgent(client)
        profile = state.get("extracted_profile", {})
        result = agent.generate_reality_check({
            **profile,
            "viability_score": state.get("viability_score", 0.5),
            "academic_fit_score": state.get("academic_fit_score", 50.0),
        })
        return {"reality_check_medium_output": result}
    except Exception as e :
        return {"reality_check_medium_output": {"error":str(e)}}
    
