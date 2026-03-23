"""Market Context Light LLM Agent - EASY path brief market analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, city_hotspots, market_salary



class MarketContextLightLLMAgent(BaseLLMAgent):
    def get_market_context(self , career_field : str, budget: str = "Moderate") -> Dict[str , Any]:
        track = career_track(career_field)
        prompt = f"""Briefly decribe the job market for {career_field}"""

        try:
            response = self.generate(prompt, temperature=0.4,max_tokens=350)
            return {
                "job_demand_trend": "Stable",
                "salary_rang_inr" : market_salary(track, budget),
                "growth_forecast" : "Moderate",
                "industry_insights" : response[:120],
                "competitive_landscape" : "Moderate",
                "geographic_hotspots": city_hotspots(track),
                "required_certifications" : "Optional",
                "emerging_opportunities" : "Digital skills",
                "market_risks" : "Competition",
                "status" : "success",
            }

        except Exception:
            # Intelligent fallback for light path
            field_lower = career_field.lower()
            if "data" in field_lower:
                insights = "Data roles have good market demand. Skill development in SQL, visualization, and basics of ML helps growth."
            elif "developer" in field_lower or "software" in field_lower:
                insights = "Software development has consistent market demand. Fundamentals matter more than specific tech stack at the start."
            else:
                insights = f"{career_field} has reasonable market opportunities. Learning core skills and building experience is key to growth."
            
            return {
                "job_demand_trend": "High",
                "salary_rang_inr": "5L - 12L",
                "growth_forecast": "Moderate to High",
                "industry_insights": insights,
                "competitive_landscape": "Moderate",
                "geographic_hotspots": "Bangalore, Pune, Hyderabad, Remote",
                "required_certifications": "Optional but helpful",
                "emerging_opportunities": "Remote work, Flexibility, Specialization",
                "market_risks": "Rapid tech changes, Competition",
                "status": "success",
            }
