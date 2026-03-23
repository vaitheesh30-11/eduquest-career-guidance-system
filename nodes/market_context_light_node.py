"""Market Context Light Node - EASY path."""

from state import EduQuestState
from agents.market_context_light_llm import MarketContextLightLLMAgent




def market_context_light_node(state:EduQuestState , client) -> dict:
    """Return only modified fields."""
    try:
        agent = MarketContextLightLLMAgent(client)
        profile = state.get("extracted_profile", {})
        career = profile.get("career_field") or state.get("career_field") or state.get("dream_career")
        budget = profile.get("budget_constraints", "Moderate")
        result = agent.get_market_context(career, budget)
        return {"market_context_light": result}
    
    except Exception as e:
        return {"market_context_light": {"status": "error","message":str(e)}}
