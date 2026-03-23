"""Roadmap Builder Full Node - HARD path."""

from state import EduQuestState
from agents.roadmap_builder_full_llm import RoadmapBuilderFullLLMAgent

def roadmap_builder_full_node(state: EduQuestState, client) -> dict:
    """Return only modified fields."""
    try:
        agent = RoadmapBuilderFullLLMAgent(client)
        profile = state.get("extracted_profile", {})
        ml_results = {
            "viability_score": state.get("viability_score"),
            "academic_fit_score": state.get("academic_fit_score"),
        }
        result = agent.generate_roadmap(profile, ml_results)
        return {"roadmap_output": result}
    except Exception as e:
        return {"roadmap_output": {"error": str(e)}}

    return state
