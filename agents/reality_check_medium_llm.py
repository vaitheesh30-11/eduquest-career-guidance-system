"""Reality Check Medium LLM Agent - MEDIUM path moderate analysis."""

from typing import Dict, Any

from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track

class RealityCheckMediumLLMAgent(BaseLLMAgent):
    def generate_reality_check(
        self,
        ml_results:Dict[str,Any],
    )->Dict[str,Any]:
        viability = ml_results.get("viability_score",0.5)
        career = ml_results.get("career_field", "this career")
        track = career_track(career)
        prompt =f"""
        Give moderate reality check for this career.
        Viability score : {viability}
        """
        try:
            response = self.generate(prompt,temperature = 0.5,max_tokens = 600)
            challenges = {
                "data": ["Skill gap in tools and statistics", "Portfolio credibility", "Competition"],
                "product": ["Case-study quality", "Stakeholder communication", "Competition"],
                "design": ["Portfolio quality", "Feedback cycles", "Competition"],
                "marketing": ["Metrics-driven proof", "Platform changes", "Competition"],
                "software": ["Skill gap", "Competition", "Time commitment"],
            }[track]
            return {
                "honest_assessment":response[:180],
                "major_challenges": challenges,
                "success_probability": round(viability*100,1),
                "mindset_requirements":[
                    "Consistency",
                    "patience",
                ],
                "status":"success",
            }
        except Exception:
            viability_pct = round(viability * 100, 1)
            return {
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
            }
