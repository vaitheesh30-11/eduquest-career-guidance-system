"""Roadmap Builder Full LLM Agent - HARD path detailed roadmap."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, learning_mode, roadmap_theme


ONLINE_COURSES="Online courses"

class RoadmapBuilderFullLLMAgent(BaseLLMAgent):

    def generate_roadmap(
        self,
        profile: Dict[str, Any],
        ml_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        career = profile.get("career_field", "this career")
        track = career_track(career)
        theme = roadmap_theme(track)
        mode = learning_mode(profile.get("constraints_summary", ""))
        viability = ml_results.get("viability_score", 0.5)
        foundation_duration = "1-3" if mode == "focused" else "1-4"
        build_duration = "4-7" if viability >= 0.6 else "4-8"
        launch_duration = "8-12" if mode == "focused" else "9-14"
        prompt = f"Generate a detailed roadmap for {career}."

        try:
            self.generate(prompt, temperature=0.5,max_tokens=1500)

            return{
                "phase_1_months": {
                    "months": foundation_duration,
                    "goals": [f"Build {item}" for item in theme["foundation"]],
                    "actions": [ONLINE_COURSES, "Structured weekly study plan", "Foundational practice tasks"],
                },
                "phase_2_months": {
                    "months": build_duration,
                    "goals": [f"Strengthen {item}" for item in theme["build"]],
                    "actions": ["Build guided projects", "Collect portfolio evidence", "Review gaps monthly"],
                },
                "phase_3_months": {
                    "months": launch_duration,
                    "goals": [f"Convert {item} into job-ready proof" for item in theme["launch"]],
                    "actions": ["Interview preparation", "Referral and networking outreach", f"Target {career} roles weekly"],
                },
                "key_milestones": [
                    f"Complete first {career} proof-of-skill project",
                    "Portfolio or case-study set ready",
                    "Resume aligned to target role",
                    "Consistent interview pipeline established",
                ],
                "success_resources": [
                    ONLINE_COURSES,
                    "Communities",
                    "Mentorship",
                    "Interview question bank",
                ],
                "status": "success"
            }
        except Exception:

            return {
                "phase_1_months": {
                    "goals": [f"Build {theme['foundation'][0]}"],
                    "actions": ["Courses"]
                },
                "phase_2_months": {
                    "goals": [f"Strengthen {theme['build'][0]}"],
                    "actions": ["Projects"]
                },
                "phase_3_months": {
                    "goals": [f"Launch toward {career} roles"],
                    "actions": ["Networking"]
                },
                "key_milestones":["Portfolio"],
                "success_resources": [ONLINE_COURSES],
                "status": "fallback"
            }
