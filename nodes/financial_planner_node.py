"""Financial Planner Node - HARD path only."""

from state import EduQuestState
from agents.financial_planner_llm import FinancialPlannerLLMAgent


def financial_planner_node(state, client)->dict:
    """Return only modified fields."""
    try:
        agent=FinancialPlannerLLMAgent(client)
        profile=state.get("extracted_profile", {})
        reality=state.get("reality_check_output", {})
        result=agent.generate_financial_plan(profile, reality)
        return {"financial_plan_output": result}
    
    except Exception as e:
        return {"financial_plan_output": {"status":"error", "message": str(e)}}
