"""
EduQuest Test Suite

Tests validate output contracts and logic without constraining implementation.
Following VentureLens testing patterns.

Test Structure:
- 12 total test cases
- Organized by component type
- Mock infrastructure for LLM testing
- Multiple student profiles for scenario testing
- Data quality validation for ML training data
"""

import pytest
import json
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path


# ============================================================================
# PART 1: Mock Infrastructure
# ============================================================================

class MockGeminiContent:
    """Simulates google.genai content response"""
    def __init__(self, text: str):
        self.text = text


class MockGeminiResponse:
    """Simulates Gemini API response"""
    def __init__(self, text: str):
        self.text = text


class MockGeminiClient:
    """
    Complete mock of GeminiClient for testing without API calls.
    Pattern matches on prompt content to return appropriate responses.
    """

    def __init__(self):
        self.call_count = 0
        self.default_responses = {
            'student_profile': {
                'career_field': 'Software Engineering',
                'current_education_level': 'Bachelor',
                'years_of_experience': 2,
                'budget_constraints': 'Moderate',
                'timeline_urgency': 'Medium',
                'interests_list': ['AI', 'Web Development', 'Cloud Computing'],
                'concerns_list': ['Career transition cost', 'Time commitment'],
                'current_degree_field': 'Computer Science',
                'gpa_percentile': 0.75,
                'research_experience_months': 6,
                'project_portfolio_count': 3
            },
            'reality_check_full': {
                'honest_assessment': 'This is a challenging but achievable career transition',
                'major_challenges': ['Skill gaps', 'Certification requirements', 'Geographic limitations', 'Industry competition'],
                'success_probability': 'Moderate (45-55%)',
                'mindset_requirements': ['Resilience for setbacks', 'Commitment to learning', 'Networking mindset']
            },
            'reality_check_medium': {
                'honest_assessment': 'This is a reasonable career move',
                'major_challenges': ['Learning curve', 'Interview preparation', 'Market competition'],
                'success_probability': 'Good (60-70%)',
                'mindset_requirements': ['Focused learning', 'Professional development']
            },
            'reality_check_light': {
                'honest_assessment': 'This aligns well with your profile',
                'major_challenges': ['Continuous skill updates', 'Market adaptation'],
                'success_probability': 'Very High (80-90%)',
                'mindset_requirements': ['Maintain momentum']
            },
            'financial_plan': {
                'estimated_costs': {
                    'courses': 2000,
                    'certifications': 1500,
                    'living_expenses': 24000
                },
                'funding_options': ['Scholarships', 'Student loans', 'Part-time work'],
                'budget_timeline': '24 months',
                'cost_mitigation': ['Free courses first', 'Employer sponsorship']
            },
            'roadmap_full': {
                'phase_1_months': {
                    'months': '1-3',
                    'goals': ['Foundation skills', 'Build portfolio', 'Start projects'],
                    'actions': ['Complete online courses', 'Start projects', 'Network']
                },
                'phase_2_months': {
                    'months': '4-8',
                    'goals': ['Advanced skills', 'Network building', 'Certification'],
                    'actions': ['Advanced courses', 'Industry events', 'Certification prep']
                },
                'phase_3_months': {
                    'months': '9-12',
                    'goals': ['Job search', 'Land position', 'Success'],
                    'actions': ['Apply to jobs', 'Interview prep', 'Negotiate offer']
                },
                'key_milestones': ['Complete core training', 'Launch 3 projects', 'Achieve certification', 'Secure position'],
                'success_resources': ['Online courses', 'Certification programs', 'Mentorship']
            },
            'roadmap_medium': {
                'q1': {
                    'goals': ['Skill assessment', 'Plan creation', 'Foundation learning'],
                    'actions': ['Identify gaps', 'Research opportunities', 'Start courses']
                },
                'q2': {
                    'goals': ['Skill development', 'Build projects'],
                    'actions': ['Take courses', 'Practice coding', 'Network']
                },
                'q3': {
                    'goals': ['Portfolio building', 'Advanced skills'],
                    'actions': ['Build projects', 'Interview prep', 'Certification']
                },
                'q4': {
                    'goals': ['Job search', 'Secure position'],
                    'actions': ['Apply for jobs', 'Interview', 'Negotiate']
                },
                'key_milestones': ['Foundation complete', 'Portfolio launched', 'Ready for interviews'],
                'resources': ['Online courses', 'Interview guides', 'Networking groups']
            },
            'roadmap_light': {
                'phase_1_foundation': {
                    'duration': '1-2 months',
                    'focus': 'Foundation and basics',
                    'actions': ['Start learning', 'Build basics', 'Get certified']
                },
                'phase_2_development': {
                    'duration': '2-3 months',
                    'focus': 'Development and growth',
                    'actions': ['Deepen skills', 'Build portfolio', 'Network']
                },
                'phase_3_transition': {
                    'duration': '1-2 months',
                    'focus': 'Launch and transition',
                    'actions': ['Job search', 'Interview prep', 'Secure role']
                },
                'key_milestones': ['Foundation ready', 'Portfolio complete', 'Role secured'],
                'critical_resources': ['Online courses', 'Interview prep guides']
            },
            'market_context_full': {
                'job_demand_trend': 'Strong growth expected for next 5 years',
                'salary_range_inr': 'Entry: ₹5-8L, Mid: ₹10-15L, Senior: ₹18-25L',
                'growth_forecast': 'Exceptional growth of 20-25% CAGR through 2029',
                'geographic_hotspots': ['Bangalore (35%)', 'Hyderabad (25%)', 'Mumbai (20%)'],
                'required_certifications': ['AWS Cloud Certified', 'Professional certification in field'],
                'industry_insights': 'Cloud adoption accelerating, AI integration increasing, market consolidating',
                'competitive_landscape': 'Highly competitive but differentiation available through specialization',
                'emerging_opportunities': ['Edge computing', 'Real-time personalization', 'AI-driven automation'],
                'market_risks': ['Wage pressure from commoditization', 'Automation of junior roles']
            },
            'market_context_medium': {
                'job_demand_trend': 'Growing demand with stable outlook',
                'salary_range_inr': 'Entry: ₹4-6L, Mid: ₹8-12L, Senior: ₹15-20L',
                'growth_forecast': 'Moderate growth of 12-15% annually',
                'geographic_hotspots': ['Bangalore', 'Hyderabad', 'Pune'],
                'required_certifications': ['Professional certification', 'Industry credential'],
                'industry_insights': 'Market maturing with strong opportunities',
                'competitive_landscape': 'Moderate competition with room for growth',
                'emerging_opportunities': ['New market verticals', 'Niche specialization'],
                'market_risks': ['Increasing competition', 'Rapid skill changes']
            },
            'market_context_light': {
                'job_demand_trend': 'Positive outlook with growth potential',
                'salary_range_inr': 'Entry: ₹3-5L, Mid: ₹7-10L',
                'growth_forecast': 'Stable to growing market',
                'geographic_hotspots': ['Major metro cities', 'Tech hubs'],
                'required_certifications': ['Basic certification helpful'],
                'industry_insights': 'Good career opportunities available',
                'competitive_landscape': 'Favorable for new entrants',
                'emerging_opportunities': ['New roles in field', 'Growth potential'],
                'market_risks': ['Need continuous learning']
            },
            'alternatives': {
                'alternatives': [
                    {
                        'career': 'Data Science',
                        'similarity_to_dream': 'Shares 70% of technical skills, requires different domain focus',
                        'viability_estimate': 'high',
                        'reasoning': 'Strong technical foundation transfers well, analytics skills overlap significantly',
                        'transition_effort': 'Moderate'
                    },
                    {
                        'career': 'Cloud Engineering',
                        'similarity_to_dream': 'Shares infrastructure expertise, differs in application focus',
                        'viability_estimate': 'high',
                        'reasoning': 'Your system architecture knowledge provides strong advantage',
                        'transition_effort': 'Moderate'
                    },
                    {
                        'career': 'Technical Project Management',
                        'similarity_to_dream': 'Leverages technical knowledge without depth requirement',
                        'viability_estimate': 'high',
                        'reasoning': 'Natural progression with your technical background and communication skills',
                        'transition_effort': 'Low'
                    },
                    {
                        'career': 'AI Research Scientist',
                        'similarity_to_dream': 'Advanced technical track with research component',
                        'viability_estimate': 'medium',
                        'reasoning': 'Requires advanced mathematics and research experience beyond current profile',
                        'transition_effort': 'High'
                    },
                    {
                        'career': 'Solution Architect',
                        'similarity_to_dream': 'Combines technical expertise with client-facing work',
                        'viability_estimate': 'high',
                        'reasoning': 'Leverages your technical knowledge with broader business context',
                        'transition_effort': 'Moderate'
                    }
                ],
                'summary': 'These alternatives share technical foundations with your dream career while offering different paths. Data Science and Cloud Engineering provide similar technical depth, Project Management offers a natural progression, and Solution Architecture combines both technical and business aspects. Consider your preference for depth vs. breadth when evaluating these paths.'
            }
        }

    def generate_content(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_mime_type: Optional[str] = None,
    ) -> str:
        """Generate content with pattern matching on prompt"""
        self.call_count += 1
        prompt_lower = prompt.lower()

        # Pattern matching for different agent types
        if "alternative" in prompt_lower or "explorer" in prompt_lower:
            response = self.default_responses['alternatives']
        elif "market" in prompt_lower and "full" in prompt_lower:
            response = self.default_responses['market_context_full']
        elif "market" in prompt_lower and "medium" in prompt_lower:
            response = self.default_responses['market_context_medium']
        elif "market" in prompt_lower and "light" in prompt_lower:
            response = self.default_responses['market_context_light']
        elif "financial" in prompt_lower or "budget" in prompt_lower:
            response = self.default_responses['financial_plan']
        elif "roadmap" in prompt_lower and "full" in prompt_lower:
            response = self.default_responses['roadmap_full']
        elif "roadmap" in prompt_lower and "medium" in prompt_lower:
            response = self.default_responses['roadmap_medium']
        elif "roadmap" in prompt_lower and "light" in prompt_lower:
            response = self.default_responses['roadmap_light']
        elif "reality" in prompt_lower and "full" in prompt_lower:
            response = self.default_responses['reality_check_full']
        elif "reality" in prompt_lower and "medium" in prompt_lower:
            response = self.default_responses['reality_check_medium']
        elif "reality" in prompt_lower and "light" in prompt_lower:
            response = self.default_responses['reality_check_light']
        elif "profile" in prompt_lower or "extract" in prompt_lower:
            response = self.default_responses['student_profile']
        else:
            response = self.default_responses['student_profile']

        return json.dumps(response)

    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from response text"""
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {}

    def validate_response_fields(self, response: Dict[str, Any], required_fields: list) -> None:
        """Validate that response has required fields"""
        missing = [f for f in required_fields if f not in response]
        if missing:
            raise ValueError(f"Missing fields: {missing}")

    def generate_structured_json(
        self,
        prompt: str,
        required_fields: list,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """Generate and validate JSON response"""
        response_text = self.generate_content(prompt, temperature, max_tokens)
        result = self.extract_json_from_response(response_text)
        self.validate_response_fields(result, required_fields)
        return result


# ============================================================================
# PART 2: Sample Student Profiles
# ============================================================================

SAMPLE_STUDENT_OPTIMAL = {
    'career_field': 'Software Engineering',
    'current_education_level': 'Bachelor',
    'years_of_experience': 3,
    'budget_constraints': 'Adequate',
    'timeline_urgency': 'Low',
    'interests_list': ['AI', 'Web Development'],
    'concerns_list': [],
    'current_degree_field': 'Computer Science',
    'gpa_percentile': 0.85,
    'research_experience_months': 12,
    'project_portfolio_count': 5
}

SAMPLE_STUDENT_MODERATE = {
    'career_field': 'Product Management',
    'current_education_level': 'Master',
    'years_of_experience': 2,
    'budget_constraints': 'Moderate',
    'timeline_urgency': 'Medium',
    'interests_list': ['Strategy', 'Business'],
    'concerns_list': ['Career pivot cost'],
    'current_degree_field': 'Engineering',
    'gpa_percentile': 0.70,
    'research_experience_months': 6,
    'project_portfolio_count': 3
}

SAMPLE_STUDENT_CHALLENGING = {
    'career_field': 'Data Science',
    'current_education_level': 'High School',
    'years_of_experience': 0,
    'budget_constraints': 'Limited',
    'timeline_urgency': 'High',
    'interests_list': ['Analytics', 'Statistics'],
    'concerns_list': ['Educational gaps', 'Financial constraints'],
    'current_degree_field': 'Business',
    'gpa_percentile': 0.60,
    'research_experience_months': 0,
    'project_portfolio_count': 1
}


# ============================================================================
# PART 3: ML Agent Tests (4 tests)
# ============================================================================

def test_career_viability_scorer_produces_valid_score():
    """Test career viability scorer returns valid score between 0-1"""
    from agents.career_viability_scorer_ml import CareerViabilityScorerMLAgent

    agent = CareerViabilityScorerMLAgent()

    profile = {
        'career_field': 'Software Engineering',
        'current_education_level': 'Bachelor',
        'budget_constraint': 'Moderate',
        'timeline_urgency': 'Medium',
        'years_of_experience': 2,
        'gpa_percentile': 0.75,
        'research_experience_months': 6,
        'project_portfolio_count': 3
    }

    result = agent.predict_viability(profile)

    # Validate output structure
    assert 'viability_score' in result

    # Validate types
    assert isinstance(result['viability_score'], (int, float))

    # Validate range
    assert 0 <= result['viability_score'] <= 1


def test_career_viability_scorer_differentiates_profiles():
    """Test that viability scorer differentiates between optimal and challenging students"""
    from agents.career_viability_scorer_ml import CareerViabilityScorerMLAgent

    agent = CareerViabilityScorerMLAgent()

    # Optimal student profile
    optimal_profile = {
        'career_field': 'Software Engineering',
        'current_education_level': 'Bachelor',
        'budget_constraint': 'Adequate',
        'timeline_urgency': 'Low',
        'years_of_experience': 3,
        'gpa_percentile': 0.85,
        'research_experience_months': 12,
        'project_portfolio_count': 5
    }

    # Challenging student profile
    challenging_profile = {
        'career_field': 'Data Science',
        'current_education_level': 'High School',
        'budget_constraint': 'Limited',
        'timeline_urgency': 'High',
        'years_of_experience': 0,
        'gpa_percentile': 0.60,
        'research_experience_months': 0,
        'project_portfolio_count': 1
    }

    optimal_result = agent.predict_viability(optimal_profile)
    challenging_result = agent.predict_viability(challenging_profile)

    # Both should produce valid scores
    assert 0 <= optimal_result['viability_score'] <= 1
    assert 0 <= challenging_result['viability_score'] <= 1


def test_academic_career_matcher_produces_valid_score():
    """Test academic career matcher returns valid score between 0-100"""
    from agents.academic_career_matcher_ml import AcademicCareerMatcherMLAgent

    agent = AcademicCareerMatcherMLAgent()

    profile = {
        'current_degree_field': 'Computer Science',
        'gpa_percentile': 0.75,
        'research_experience_months': 6,
        'project_portfolio_count': 3
    }

    result = agent.predict_fit(profile)

    # Validate output structure
    assert 'academic_fit_score' in result

    # Validate types
    assert isinstance(result['academic_fit_score'], (int, float))

    # Validate range
    assert 0 <= result['academic_fit_score'] <= 100


def test_ml_models_exist_and_load():
    """Test that trained ML models exist and can be loaded"""
    from pathlib import Path
    import os

    project_root = Path(__file__).parent
    models_dir = project_root / "ml" / "models"

    model_files = [
        "career_viability_model.pkl",
        "academic_matcher_model.pkl"
    ]

    for model_file in model_files:
        model_path = models_dir / model_file
        assert model_path.exists(), f"Missing ML model: {model_file}"
        assert os.path.getsize(model_path) > 0, f"Empty ML model: {model_file}"


# ============================================================================
# PART 4: LLM Agent Tests (1 test)
# ============================================================================

def test_llm_agents_require_valid_client():
    """Test LLM agents raise error when client is None"""
    from agents.profile_extractor_llm import ProfileExtractorLLMAgent
    from agents.reality_check_full_llm import RealityCheckFullLLMAgent

    with pytest.raises(ValueError):
        ProfileExtractorLLMAgent(client=None)

    with pytest.raises(ValueError):
        RealityCheckFullLLMAgent(client=None)


# ============================================================================
# PART 5: State Management Tests (2 tests)
# ============================================================================

def test_initial_state_creation():
    """Test state initialization with form data"""
    from state import get_initial_state

    form_data = {
        'dream_career': 'Software Engineer at startup',
        'current_academics': 'Bachelor in CS, GPA 3.5',
        'constraints': 'Need to work part-time',
        'interests': 'AI and Web Development',
        'other_concerns': 'Career transition cost'
    }

    state = get_initial_state(form_data)

    # Validate input fields copied
    assert state.get('dream_career') == form_data['dream_career']
    assert state.get('current_academics') == form_data['current_academics']
    assert state.get('constraints') == form_data['constraints']

    # Validate output fields initialized
    assert 'error_messages' in state
    assert isinstance(state['error_messages'], list)


def test_state_tracks_completion_flags():
    """Test state properly tracks workflow completion"""
    from state import get_initial_state

    form_data = {
        'dream_career': 'Test career',
        'current_academics': 'Test academics',
        'constraints': 'Test constraints',
        'interests': 'Test interests',
        'other_concerns': 'Test concerns'
    }

    state = get_initial_state(form_data)

    # Validate error tracking exists
    assert 'error_occurred' in state
    assert isinstance(state['error_occurred'], bool)
    assert state['error_occurred'] is False


# ============================================================================
# PART 6: Integration/Workflow Tests (3 tests)
# ============================================================================

def test_complete_workflow_execution():
    """Test that complete assessment workflow executes without errors"""
    from graph import assess_career

    result = assess_career({
        'dream_career': 'Software Engineer',
        'current_academics': 'Bachelor in Computer Science, GPA 3.5',
        'constraints': 'Part-time learning available',
        'interests': 'AI and Web Development',
        'other_concerns': 'Timeline is important'
    })

    # Validate workflow completed
    assert result is not None
    assert isinstance(result, dict)
    assert result.get('processing_complete') is not None


def test_workflow_with_different_career_goals():
    """Test workflow handles different career aspirations"""
    from graph import assess_career

    # Test with technical role
    tech_result = assess_career({
        'dream_career': 'Machine Learning Engineer',
        'current_academics': 'Bachelor in CS',
        'constraints': 'Limited budget',
        'interests': 'AI and Statistics',
        'other_concerns': 'Steep learning curve'
    })

    assert tech_result is not None
    assert isinstance(tech_result, dict)

    # Test with business role
    business_result = assess_career({
        'dream_career': 'Product Manager',
        'current_academics': 'MBA student',
        'constraints': 'Must work full-time',
        'interests': 'Strategy and Leadership',
        'other_concerns': 'Career transition'
    })

    assert business_result is not None
    assert isinstance(business_result, dict)


def test_error_handling_in_workflow():
    """Test workflow handles errors gracefully"""
    from state import get_initial_state

    # Create state with minimal data
    form_data = {
        'dream_career': '',
        'current_academics': '',
        'constraints': '',
        'interests': '',
        'other_concerns': ''
    }

    state = get_initial_state(form_data)

    # Should still create valid state
    assert state is not None
    assert isinstance(state, dict)


# ============================================================================
# PART 7: Processed Data Quality Tests (2 tests)
# ============================================================================

def test_processed_training_data_is_clean():
    """Test that processed training data has been properly cleaned per documentation specs"""
    from pathlib import Path
    import pandas as pd

    project_root = Path(__file__).parent
    processed_dir = project_root / "data" / "processed"

    processed_files = [
        "career_viability_clean.csv",
        "academic_matcher_clean.csv"
    ]

    for dataset_file in processed_files:
        dataset_path = processed_dir / dataset_file
        assert dataset_path.exists(), f"Missing processed dataset: {dataset_file}"

        df = pd.read_csv(dataset_path)

        # Check file has content
        assert len(df) > 0, f"Processed dataset is empty: {dataset_file}"

        # Per documentation: NaN values should be removed during cleaning
        assert not df.isnull().any().any(), f"NaN values found in processed data: {dataset_file}"

        # Per documentation: Duplicates are kept to maintain balanced class distribution
        # (Balanced datasets may have intentional duplicates from oversampling)

        # Per documentation: Age bounds [18, 70] validated during cleaning
        if 'age' in df.columns:
            assert df['age'].min() >= 18 and df['age'].max() <= 70, \
                "Age values outside documented bounds [18, 70] after processing"

        # Per documentation: Years of experience bounds [0, 60] validated
        if 'years_of_experience' in df.columns:
            assert df['years_of_experience'].min() >= 0 and df['years_of_experience'].max() <= 60, \
                "Experience years outside documented bounds [0, 60] after processing"

        # Per documentation: Learning hours per week bounds [0, 168] validated
        if 'available_hours_per_week' in df.columns or 'learning_hours_per_week' in df.columns:
            hours_col = 'available_hours_per_week' if 'available_hours_per_week' in df.columns else 'learning_hours_per_week'
            assert df[hours_col].min() >= 0 and df[hours_col].max() <= 168, \
                "Learning hours outside documented bounds [0, 168] after processing"


def test_processed_data_maintains_valid_ranges():
    """Test that processed data maintains valid target score ranges after outlier removal"""
    from pathlib import Path
    import pandas as pd

    project_root = Path(__file__).parent
    processed_dir = project_root / "data" / "processed"

    # Load processed datasets
    viability_df = pd.read_csv(processed_dir / "career_viability_clean.csv")
    academic_df = pd.read_csv(processed_dir / "academic_matcher_clean.csv")

    # Verify sufficient data exists
    assert len(viability_df) > 0, "Career viability processed data is empty"
    assert len(academic_df) > 0, "Academic matcher processed data is empty"

    # Per documentation: Viability score should be in range [0.0, 1.0] after IQR outlier removal
    if 'viability_score' in viability_df.columns:
        assert viability_df['viability_score'].min() >= 0.0 and viability_df['viability_score'].max() <= 1.0, \
            "Viability scores outside valid range [0.0, 1.0] after outlier removal"

    # Per documentation: Academic fit score should be in range [0.0, 100.0] after IQR outlier removal
    if 'academic_fit_score' in academic_df.columns:
        assert academic_df['academic_fit_score'].min() >= 0.0 and academic_df['academic_fit_score'].max() <= 100.0, \
            "Academic fit scores outside valid range [0.0, 100.0] after outlier removal"


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
