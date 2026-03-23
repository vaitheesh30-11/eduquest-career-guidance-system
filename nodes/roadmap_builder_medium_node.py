"""Roadmap Builder Medium Node - MEDIUM path."""

from state import EduQuestState
from agents.roadmap_builder_medium_llm import RoadmapBuilderMediumLLMAgent


def roadmap_builder_medium_node(state: EduQuestState, client) -> dict:
    """Return only modified fields."""
    try:
        agent = RoadmapBuilderMediumLLMAgent(client)
        profile = state.get("extracted_profile", {})
        ml_results = {
            "viability_score": state.get("viability_score"),
            "academic_fit_score": state.get("academic_fit_score"),
        }
        result = agent.generate_roadmap(profile, ml_results)
        return {"roadmap_medium_output": result}
    except Exception as e:
        return {"roadmap_medium_output": {"error": str(e)}}
