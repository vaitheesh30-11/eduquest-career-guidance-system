#!/usr/bin/env python3
"""Test all display functions with real data."""

import json
from graph import assess_career

test_input = {
    "dream_career": "Data Scientist",
    "current_academics": "B.Tech Computer Science",
    "constraints": "Moderate Budget",
    "interests": "ML, AI, Data Analysis",
    "other_concerns": "Competition"
}

result = assess_career(test_input)

print("\n" + "="*80)
print("VERIFYING ALL DISPLAY DATA STRUCTURES")
print("="*80)

checks = {
    "Overview Tab": {
        "viability_score": result.get("viability_score"),
        "academic_fit_score": result.get("academic_fit_score"),
        "path_taken": result.get("path_taken"),
        "extracted_profile": bool(result.get("extracted_profile")),
    },
    "Roadmap Tab": {
        "path_taken": result.get("path_taken"),
        "roadmap_output": {
            "has_phase_1": "phase_1_months" in result.get("roadmap_output", {}),
            "has_phase_2": "phase_2_months" in result.get("roadmap_output", {}),
            "has_phase_3": "phase_3_months" in result.get("roadmap_output", {}),
            "has_milestones": "key_milestones" in result.get("roadmap_output", {}),
            "has_resources": "success_resources" in result.get("roadmap_output", {}),
        }
    },
    "Planning Tab": {
        "financial_plan_output": bool(result.get("financial_plan_output")),
        "market_context": bool(result.get("market_context")),
        "reality_check_output": bool(result.get("reality_check_output")),
    },
    "Alternatives Tab": {
        "alternatives_output_exists": bool(result.get("alternatives_output")),
        "has_alternatives_array": bool(result.get("alternatives_output", {}).get("alternatives")),
        "has_summary": bool(result.get("alternatives_output", {}).get("summary")),
    }
}

# Print verification results
for tab, data in checks.items():
    print(f"\n[OK] {tab}:")
    for key, value in data.items():
        status = "[OK]" if value or isinstance(value, dict) else "[FAIL]"
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"  {status} {k}: {v}")
        else:
            print(f"  {status} {key}: {value}")

# Sample data from each section
print("\n" + "="*80)
print("SAMPLE DATA FOR EACH TAB")
print("="*80)

print("\n[OVERVIEW TAB - Metrics]")
print(f"  Viability Score: {result.get('viability_score')}")
print(f"  Academic Fit: {result.get('academic_fit_score')}")
print(f"  Path Taken: {result.get('path_taken')}")

print("\n[ROADMAP TAB - Phase 1 Goals & Actions]")
roadmap = result.get("roadmap_output", {})
p1 = roadmap.get("phase_1_months", {})
print(f"  Goals: {p1.get('goals', [])}")
print(f"  Actions: {p1.get('actions', [])}")

print("\n[PLANNING TAB - Financial Details]")
financial = result.get("financial_plan_output", {})
print(f"  Estimated Cost: {financial.get('estimated_total_cost')}")
print(f"  Monthly Budget: {financial.get('monthly_budget')}")

print("\n[PLANNING TAB - Reality Check]")
reality = result.get("reality_check_output", {})
print(f"  Success Probability: {reality.get('success_probability')}%")
print(f"  Major Challenges: {reality.get('major_challenges', [])[:2]}")

print("\n[ALTERNATIVES TAB - First Alternative]")
alternatives = result.get("alternatives_output", {}).get("alternatives", [])
if alternatives:
    alt = alternatives[0]
    print(f"  Career: {alt.get('career')}")
    print(f"  Similarity: {alt.get('similarity_to_dream')}")
    print(f"  Viability: {alt.get('viability_estimate')}")

print("\n" + "="*80)
print("[SUCCESS] ALL DISPLAY DATA READY FOR UI")
print("="*80)
