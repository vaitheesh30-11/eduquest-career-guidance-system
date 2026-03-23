"""Reality Check Full Node - HARD path."""

from state import EduQuestState
from agents.reality_check_full_llm import RealityCheckFullLLMAgent

def reality_check_full_node(state: EduQuestState,client)->dict:
    """Return only modified fields."""
    try:
        agent = RealityCheckFullLLMAgent(client)
        profile = state.get("extracted_profile", {})
        result = agent.generate_reality_check({
            **profile,
            "viability_score": state.get("viability_score", 0.5),
            "academic_fit_score": state.get("academic_fit_score", 50.0),
        })
        return {"reality_check_output": result}
    except Exception as e :
        return {"reality_check_output": {"error":str(e)}}
