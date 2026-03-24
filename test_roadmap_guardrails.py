from agents.roadmap_builder_light_llm import RoadmapBuilderLightLLMAgent
from agents.roadmap_builder_medium_llm import RoadmapBuilderMediumLLMAgent
from agents.roadmap_builder_full_llm import RoadmapBuilderFullLLMAgent


class DirectJsonClient:
    is_initialized = True
    model = "mock-model"

    def __init__(self, response_text: str):
        self.response_text = response_text

    def generate_content(self, *args, **kwargs):
        return self.response_text

    def extract_json_from_response(self, response_text):
        import json
        return json.loads(response_text)

    def validate_response_fields(self, response, required_fields):
        missing = [field for field in required_fields if field not in response]
        if missing:
            raise ValueError(f"Missing fields: {missing}")


def test_light_roadmap_guardrail_normalizes_month_schema():
    client = DirectJsonClient(
        """
        {
          "phase_1_months": {"months": "1-3", "goals": ["Basics"], "actions": ["Study"]},
          "phase_2_months": {"months": "4-6", "goals": ["Practice"], "actions": ["Projects"]},
          "phase_3_months": {"months": "7-9", "goals": ["Apply"], "actions": ["Interviews"]},
          "key_milestones": ["Milestone 1"],
          "success_resources": ["Courses"],
          "strategy_summary": "Summary",
          "phase_success_signals": ["Signal"],
          "weekly_routine": ["Routine"]
        }
        """
    )
    agent = RoadmapBuilderLightLLMAgent(client)

    result = agent.generate_roadmap({"career_field": "Teacher"}, {"viability_score": 0.2})

    assert result["response_source"] == "llm_direct"
    assert "phase_1_foundation" in result
    assert result["critical_resources"] == ["Courses"]


def test_medium_roadmap_guardrail_preserves_structured_shape():
    class StructuredClient:
        is_initialized = True
        model = "mock-model"

        def generate_structured_json(self, *args, **kwargs):
            return {
                "q1": {"goals": ["Learn"], "actions": ["Study"]},
                "q2": {"goals": ["Build"], "actions": ["Practice"]},
                "q3": {"goals": ["Refine"], "actions": ["Review"]},
                "q4": {"goals": ["Launch"], "actions": ["Apply"]},
                "key_milestones": ["Milestone"],
                "critical_resources": ["Mentor"],
                "strategy_summary": "Summary",
                "phase_success_signals": ["Signal"],
                "weekly_routine": ["Routine"],
            }

    agent = RoadmapBuilderMediumLLMAgent(StructuredClient())
    result = agent.generate_roadmap({"career_field": "Software Engineer"}, {"viability_score": 0.5})

    assert result["response_source"] == "llm_structured"
    assert result["q1"]["goals"] == ["Learn"]


def test_full_roadmap_guardrail_fallback_validates():
    class FailingClient:
        is_initialized = True
        model = "mock-model"

        def generate_structured_json(self, *args, **kwargs):
            raise ValueError("no structured response")

        def generate_content(self, *args, **kwargs):
            raise ValueError("no direct response")

    agent = RoadmapBuilderFullLLMAgent(FailingClient())
    result = agent.generate_roadmap({"career_field": "Teacher", "constraints_summary": ""}, {"viability_score": 0.3})

    assert result["response_source"] == "fallback"
    assert "phase_1_months" in result
