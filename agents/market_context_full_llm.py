"""Market Context Full LLM Agent - HARD path comprehensive market analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, city_hotspots, market_salary



class MarketContextFullLLMAgent(BaseLLMAgent):

    def get_market_context(self,career_field: str, budget: str = "Moderate") -> Dict[str,Any]:
        track = career_track(career_field)
        prompt = f"""
        Provide a detailed market analysis for {career_field}.
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
                max_tokens=1000,
            )
            return{
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
                    prompt=f"Provide practical market insights for {career_field} in India: demand trend, salary range, growth, hotspots, opportunities, risks.",
                    temperature=0.4,
                    max_tokens=700,
                )
                return {
                    "job_demand_trend": "Moderate to High",
                    "salary_rang_inr": market_salary(track, budget),
                    "growth_forecast": "Growing",
                    "industry_insights": raw[:300],
                    "competitive_landscape": "Moderate to High",
                    "geographic_hotspots": city_hotspots(track),
                    "required_certifications": "Role-specific certifications with practical portfolio proof",
                    "emerging_opportunities": "AI-enabled tools, specialization, and remote/hybrid opportunities",
                    "market_risks": "Market cycles, hiring volatility, and skill mismatch",
                    "status": "success",
                }
            except Exception:
                return {
                    "job_demand_trend": "Moderate to High",
                    "salary_rang_inr": market_salary(track, budget),
                    "growth_forecast": "Steady growth expected",
                    "industry_insights": f"{career_field} has role-specific demand that varies by region and specialization.",
                    "competitive_landscape": "Moderate competition",
                    "geographic_hotspots": city_hotspots(track),
                    "required_certifications": "Role-specific certifications and practical portfolio evidence",
                    "emerging_opportunities": "Digital adoption, specialization, and remote/hybrid roles",
                    "market_risks": "Economic cycles, changing hiring criteria, and skill mismatch",
                    "status": "fallback",
                }
