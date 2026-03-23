"""Alternative Explorer Node - HARD path only."""

from state import EduQuestState
from agents.alternative_explorer_llm import AlternativeExplorerLLMAgent
 


def alternative_explorer_node(state: EduQuestState, client)-> dict:
    """Return only modified fields."""
    try:
        agent=AlternativeExplorerLLMAgent(client)
        profile=state.get("extracted_profile",{})
        viability_score=state.get("viability_score", 0)

        result=agent.explore_alternatives(profile, {"viability_score": viability_score})
        return {"alternatives_output": result}
        
    except Exception as e:
        return {"alternatives_output": {"status":"error","message":str(e)}}
