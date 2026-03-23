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

        Include:
        - estimated_total_cost
        - monthly_budget
        - cost_breakdown
        - funding_sources
        - roi_analysis
        - risk_mitigation
        '''

        try:
            response = self.generate(prompt=prompt, temperature=0.6, max_tokens=1200)
            funding = {
                "Limited": "Free resources, low-cost cohort courses, employer reimbursement, scholarships",
                "Moderate": "Savings, EMI-based bootcamps, selective certifications, employer support",
                "Adequate": "Premium mentoring, certifications, relocation fund, networking events",
            }[budget]
            mitigation = "Keep the plan part-time and milestone-based" if mode == "part_time" else "Front-load skill building before expensive commitments"
            track_breakdown = {
                "data": "SQL/Python training, analytics tools, portfolio projects, interview prep",
                "product": "PM courses, case-study coaching, mock interviews, networking events",
                "design": "Design tools, portfolio refinement, mentorship, case-study reviews",
                "marketing": "Campaign labs, analytics tools, portfolio projects, certifications",
                "software": "Courses, cloud credits, portfolio apps, interview practice",
            }[track]

            return{
                "estimated_total_cost": ranges["total"],
                "monthly_budget": ranges["monthly"],
                "cost_breakdown": track_breakdown,
                "funding_sources": funding,
                "roi_analysis": response[:200] if response else f"ROI improves as you convert projects into {career} interview opportunities.",
                "risk_mitigation": mitigation,
                "status": "success",
            }

        except Exception:
            return{
                "estimated_total_cost": ranges["total"],
                "monthly_budget": ranges["monthly"],
                "cost_breakdown": "Training, portfolio work, interview preparation",
                "funding_sources": "Savings and low-cost learning paths",
                "roi_analysis": "Moderate ROI expected when spending stays milestone-based.",
                "risk_mitigation": "Learn gradually",
                "status": "fallback",
            }
