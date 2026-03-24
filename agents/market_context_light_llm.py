"""Market Context Light LLM Agent - EASY path brief market analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, city_hotspots, market_salary



class MarketContextLightLLMAgent(BaseLLMAgent):
    def get_market_context(self , career_field : str, budget: str = "Moderate") -> Dict[str , Any]:
        track = career_track(career_field)
        prompt = f"""
        Briefly describe the job market for {career_field}.
        Return only valid JSON with this exact shape:
        {{
          "job_demand_trend": "string",
          "salary_rang_inr": "string",
          "growth_forecast": "string",
          "industry_insights": "string",
          "competitive_landscape": "string",
          "geographic_hotspots": "string",
          "required_certifications": "string",
          "emerging_opportunities": "string",
          "market_risks": "string"
        }}
        Budget profile: {budget}
        """

        try:
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=[
                    "job_demand_trend",
                    "salary_rang_inr",
                    "growth_forecast",
                    "industry_insights",
                    "competitive_landscape",
                    "geographic_hotspots",
                    "required_certifications",
                    "emerging_opportunities",
                    "market_risks",
                ],
                temperature=0.4,
                max_tokens=550,
            )
            return {
                "job_demand_trend": str(result.get("job_demand_trend", "")),
                "salary_rang_inr" : str(result.get("salary_rang_inr", market_salary(track, budget))),
                "growth_forecast" : str(result.get("growth_forecast", "")),
                "industry_insights" : str(result.get("industry_insights", "")),
                "competitive_landscape" : str(result.get("competitive_landscape", "")),
                "geographic_hotspots": str(result.get("geographic_hotspots", city_hotspots(track))),
                "required_certifications" : str(result.get("required_certifications", "")),
                "emerging_opportunities" : str(result.get("emerging_opportunities", "")),
                "market_risks" : str(result.get("market_risks", "")),
                "status" : "success",
            }
        except Exception:
            try:
                raw = self.generate_direct(
                    prompt=f"Give short market context for {career_field}: demand, salary, hotspots, key risk.",
                    temperature=0.4,
                    max_tokens=350,
                )
                return {
                    "job_demand_trend": "Stable to Growing",
                    "salary_rang_inr": market_salary(track, budget),
                    "growth_forecast": "Moderate",
                    "industry_insights": raw[:180],
                    "competitive_landscape": "Moderate",
                    "geographic_hotspots": city_hotspots(track),
                    "required_certifications": "Optional but useful",
                    "emerging_opportunities": "Remote/hybrid roles and specialization",
                    "market_risks": "Competition and changing hiring expectations",
                    "status": "success",
                }
            except Exception:
                # Intelligent fallback for light path
                return {
                    "job_demand_trend": "High",
                    "salary_rang_inr": market_salary(track, budget),
                    "growth_forecast": "Moderate to High",
                    "industry_insights": f"{career_field} has reasonable market opportunities with better outcomes from skill depth and practical evidence.",
                    "competitive_landscape": "Moderate",
                    "geographic_hotspots": city_hotspots(track),
                    "required_certifications": "Optional but helpful",
                    "emerging_opportunities": "Remote work, flexibility, and specialization",
                    "market_risks": "Rapid changes in role requirements and competition",
                    "status": "fallback",
                }
