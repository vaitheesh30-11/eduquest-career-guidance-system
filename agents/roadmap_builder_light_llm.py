"""Roadmap Builder Light LLM Agent - EASY path 3-phase roadmap."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, roadmap_theme

TM="3 months"

class RoadmapBuilderLightLLMAgent(BaseLLMAgent):

    def generate_roadmap(
        self,
        profile: Dict[str, Any],
        ml_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        career = profile.get("career_field", "this career")
        theme = roadmap_theme(career_track(career))
        prompt = f"Create a light roadmap for {career}."

        try:
            self.generate(prompt, temperature=0.5,max_tokens=600)

            return{
                "phase_1_foundation": {
                    "duration": TM,
                    "focus": f"Basics for {career}",
                    "goals": [f"Learn {theme['foundation'][0]}", f"Practice {theme['foundation'][1]}"],
                    "actions": ["Learn fundamentals", "Follow a starter curriculum"],
                },
                "phase_2_foundation": {
                    "duration": TM,
                    "focus": "Practice",
                    "goals": [f"Build {theme['build'][0]}", f"Show {theme['build'][1]}"],
                    "actions": ["Build projects", "Document outcomes"],
                },
                "phase_3_foundation": {
                    "duration": TM,
                    "focus": "Job readiness",
                    "goals": [f"Prepare for {career} roles", f"Strengthen {theme['launch'][1]}"],
                    "actions": ["Apply internships", "Start interview prep"],
                },
                "key_milestones": [
                    "Complete course",
                    "Portfolio ready",
                ],
                "critical_resources": [
                    "Online learning",
                    "Community support",
                ],
                "status": "success"
            }
        except Exception:

             return{
                "phase_1_foundation": {
                    "duration": TM,
                },
                "phase_2_foundation": {
                    "duration": TM,
                },
                "phase_3_foundation": {
                    "duration": TM,
                },
                "key_milestones": [],
                "critical_resources": [],
                "status": "fallback",
            }
