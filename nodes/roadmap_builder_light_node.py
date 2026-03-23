"""Roadmap Builder Light Node - EASY path."""

from state import EduQuestState
from agents.roadmap_builder_light_llm import RoadmapBuilderLightLLMAgent


def roadmap_builder_light_node(state: EduQuestState, client) -> dict:
    """Return only modified fields."""
    try:
        agent = RoadmapBuilderLightLLMAgent(client)
        profile = state.get("extracted_profile", {})
        ml_results = {
            "viability_score": state.get("viability_score"),
            "academic_fit_score": state.get("academic_fit_score"),
        }
        result = agent.generate_roadmap(profile, ml_results)
        return {"roadmap_light_output": result}
    except Exception as e:
        return {"roadmap_light_output": {"error": str(e)}}
