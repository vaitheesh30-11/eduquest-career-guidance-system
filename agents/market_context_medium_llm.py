"""Market Context Medium LLM Agent - MEDIUM path moderate market analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, city_hotspots, market_salary


class MarketContextMediumLLMAgent(BaseLLMAgent):
    def get_market_context(self , career_field : str, budget: str = "Moderate") -> Dict[str , Any]:
        track = career_track(career_field)
        prompt = f"""
        Give medium-depth market insights for {career_field}.
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
                max_tokens=800,
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
                    prompt=f"Give concise medium-depth market context for {career_field} in India: demand, salary, growth, hotspots, opportunities, risks.",
                    temperature=0.4,
                    max_tokens=500,
                )
                return {
                    "job_demand_trend": "Moderate to High",
                    "salary_rang_inr": market_salary(track, budget),
                    "growth_forecast": "Growing steadily",
                    "industry_insights": raw[:220],
                    "competitive_landscape": "Moderate to High",
                    "geographic_hotspots": city_hotspots(track),
                    "required_certifications": "Helpful when combined with practical proof",
                    "emerging_opportunities": "Role specialization and AI-augmented workflows",
                    "market_risks": "Entry-level competition and changing role requirements",
                    "status": "success",
                }
            except Exception:
                # Intelligent fallback for medium path
                return {
                    "job_demand_trend": "High",
                    "salary_rang_inr": market_salary(track, budget),
                    "growth_forecast": "Growing steadily",
                    "industry_insights": f"{career_field} has moderate-to-strong market demand depending on specialization and city.",
                    "competitive_landscape": "Moderate to High",
                    "geographic_hotspots": city_hotspots(track),
                    "required_certifications": "Helpful for advancement",
                    "emerging_opportunities": "AI/automation tools, domain specialization, remote positions",
                    "market_risks": "Automation, skill obsolescence, market saturation",
                    "status": "fallback",
                }
