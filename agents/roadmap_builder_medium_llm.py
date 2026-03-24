"""Roadmap Builder Medium LLM Agent - MEDIUM path quarterly roadmap."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, roadmap_theme



class RoadmapBuilderMediumLLMAgent(BaseLLMAgent):
    def _extract_points(self, text: str, limit: int = 4):
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
        viability = ml_results.get("viability_score", 0.5)
        prompt = f"""
        Create a medium-depth 12-month roadmap for {career}.
        Return only valid JSON with this exact shape:
        {{
          "q1": {{"goals": ["string"], "actions": ["string"]}},
          "q2": {{"goals": ["string"], "actions": ["string"]}},
          "q3": {{"goals": ["string"], "actions": ["string"]}},
          "q4": {{"goals": ["string"], "actions": ["string"]}},
          "key_milestones": ["string"],
          "critical_resources": ["string"],
          "strategy_summary": "string",
          "phase_success_signals": ["string"],
          "weekly_routine": ["string"]
        }}
        Context:
        - viability_score: {viability}
        - career_track: {track}
        """

        try:
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=[
                    "q1",
                    "q2",
                    "q3",
                    "q4",
                    "key_milestones",
                    "critical_resources",
                    "strategy_summary",
                    "phase_success_signals",
                    "weekly_routine",
                ],
                temperature=0.5,
                max_tokens=1100,
            )

            return {
                "q1": result.get("q1", {}),
                "q2": result.get("q2", {}),
                "q3": result.get("q3", {}),
                "q4": result.get("q4", {}),
                "key_milestones": list(result.get("key_milestones", [])),
                "critical_resources": list(result.get("critical_resources", [])),
                "strategy_summary": str(result.get("strategy_summary", "")),
                "phase_success_signals": list(result.get("phase_success_signals", [])),
                "weekly_routine": list(result.get("weekly_routine", [])),
                "status": "success"
            }

        except Exception:
            try:
                raw = self.generate_direct(
                    prompt=f"Create a quarter-wise 12-month actionable roadmap for {career} with goals, actions, milestones, weekly routine and progress signals.",
                    temperature=0.5,
                    max_tokens=900,
                )
                points = self._extract_points(raw, limit=10)
                q1 = points[:2] if len(points) >= 2 else [f"Learn {theme['foundation'][0]}", f"Practice {theme['foundation'][1]}"]
                q2 = points[2:4] if len(points) >= 4 else [f"Build {theme['build'][0]}", f"Build {theme['build'][1]}"]
                q3 = points[4:6] if len(points) >= 6 else [f"Refine {theme['build'][1]}", f"Strengthen {theme['build'][2]}"]
                q4 = points[6:8] if len(points) >= 8 else [f"Prepare for {career} interviews", f"Show {theme['launch'][0]} evidence"]
                return {
                    "q1": {"goals": q1, "actions": ["Weekly study plan", "Practice and review"]},
                    "q2": {"goals": q2, "actions": ["Build projects", "Track outcomes"]},
                    "q3": {"goals": q3, "actions": ["Portfolio refinement", "Mock reviews"]},
                    "q4": {"goals": q4, "actions": ["Applications", "Interview preparation"]},
                    "key_milestones": points[:3] if points else [f"{career} readiness milestone 1", "Portfolio milestone", "Interview milestone"],
                    "critical_resources": ["Courses", "Mentors", "Community"],
                    "strategy_summary": raw[:220],
                    "phase_success_signals": points[3:6] if len(points) > 5 else ["Consistent progress each month", "Visible portfolio growth"],
                    "weekly_routine": points[6:9] if len(points) > 8 else ["2 learning blocks", "2 practice blocks", "1 review block"],
                    "status": "success",
                }
            except Exception:
                pass

            return {
                "q1": {"goals": [f"Learn {theme['foundation'][0]}", f"Practice {theme['foundation'][1]}"], "actions": ["Weekly study blocks", "Concept revision"]},
                "q2": {"goals": [f"Build {theme['build'][0]}", f"Show progress in {theme['build'][1]}"], "actions": ["Hands-on projects", "Monthly reviews"]},
                "q3": {"goals": [f"Refine {theme['build'][1]}", f"Strengthen {theme['build'][2]}"], "actions": ["Portfolio polishing", "Peer feedback"]},
                "q4": {"goals": [f"Prepare for {career} interviews", f"Convert {theme['launch'][0]} into evidence"], "actions": ["Applications", "Networking"]},
                "key_milestones": [f"{career} portfolio baseline completed", "Interview prep system ready"],
                "critical_resources": ["Courses", "Mentorship", "Community groups"],
                "strategy_summary": f"Build fundamentals first, then convert practical outcomes into {career} interview evidence.",
                "phase_success_signals": ["Consistent weekly progress", "Portfolio artifacts ready", "Mock interview confidence improving"],
                "weekly_routine": ["2 learning sessions", "2 practice sessions", "1 review/reflection session"],
                "status": "fallback"
            }
