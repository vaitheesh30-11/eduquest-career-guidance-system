import pytest

from agents.alternative_explorer_llm import AlternativeExplorerLLMAgent
from agents.market_context_light_llm import MarketContextLightLLMAgent


class StructuredSuccessClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, prompt, required_fields, temperature=0.7, max_tokens=2000, **kwargs):
        if required_fields == ["alternatives", "summary"]:
            return {
                "alternatives": [
                    {
                        "career": "Full Stack Developer",
                        "similarity_to_dream": 0.8,
                        "viability_estimate": 0.75,
                        "reasoning": "High overlap with software skills.",
                        "transition_effort": "Low",
                    }
                ],
                "summary": "Mock structured success",
            }
        raise AssertionError(f"Unexpected required_fields: {required_fields}")


class FullFailureClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, *args, **kwargs):
        raise ValueError("mock structured failure")

    def generate_content(self, *args, **kwargs):
        raise ValueError("mock direct failure")


class DirectOnlyClient:
    is_initialized = True
    model = "mock-model"

    def generate_structured_json(self, *args, **kwargs):
        raise ValueError("mock structured failure")

    def generate_content(self, *args, **kwargs):
        return "Short direct market summary from mock client."


def test_alternative_explorer_marks_structured_llm_source():
    agent = AlternativeExplorerLLMAgent(StructuredSuccessClient())
    result = agent.explore_alternatives(
        {"career_field": "Software Engineer"},
        {"viability_score": 0.5},
    )

    assert result["response_source"] == "llm_structured"
    assert result["status"] == "success"


def test_alternative_explorer_marks_fallback_source():
    agent = AlternativeExplorerLLMAgent(FullFailureClient())
    result = agent.explore_alternatives(
        {"career_field": "Software Engineer"},
        {"viability_score": 0.5},
    )

    assert result["response_source"] == "fallback"


def test_market_context_marks_direct_llm_source():
    agent = MarketContextLightLLMAgent(DirectOnlyClient())
    result = agent.get_market_context("Software Engineer", "Moderate")

    assert result["response_source"] == "llm_direct"
    assert result["status"] == "success"
