"""Reality Check Full LLM Agent - HARD path deep analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent 
from agents.output_schemas import RealityCheckOutput
from agents.personalization import career_track, learning_mode

class RealityCheckFullLLMAgent(BaseLLMAgent):
    def _validate_output(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return RealityCheckOutput.model_validate(payload).model_dump()

    def generate_reality_check(
        self,
        ml_results : Dict[str,Any],
    ) -> Dict[str,Any]:
        viability = ml_results.get("viability_score",0.5)
        academic_fit = ml_results.get("academic_fit_score",0.5)
        career = ml_results.get("career_field", "this career")
        track = career_track(career)
        mode = learning_mode(ml_results.get("constraints_summary", ""))
        prompt = f"""
        You are a practical career advisor.
        Return only valid JSON with this exact shape:
        {{
          "honest_assessment": "string",
          "major_challenges": ["string", "string", "string", "string"],
          "success_probability": number,
          "mindset_requirements": ["string", "string", "string"]
        }}

        Provide a realistic assessment of achieving this career: {career}.
        Viability Score: {viability}
        Academic Fit Score: {academic_fit}
        """
        try :
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=[
                    "honest_assessment",
                    "major_challenges",
                    "success_probability",
                    "mindset_requirements",
                ],
                temperature=0.5,
                max_tokens=1000,
            )
            mindset = result.get("mindset_requirements", [])
            if mode == "part_time":
                mindset = mindset + ["Disciplined scheduling around existing commitments"]
            success_probability = float(result.get("success_probability", round(viability * 100, 1)))
            success_probability = max(0.0, min(100.0, success_probability))
            return self._validate_output(self._with_response_source({
                "honest_assessment": str(result.get("honest_assessment", "")),
                "major_challenges": list(result.get("major_challenges", []))[:5],
                "success_probability": round(success_probability, 1),
                "mindset_requirements": mindset,
                "status":"success",

            }, "llm_structured"))
        except Exception :
            # Intelligent fallback assessment based on ML scores
            viability_pct = round(viability * 100, 1)
            academic_pct = round(academic_fit if academic_fit > 1 else academic_fit * 100, 1)
            
            # Determine assessment tone based on scores
            if viability >= 0.7:
                honest = f"Your career path is highly viable. With {viability_pct}% career viability score and {academic_pct}% academic fit, you have a strong foundation. Success depends on consistent effort, continuous learning, and adapting to market demands."
                challenges = [
                    "Rapidly evolving skill requirements in your field",
                    "High competition from other professionals",
                    "Balancing learning while building practical experience",
                    "Financial investment in upskilling and certifications"
                ]
                success = min(85, round(viability_pct + academic_pct / 2))
            elif viability >= 0.5:
                honest = f"Your career path is moderately viable ({viability_pct}% viability, {academic_pct}% fit). You have potential but need focused effort on skill gaps. Success requires intentional learning and project building."
                challenges = [
                    "Filling knowledge gaps through structured learning",
                    "Building practical portfolio and projects",
                    "Managing competition from better-prepared candidates",
                    "Time management between learning and current responsibilities"
                ]
                success = min(70, round(viability_pct + academic_pct / 2))
            else:
                honest = f"Your career path requires significant preparation ({viability_pct}% viability, {academic_pct}% fit). It's achievable but demands dedicated effort, skill building, and strategic planning."
                challenges = [
                    "Substantial skill foundation gaps to fill",
                    "Need for extended learning period",
                    "Highly competitive field with experienced candidates",
                    "Potential career transition costs and risks"
                ]
                success = min(55, round(viability_pct + academic_pct / 2))
            
            return self._validate_output(self._with_response_source({
                "honest_assessment": honest,
                "major_challenges": challenges,
                "success_probability": success,
                "mindset_requirements": [
                    "Consistent, disciplined effort and learning",
                    "Long-term perspective - growth over 2-3 years",
                    "Adaptability to changing market and technology",
                    "Resilience through setbacks and challenges",
                    "Proactive networking and community engagement"
                ],
                "status": "success",
            }, "fallback"))
