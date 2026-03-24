from agents.alternative_explorer_llm import AlternativeExplorerLLMAgent
from agents.financial_planner_llm import FinancialPlannerLLMAgent
from agents.market_context_light_llm import MarketContextLightLLMAgent
from agents.reality_check_medium_llm import RealityCheckMediumLLMAgent


class StructuredRealityClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, *args, **kwargs):
        return {
            "honest_assessment": "Achievable path.",
            "major_challenges": ["Skill gap", "Competition", "Time"],
            "success_probability": 62.5,
            "mindset_requirements": ["Consistency", "Patience", "Adaptability"],
        }


class DirectMarketClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, *args, **kwargs):
        raise ValueError("structured failure")

    def generate_content(self, *args, **kwargs):
        return "Demand is stable, salary is decent, and Bangalore is a strong hotspot."


class FallbackFinancialClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, *args, **kwargs):
        raise ValueError("structured failure")


class StructuredAlternativesClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, *args, **kwargs):
        return {
            "alternatives": [
                {
                    "career": "Full Stack Developer",
                    "similarity_to_dream": 0.8,
                    "viability_estimate": 0.75,
                    "reasoning": "Overlap is strong.",
                    "transition_effort": "Low",
                }
            ],
            "summary": "Good nearby options.",
        }


def test_reality_guardrail_validates_structured_output():
    agent = RealityCheckMediumLLMAgent(StructuredRealityClient())
    result = agent.generate_reality_check({"viability_score": 0.52, "career_field": "Teacher"})
    assert result["response_source"] == "llm_structured"
    assert isinstance(result["success_probability"], float)


def test_market_guardrail_validates_direct_output():
    agent = MarketContextLightLLMAgent(DirectMarketClient())
    result = agent.get_market_context("Teacher", "Moderate")
    assert result["response_source"] == "llm_direct"
    assert "job_demand_trend" in result


def test_financial_guardrail_validates_fallback_output():
    agent = FinancialPlannerLLMAgent(FallbackFinancialClient())
    result = agent.generate_financial_plan(
        {"career_field": "Teacher", "budget_constraints": "Limited", "constraints_summary": ""},
        {"viability_score": 0.4},
    )
    assert result["response_source"] == "fallback"
    assert "monthly_budget" in result


def test_alternatives_guardrail_validates_items():
    agent = AlternativeExplorerLLMAgent(StructuredAlternativesClient())
    result = agent.explore_alternatives({"career_field": "Software Engineer"}, {"viability_score": 0.5})
    assert result["response_source"] == "llm_structured"
    assert result["alternatives"][0]["transition_effort"] == "Low"
