"""Profile Extractor LLM Agent - extracts structured profile from free text."""

from typing import Dict, Any
from agents.personalization import (
    infer_budget,
    infer_degree_field,
    infer_education_level,
    infer_gpa,
    infer_projects,
    infer_research_months,
    infer_timeline,
    infer_years_experience,
    split_items,
)


class ProfileExtractorLLMAgent:
    """Profile extractor - doesn't require LLM since it uses rule-based extraction."""
    
    def __init__(self, client=None):
        """Initialize - client parameter for compatibility but not required."""
        self.client = client

    def extract_profile(self, raw_inputs:Dict[str,str]) ->Dict[str,Any]:
        """Public method called by nodes."""
        return self.extract_structured_profile(raw_inputs)

    def extract_structured_profile(self, raw_inputs:Dict[str,str]) ->Dict[str,Any]:
        try:
            current_academics = raw_inputs.get("current_academics", "")
            constraints = raw_inputs.get("constraints", "")
            interests = raw_inputs.get("interests", "")
            concerns = raw_inputs.get("other_concerns", "")
            dream_career = raw_inputs.get("dream_career", "")

            profile = {
                "career_field": dream_career,
                "current_education_level": infer_education_level(current_academics),
                "years_of_experience": infer_years_experience(current_academics, constraints),
                "budget_constraints": infer_budget(constraints),
                "timeline_urgency": infer_timeline(constraints, concerns),
                "interests_list": split_items(interests),
                "concerns_list": split_items(concerns),
                "constraints_summary": constraints,
                "current_degree_field": infer_degree_field(current_academics, dream_career),
                "current_degree_filed": infer_degree_field(current_academics, dream_career),
                "gpa_percentile": infer_gpa(current_academics),
                "research_experience_months": infer_research_months(current_academics, interests),
                "project_portfolio_count": infer_projects(current_academics, interests, concerns),
            }

            return profile
        
        except Exception:
            return {}
