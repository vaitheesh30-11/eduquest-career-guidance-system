"""Market Context Full Node - HARD path."""

from state import EduQuestState
from agents.market_context_full_llm import MarketContextFullLLMAgent



def market_context_full_node(state:EduQuestState , client) -> dict:
    """Return only modified fields."""
    try:
        agent = MarketContextFullLLMAgent(client)
        profile = state.get("extracted_profile", {})
        career = profile.get("career_field") or state.get("career_field") or state.get("dream_career")
        budget = profile.get("budget_constraints", "Moderate")
        result = agent.get_market_context(career, budget)
        return {"market_context": result}
    
    except Exception as e:
        return {"market_context": {"status": "error","message":str(e)}}
