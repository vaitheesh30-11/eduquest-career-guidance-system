"""Reality Check Light LLM Agent - EASY path brief analysis."""

from typing import Dict, Any

from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track

class RealityCheckLightLLMAgent(BaseLLMAgent):
    def generate_reality_check(
        self,
        ml_results:Dict[str,Any],
    )-> Dict[str,Any]:
        viability = ml_results.get("viability_score",0.5)
        career = ml_results.get("career_field", "this career")
        track = career_track(career)
        prompt = f"Give short reality check for this career. Viability score: {viability}"
        try :
            response = self.generate(prompt,temperature =0.5,max_tokens = 350)
            main_challenge = {
                "data": "Skill learning in analytics tools",
                "product": "Turning experience into product stories",
                "design": "Building a stronger portfolio",
                "marketing": "Showing measurable campaign impact",
                "software": "Skill learning",
            }[track]
            return {
                "honest_assessment":response[:150],
                "major_challenges":[
                    main_challenge,
                    "Consistency",
                ],
                "success_probability":round(viability*100,1),
                "mindset_requirements":["Persistence"],
                "status":"success",
            }
        except Exception:
            viability_pct = round(viability * 100, 1)
            return {
                "honest_assessment": f"This career change is feasible. With {viability_pct}% viability, you have potential. Start with foundational learning, build projects, and gradually progress. Stay consistent and adaptable.",
                "major_challenges": [
                    "Initial learning curve",
                    "Time commitment for skill building",
                    "Market competition"
                ],
                "success_probability": min(70, round(viability_pct * 1.1)),
                "mindset_requirements": [
                    "Persistence through challenges",
                    "Flexibility and adaptability",
                    "Long-term commitment"
                ],
                "status": "success",
            }
