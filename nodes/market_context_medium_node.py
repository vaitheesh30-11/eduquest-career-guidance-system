"""Market Context Medium Node - MEDIUM path."""

from state import EduQuestState
from agents.market_context_medium_llm import MarketContextMediumLLMAgent



def market_context_medium_node(state:EduQuestState , client) -> dict:
    """Return only modified fields."""
    try:
        agent = MarketContextMediumLLMAgent(client)
        profile = state.get("extracted_profile", {})
        career = profile.get("career_field") or state.get("career_field") or state.get("dream_career")
        budget = profile.get("budget_constraints", "Moderate")
        result = agent.get_market_context(career, budget)
        return {"market_context_medium": result}
    
    except Exception as e:
        return {"market_context_medium": {"status": "error","message":str(e)}}
