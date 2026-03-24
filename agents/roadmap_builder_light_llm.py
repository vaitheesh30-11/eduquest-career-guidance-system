"""Roadmap Builder Light LLM Agent - EASY path 3-phase roadmap."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, roadmap_theme

TM="3 months"

class RoadmapBuilderLightLLMAgent(BaseLLMAgent):
    def _extract_points(self, text: str, limit: int = 8):
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
        Create a light, beginner-friendly roadmap for {career}.
        Return only valid JSON with this exact shape:
        {{
          "phase_1_foundation": {{"duration": "string", "focus": "string", "goals": ["string"], "actions": ["string"]}},
          "phase_2_foundation": {{"duration": "string", "focus": "string", "goals": ["string"], "actions": ["string"]}},
          "phase_3_foundation": {{"duration": "string", "focus": "string", "goals": ["string"], "actions": ["string"]}},
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
                    "phase_1_foundation",
                    "phase_2_foundation",
                    "phase_3_foundation",
                    "key_milestones",
                    "critical_resources",
                    "strategy_summary",
                    "phase_success_signals",
                    "weekly_routine",
                ],
                temperature=0.5,
                max_tokens=900,
            )

            return{
                "phase_1_foundation": result.get("phase_1_foundation", {}),
                "phase_2_foundation": result.get("phase_2_foundation", {}),
                "phase_3_foundation": result.get("phase_3_foundation", {}),
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
                    prompt=f"Create a simple 3-phase beginner roadmap for {career} with goals, actions, milestones and weekly routine.",
                    temperature=0.5,
                    max_tokens=650,
                )
                points = self._extract_points(raw, limit=8)
                p1 = points[:2] if len(points) >= 2 else [f"Learn {theme['foundation'][0]}", f"Practice {theme['foundation'][1]}"]
                p2 = points[2:4] if len(points) >= 4 else [f"Build {theme['build'][0]}", f"Show {theme['build'][1]}"]
                p3 = points[4:6] if len(points) >= 6 else [f"Prepare for {career} roles", f"Strengthen {theme['launch'][1]}"]
                return {
                    "phase_1_foundation": {"duration": TM, "focus": f"Basics for {career}", "goals": p1, "actions": ["Foundational learning", "Weekly exercises"]},
                    "phase_2_foundation": {"duration": TM, "focus": "Practice", "goals": p2, "actions": ["Project execution", "Outcome documentation"]},
                    "phase_3_foundation": {"duration": TM, "focus": "Job readiness", "goals": p3, "actions": ["Applications", "Interview practice"]},
                    "key_milestones": points[:2] if points else ["Core skill baseline complete", "First portfolio proof complete"],
                    "critical_resources": ["Online learning", "Mentor feedback", "Community support"],
                    "strategy_summary": raw[:200],
                    "phase_success_signals": points[2:4] if len(points) >= 4 else ["Clear weekly progress", "Confidence in fundamentals"],
                    "weekly_routine": points[4:7] if len(points) >= 7 else ["3 short study sessions", "2 practice sessions", "1 review session"],
                    "status": "success",
                }
            except Exception:
                pass

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
                "key_milestones": ["Core skills checklist complete", "First portfolio-ready artifact complete"],
                "critical_resources": ["Online learning", "Community support"],
                "strategy_summary": f"Start simple, practice consistently, then transition into {career} applications.",
                "phase_success_signals": ["You can explain fundamentals clearly", "You can show at least one practical outcome"],
                "weekly_routine": ["3 short study sessions", "2 hands-on practice blocks", "1 weekly review"],
                "status": "fallback",
            }
