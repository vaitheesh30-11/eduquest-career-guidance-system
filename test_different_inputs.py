"""Test that different inputs produce different outputs."""

import sys
from utils.gemini_client import GeminiClient
from agents.base_llm_agent import BaseLLMAgent, extract_career_from_prompt
from agents.market_context_full_llm import MarketContextFullLLMAgent
from agents.alternative_explorer_llm import AlternativeExplorerLLMAgent
from agents.roadmap_builder_full_llm import RoadmapBuilderFullLLMAgent

def test_career_extraction():
    """Test that different careers are extracted correctly from prompts."""
    print("=" * 80)
    print("TEST 1: Career Extraction from Prompts")
    print("=" * 80)
    
    test_cases = [
        ("dream_career: Data Scientist\nAnalyze this", "Data Scientist"),
        ("I want to pursue a career in Software Engineer", "Software Engineer"),
        ("dream career: Product Manager", "Product Manager"),
        ("User dream_career: UX Designer", "UX Designer"),
        ("Provide analysis for Machine Learning Engineer", "Machine Learning Engineer"),
    ]
    
    for prompt, expected_substr in test_cases:
        extracted = extract_career_from_prompt(prompt)
        match = expected_substr.lower() in extracted.lower()
        status = "[PASS]" if match else "[FAIL]"
        print(f"{status}: Extracted '{extracted}' (expected substring: '{expected_substr}')")
    
    print()

def test_mock_responses():
    """Test that mock responses are different for different careers."""
    print("=" * 80)
    print("TEST 2: Mock Response Generation for Different Careers")
    print("=" * 80)
    
    client = GeminiClient()
    agent = BaseLLMAgent(client)
    
    # Test different career prompts
    prompts = [
        "Provide market analysis for dream_career: Data Scientist",
        "Provide market analysis for dream_career: Software Engineer",
        "Provide market analysis for dream_career: Product Manager",
    ]
    
    responses = []
    for prompt in prompts:
        response = agent.generate(prompt)
        responses.append(response)
        career = extract_career_from_prompt(prompt)
        print(f"\nCareer: {career}")
        print(f"Response: {response[:150]}...")
    
    # Check that responses are different
    print("\n" + "=" * 80)
    print("Uniqueness Check:")
    print("=" * 80)
    
    for i, resp1 in enumerate(responses):
        for j, resp2 in enumerate(responses[i+1:], start=i+1):
            similarity = len(set(resp1.split()) & set(resp2.split())) / len(set(resp1.split()) | set(resp2.split()))
            status = "[DIFFERENT]" if similarity < 0.5 else "[SIMILAR]"
            print(f"{status}: Response {i} vs {j} (overlap: {similarity:.1%})")
    
    print()

def test_market_context():
    """Test that market context is different for different careers."""
    print("=" * 80)
    print("TEST 3: Market Context for Different Careers")
    print("=" * 80)
    
    client = GeminiClient()
    agent = MarketContextFullLLMAgent(client)
    
    careers = ["Data Scientist", "Software Engineer", "UX Designer"]
    contexts = []
    
    for career in careers:
        context = agent.get_market_context(career, "Moderate")
        contexts.append(context)
        print(f"\nCareer: {career}")
        print(f"  Demand: {context.get('job_demand_trend')}")
        print(f"  Salary: {context.get('salary_rang_inr')}")
        print(f"  Hotspots: {context.get('geographic_hotspots')}")
        print(f"  Opportunities: {context.get('emerging_opportunities')}")
    
    print("\n" + "=" * 80)
    print("Context Differentiation:")
    print("=" * 80)
    
    # Check that at least some fields are different
    salary_1 = contexts[0].get('salary_rang_inr')
    salary_2 = contexts[1].get('salary_rang_inr')
    
    match = salary_1 != salary_2
    status = "[PASS]" if match else "[FAIL]"
    print(f"{status}: Different salaries generated (Data Scientist: {salary_1} vs Software Engineer: {salary_2})")
    
    print()

def test_alternatives():
    """Test that alternatives are different for different careers."""
    print("=" * 80)
    print("TEST 4: Alternative Careers for Different Dream Careers")
    print("=" * 80)
    
    client = GeminiClient()
    agent = AlternativeExplorerLLMAgent(client)
    
    profiles = [
        {"career_field": "Data Scientist", "gpa_percentile": 0.8},
        {"career_field": "Software Engineer", "gpa_percentile": 0.8},
    ]
    
    ml_results = {"viability_score": 0.75}
    
    for profile in profiles:
        result = agent.explore_alternatives(profile, ml_results)
        alts = result.get("alternatives", [])
        print(f"\nDream Career: {profile['career_field']}")
        print("Alternatives:")
        for alt in alts[:2]:  # Show first 2 alternatives
            print(f"  - {alt.get('career')} (similarity: {alt.get('similarity_to_dream')})")
    
    print()

def test_roadmap():
    """Test that roadmaps are different for different careers."""
    print("=" * 80)
    print("TEST 5: Roadmap for Different Careers")
    print("=" * 80)
    
    client = GeminiClient()
    agent = RoadmapBuilderFullLLMAgent(client)
    
    careers = ["Data Scientist", "Software Engineer"]
    
    for career in careers:
        profile = {
            "career_field": career,
            "constraints_summary": "Can dedicate 2-3 hours daily"
        }
        ml_results = {"viability_score": 0.75}
        
        roadmap = agent.generate_roadmap(profile, ml_results)
        
        print(f"\nCareer: {career}")
        phase1_goals = roadmap.get('phase_1_months', {}).get('goals', [])
        print(f"  Phase 1 Goals: {phase1_goals}")
        
        phase2_goals = roadmap.get('phase_2_months', {}).get('goals', [])
        print(f"  Phase 2 Goals: {phase2_goals}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTING CAREER-SPECIFIC RESPONSES")
    print("=" * 80 + "\n")
    
    test_career_extraction()
    test_mock_responses()
    test_market_context()
    test_alternatives()
    test_roadmap()
    
    print("=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)
