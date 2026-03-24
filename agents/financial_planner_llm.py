"""Financial Planner LLM Agent - HARD path financial analysis."""

from typing import Dict, Any
from .base_llm_agent import BaseLLMAgent
from .personalization import budget_ranges, career_track, learning_mode


class FinancialPlannerLLMAgent(BaseLLMAgent):
    def generate_financial_plan(self, profile: Dict[str, Any], ml_results:Dict[str, Any])->Dict[str,Any]:
        viability = ml_results.get("viability_score", ml_results.get("success_probability", 50) / 100)
        career = profile.get("career_field", "Unknown")
        budget = profile.get("budget_constraints", "Moderate")
        ranges = budget_ranges(budget)
        mode = learning_mode(profile.get("constraints_summary", ""))
        track = career_track(career)
        prompt=f'''
        Create a financial plan for pursuing a career in {career}.
        Viability score: {viability}

        Return only valid JSON with this exact shape:
        {{
          "estimated_total_cost": "string",
          "monthly_budget": "string",
          "cost_breakdown": "string",
          "funding_sources": "string",
          "roi_analysis": "string",
          "risk_mitigation": "string"
        }}
        '''

        try:
            result = self.generate_structured_json(
                prompt=prompt,
                required_fields=[
                    "estimated_total_cost",
                    "monthly_budget",
                    "cost_breakdown",
                    "funding_sources",
                    "roi_analysis",
                    "risk_mitigation",
                ],
                temperature=0.6,
                max_tokens=1200,
            )

            return{
                "estimated_total_cost": str(result.get("estimated_total_cost", ranges["total"])),
                "monthly_budget": str(result.get("monthly_budget", ranges["monthly"])),
                "cost_breakdown": str(result.get("cost_breakdown", "")),
                "funding_sources": str(result.get("funding_sources", "")),
                "roi_analysis": str(result.get("roi_analysis", "")),
                "risk_mitigation": str(result.get("risk_mitigation", "")),
                "status": "success",
            }

        except Exception:
            mitigation = "Keep the plan part-time and milestone-based" if mode == "part_time" else "Front-load skill building before expensive commitments"
            return{
                "estimated_total_cost": ranges["total"],
                "monthly_budget": ranges["monthly"],
                "cost_breakdown": f"Core training and portfolio work for {career} ({track} track)",
                "funding_sources": f"Budget-aware options based on {budget} constraints",
                "roi_analysis": f"ROI depends on converting new skills into interviews for {career}.",
                "risk_mitigation": mitigation,
                "status": "fallback",
            }
