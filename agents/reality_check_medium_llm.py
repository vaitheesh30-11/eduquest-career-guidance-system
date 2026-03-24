"""Reality Check Medium LLM Agent - MEDIUM path moderate analysis."""

from typing import Dict, Any

from agents.base_llm_agent import BaseLLMAgent
from agents.output_schemas import RealityCheckOutput
from agents.personalization import career_track

class RealityCheckMediumLLMAgent(BaseLLMAgent):
    def _validate_output(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return RealityCheckOutput.model_validate(payload).model_dump()

    def generate_reality_check(
        self,
        ml_results:Dict[str,Any],
    )->Dict[str,Any]:
        viability = ml_results.get("viability_score",0.5)
        career = ml_results.get("career_field", "this career")
        track = career_track(career)
        prompt =f"""
        Give a moderate reality check for this career: {career}.
        Viability score: {viability}
        Return only valid JSON with this exact shape:
        {{
          "honest_assessment": "string",
          "major_challenges": ["string", "string", "string"],
          "success_probability": number,
          "mindset_requirements": ["string", "string", "string"]
        }}
        """
        try:
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=[
                    "honest_assessment",
                    "major_challenges",
                    "success_probability",
                    "mindset_requirements",
                ],
                temperature=0.5,
                max_tokens=700,
            )
            success_probability = float(result.get("success_probability", round(viability * 100, 1)))
            success_probability = max(0.0, min(100.0, success_probability))
            return self._validate_output(self._with_response_source({
                "honest_assessment": str(result.get("honest_assessment", "")),
                "major_challenges": list(result.get("major_challenges", []))[:4],
                "success_probability": round(success_probability, 1),
                "mindset_requirements": list(result.get("mindset_requirements", []))[:4],
                "status":"success",
            }, "llm_structured"))
        except Exception:
            viability_pct = round(viability * 100, 1)
            return self._validate_output(self._with_response_source({
                "honest_assessment": f"Your career goal is achievable with focused effort. With {viability_pct}% viability score, you have a reasonable foundation. Success requires consistent learning and practical experience building.",
                "major_challenges": [
                    "Skill gaps that need filling",
                    "Competition in your chosen field",
                    "Balancing learning with other commitments"
                ],
                "success_probability": min(75, round(viability_pct * 1.2)),
                "mindset_requirements": [
                    "Consistent daily effort",
                    "Patience with the learning process",
                    "Willingness to adapt and pivot"
                ],
                "status": "success",
            }, "fallback"))
