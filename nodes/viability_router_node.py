"""Viability Router Node - pure logic node for path routing."""

from state import EduQuestState




def viability_router_node(state : EduQuestState) -> dict:
    """Return only modified fields."""
    score = state.get("viability_score",0)

    if score >= 0.6:
        path = "HARD_PATH"
    elif score >= 0.3:
        path = "MEDIUM_PATH"
    else:
        path = "LIGHT_PATH"
    
    return {"path_taken": path}
