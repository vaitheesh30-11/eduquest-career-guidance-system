"""Roadmap Builder Full LLM Agent - HARD path detailed roadmap."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, learning_mode, roadmap_theme


ONLINE_COURSES="Online courses"

class RoadmapBuilderFullLLMAgent(BaseLLMAgent):
    def _extract_points(self, text: str, limit: int = 12):
        points = []
        for line in (text or "").splitlines():
            item = line.strip().lstrip("-*0123456789. ").strip()
            if item and len(item) > 6:
                points.append(item)
            if len(points) >= limit:
                break
        return points

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
        prompt = f"""
        Generate a detailed roadmap for {career}.
        Return only valid JSON with this exact shape:
        {{
          "phase_1_months": {{"months": "string", "goals": ["string"], "actions": ["string"]}},
          "phase_2_months": {{"months": "string", "goals": ["string"], "actions": ["string"]}},
          "phase_3_months": {{"months": "string", "goals": ["string"], "actions": ["string"]}},
          "key_milestones": ["string"],
          "success_resources": ["string"],
          "strategy_summary": "string",
          "phase_success_signals": ["string"],
          "weekly_routine": ["string"]
        }}

        Context:
        - learning_mode: {mode}
        - viability_score: {viability}
        - preferred_phase_windows: {foundation_duration}, {build_duration}, {launch_duration}
        """

        try:
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=[
                    "phase_1_months",
                    "phase_2_months",
                    "phase_3_months",
                    "key_milestones",
                    "success_resources",
                    "strategy_summary",
                    "phase_success_signals",
                    "weekly_routine",
                ],
                temperature=0.5,
                max_tokens=1500,
            )

            return{
                "phase_1_months": result.get("phase_1_months", {}),
                "phase_2_months": result.get("phase_2_months", {}),
                "phase_3_months": result.get("phase_3_months", {}),
                "key_milestones": list(result.get("key_milestones", [])),
                "success_resources": list(result.get("success_resources", [])),
                "strategy_summary": str(result.get("strategy_summary", "")),
                "phase_success_signals": list(result.get("phase_success_signals", [])),
                "weekly_routine": list(result.get("weekly_routine", [])),
                "status": "success"
            }
        except Exception:
            try:
                raw = self.generate_direct(
                    prompt=f"Generate a detailed 3-phase roadmap for {career} with monthly windows, goals, actions, milestones, strategy summary and weekly routine.",
                    temperature=0.5,
                    max_tokens=1200,
                )
                points = self._extract_points(raw, limit=12)
                p1 = points[:3] if len(points) >= 3 else [f"Build {item}" for item in theme["foundation"]]
                p2 = points[3:6] if len(points) >= 6 else [f"Strengthen {item}" for item in theme["build"]]
                p3 = points[6:9] if len(points) >= 9 else [f"Convert {item} into job-ready proof" for item in theme["launch"]]
                return {
                    "phase_1_months": {"months": foundation_duration, "goals": p1, "actions": ["Structured study", "Mentor check-ins", "Practice tasks"]},
                    "phase_2_months": {"months": build_duration, "goals": p2, "actions": ["Project implementation", "Portfolio evidence", "Gap reviews"]},
                    "phase_3_months": {"months": launch_duration, "goals": p3, "actions": ["Mock interviews", "Applications", "Networking"]},
                    "key_milestones": points[:4] if points else [f"First {career} project complete", "Portfolio ready", "Interview readiness"],
                    "success_resources": ["Courses", "Mentors", "Communities", "Interview prep banks"],
                    "strategy_summary": raw[:260],
                    "phase_success_signals": points[4:7] if len(points) >= 7 else ["Weekly consistency", "Increasing project depth", "Interview confidence"],
                    "weekly_routine": points[7:10] if len(points) >= 10 else ["2 learning blocks", "2 project blocks", "1 review block"],
                    "status": "success",
                }
            except Exception:
                pass

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
                "strategy_summary": f"Move from fundamentals to evidence-backed applications for {career}.",
                "phase_success_signals": ["Weekly consistency", "Visible project output", "Interview readiness growth"],
                "weekly_routine": ["2 deep work study sessions", "2 practical implementation sessions", "1 reflection and correction session"],
                "status": "fallback"
            }
