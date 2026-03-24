"""Alternative Explorer LLM Agent - HARD path alternative careers."""

from typing import Dict, Any, List
from agents.base_llm_agent import BaseLLMAgent
from agents.output_schemas import AlternativesOutput
from agents.personalization import career_track


class AlternativeExplorerLLMAgent(BaseLLMAgent):
    def _validate_output(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return AlternativesOutput.model_validate(payload).model_dump()

    def __init__(self, client):
        super().__init__(client)

    def explore_alternatives(self, profile: Dict[str, Any], ml_results:Dict[str, Any])->Dict[str,Any]:

        dream_career=profile.get("career_field","the target career")
        viability=ml_results.get("viability_score", 0)

        prompt=f'''
        You are a career advisor.

        User dream career: {dream_career}
        Viability Score: {viability}

        Suggest 5 alternative careers.

        Return only valid JSON with this exact shape:
        {{
          "alternatives": [
            {{
              "career": "string",
              "similarity_to_dream": number,
              "viability_estimate": number,
              "reasoning": "string",
              "transition_effort": "Low|Medium|High"
            }}
          ],
          "summary": "string"
        }}
        '''

        try:
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=["alternatives", "summary"],
                temperature=0.6,
                max_tokens=1200
            )
            raw_alternatives = result.get("alternatives", [])
            alternatives: List[Dict[str, Any]] = []
            for alt in raw_alternatives[:5]:
                if not isinstance(alt, dict):
                    continue
                alternatives.append(
                    {
                        "career": str(alt.get("career", "")),
                        "similarity_to_dream": max(0.0, min(1.0, float(alt.get("similarity_to_dream", 0.0)))),
                        "viability_estimate": max(0.0, min(1.0, float(alt.get("viability_estimate", 0.0)))),
                        "reasoning": str(alt.get("reasoning", "")),
                        "transition_effort": str(alt.get("transition_effort", "Medium")),
                    }
                )
            if not alternatives:
                raise ValueError("LLM returned empty alternatives list")
            return self._validate_output(self._with_response_source({
                "alternatives": alternatives,
                "summary": str(result.get("summary", "Generated alternative career paths")),
                "status": "success",
            }, "llm_structured"))

        except Exception:
            # Generate intelligent alternatives based on dream career
            career = dream_career.lower()
            
            if "data scientist" in career:
                alternatives = [
                    {
                        "career": "Machine Learning Engineer",
                        "similarity_to_dream": 0.85,
                        "viability_estimate": 0.75,
                        "reasoning": "Focuses on ML model productionization and system design. Requires similar ML knowledge with emphasis on engineering and deployment. High market demand.",
                        "transition_effort": "Low",
                    },
                    {
                        "career": "Data Analyst",
                        "similarity_to_dream": 0.75,
                        "viability_estimate": 0.8,
                        "reasoning": "Works with business intelligence and analytics. Leverages SQL and visualization skills. Less ML-heavy but more accessible entry path.",
                        "transition_effort": "Low",
                    },
                    {
                        "career": "Analytics Engineer",
                        "similarity_to_dream": 0.8,
                        "viability_estimate": 0.78,
                        "reasoning": "Bridges data engineering and analytics. Strong growth field combining data pipeline development with analytical insights.",
                        "transition_effort": "Medium",
                    },
                    {
                        "career": "AI/ML Research Scientist",
                        "similarity_to_dream": 0.9,
                        "viability_estimate": 0.65,
                        "reasoning": "Focuses on cutting-edge ML research and innovation. Requires strong mathematical foundation and research experience. Higher barrier to entry.",
                        "transition_effort": "High",
                    },
                    {
                        "career": "Business Intelligence Developer",
                        "similarity_to_dream": 0.7,
                        "viability_estimate": 0.8,
                        "reasoning": "Creates dashboards and analytical tools for business insights. Mix of technical and business understanding. Strong job market.",
                        "transition_effort": "Low",
                    }
                ]
            
            elif "software" in career or "developer" in career:
                alternatives = [
                    {
                        "career": "Full Stack Developer",
                        "similarity_to_dream": 0.85,
                        "viability_estimate": 0.85,
                        "reasoning": "Combines front-end and back-end development skills. Highly versatile and in-demand across industries.",
                        "transition_effort": "Low",
                    },
                    {
                        "career": "DevOps Engineer",
                        "similarity_to_dream": 0.8,
                        "viability_estimate": 0.8,
                        "reasoning": "Focuses on deployment, automation, and infrastructure. Leverages programming knowledge for system operations.",
                        "transition_effort": "Medium",
                    },
                    {
                        "career": "Cloud Architect",
                        "similarity_to_dream": 0.75,
                        "viability_estimate": 0.7,
                        "reasoning": "Designs cloud infrastructures and solutions. Growing field with excellent opportunities and compensation.",
                        "transition_effort": "Medium",
                    },
                    {
                        "career": "Solutions Architect",
                        "similarity_to_dream": 0.7,
                        "viability_estimate": 0.75,
                        "reasoning": "Bridges technical and business needs. Involves more client-facing work and high-level design.",
                        "transition_effort": "Medium",
                    },
                    {
                        "career": "Technical Lead/Manager",
                        "similarity_to_dream": 0.65,
                        "viability_estimate": 0.8,
                        "reasoning": "Transitions from individual contributor to leadership. Combines technical expertise with team management.",
                        "transition_effort": "Medium",
                    }
                ]
            
            else:
                # Generic alternatives for other careers
                alternatives = [
                    {
                        "career": f"Senior {dream_career}",
                        "similarity_to_dream": 0.95,
                        "viability_estimate": 0.85,
                        "reasoning": "Natural progression path with deepened expertise and specialization in your chosen field.",
                        "transition_effort": "Low",
                    },
                    {
                        "career": f"{dream_career} Consultant",
                        "similarity_to_dream": 0.9,
                        "viability_estimate": 0.7,
                        "reasoning": "Leverage your expertise to help organizations solve problems. Requires strong domain knowledge.",
                        "transition_effort": "Medium",
                    },
                    {
                        "career": f"Technical Lead - {dream_career}",
                        "similarity_to_dream": 0.85,
                        "viability_estimate": 0.75,
                        "reasoning": "Combine expertise with team leadership and mentoring responsibilities.",
                        "transition_effort": "Medium",
                    },
                    {
                        "career": f"Product Manager ({dream_career})",
                        "similarity_to_dream": 0.7,
                        "viability_estimate": 0.65,
                        "reasoning": "Transition to product leadership using domain expertise in your field.",
                        "transition_effort": "High",
                    },
                    {
                        "career": f"Educator/Trainer in {dream_career}",
                        "similarity_to_dream": 0.75,
                        "viability_estimate": 0.7,
                        "reasoning": "Share domain knowledge through teaching, training, or content creation.",
                        "transition_effort": "Medium",
                    }
                ]
            
            return self._validate_output(self._with_response_source({
                "alternatives": alternatives,
                "summary": "Personalized career alternatives based on your target role and market analysis",
                "status": "success",
            }, "fallback"))
