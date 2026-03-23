"""Output Aggregator Node - Aggregates outputs based on path taken."""

from state import EduQuestState


def output_aggregator_node(state : EduQuestState) -> dict:
    """Return only modified fields."""
    try:
        final_output = {
            "profile" : state.get("extracted_profile"),
            "viability_score" : state.get("viability_score"),
            "academic_fit_score" : state.get("academic_fit_score"),
            "market_context" : state.get("market_context"),
            "reality_check": state.get("reality_check_output"),
            "roadmap":state.get("roadmap_output"),
            "financial_plan" : state.get("financial_plan_output"),
            "alternatives":state.get("alternatives_output"),
        }
        return {"aggregated_output": final_output}

    except Exception as e:
        return {"aggregated_output" : {"status" : "error" , "message":str(e)}}
