"""Roadmap Builder Medium LLM Agent - MEDIUM path quarterly roadmap."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, roadmap_theme



class RoadmapBuilderMediumLLMAgent(BaseLLMAgent):
    def generate_roadmap(
        self,
        profile: Dict[str, Any],
        ml_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        career = profile.get("career_field", "this career")
        theme = roadmap_theme(career_track(career))
        prompt = f"Create a medium-depth roadmap for {career}."

        try:
            self.generate(prompt, temperature=0.5,max_tokens=900)

            return {
                "q1": {"goals": [f"Learn {item}" for item in theme["foundation"][:2]], "actions": ["Courses", "Weekly practice"]},
                "q2": {"goals": [f"Build {item}" for item in theme["build"][:2]], "actions": ["Practice", "Mini-projects"]},
                "q3": {"goals": [f"Refine {item}" for item in theme["build"][1:3]], "actions": ["Portfolio updates", "Mock reviews"]},
                "q4": {"goals": [f"Prepare for {career} interviews", f"Convert {theme['launch'][0]} into evidence"], "actions": ["Apply jobs", "Network"]},
                "key_milestones": [
                    f"First {career} project completed",
                    "Portfolio updated",
                    "Interview-ready stories prepared"
                ],
                "critical_resources": [
                    "Courses",
                    "Communities",
                    "Mentorship"
                ],
                "status": "success"
            }

        except Exception:

            return {
                "q1": {"goals": []},
                "q2": {"goals": []},
                "q3": {"goals": []},
                "q4": {"goals": []},
                "key_milestones": [],
                "resources": [],
                "status": "fallback"
            }
