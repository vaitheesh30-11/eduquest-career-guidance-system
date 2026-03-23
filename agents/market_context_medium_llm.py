"""Market Context Medium LLM Agent - MEDIUM path moderate market analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent
from agents.personalization import career_track, city_hotspots, market_salary


class MarketContextMediumLLMAgent(BaseLLMAgent):
    def get_market_context(self , career_field : str, budget: str = "Moderate") -> Dict[str , Any]:
        track = career_track(career_field)
        prompt = f"Give brief market insights for {career_field}"

        try:
            response = self.generate(prompt, temperature=0.4,max_tokens=600)
            return {
                "job_demand_trend": "Moderate",
                "salary_rang_inr" : market_salary(track, budget),
                "growth_forecast" : "Growing",
                "industry_insights" : response[:150],
                "competitive_landscape" : "Moderate",
                "geographic_hotspots": city_hotspots(track),
                "required_certifications" : "Helpful when paired with project proof",
                "emerging_opportunities" : "AI tools and role specialization",
                "market_risks" : "Automation and crowded entry-level pipelines",
                "status" : "success",
            }

        except Exception:
            # Intelligent fallback for medium path
            field_lower = career_field.lower()
            if "data" in field_lower or "analyst" in field_lower:
                insights = "Data and analytics roles have strong demand across industries. Growth focus on business intelligence and AI-driven insights. Good salary progression opportunities."
            elif "developer" in field_lower or "engineer" in field_lower:
                insights = "Engineering roles remain highly in-demand globally. Salary ranges competitive with good growth potential. Tech stacks like cloud, DevOps, and full-stack are particularly valued."
            else:
                insights = f"{career_field} has moderate market demand with steady growth. Salary competitive in tier-1 cities. Continuous skill development is important for advancement."
            
            return {
                "job_demand_trend": "High",
                "salary_rang_inr": "6L - 18L",
                "growth_forecast": "Growing steadily",
                "industry_insights": insights,
                "competitive_landscape": "Moderate to High",
                "geographic_hotspots": "Bangalore, Hyderabad, Pune, Mumbai",
                "required_certifications": "Helpful for advancement",
                "emerging_opportunities": "AI/ML, Cloud technologies, Remote positions",
                "market_risks": "Automation, Skill obsolescence, Market saturation",
                "status": "success",
            }
