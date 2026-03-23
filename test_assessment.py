#!/usr/bin/env python3
"""Quick test script to verify assessment flow works."""

import sys
from graph import assess_career

# Test data
test_form = {
    "dream_career": "Software Engineer",
    "current_academics": "Bachelor's in Computer Science",
    "constraints": "Prefer remote work",
    "interests": "AI, Machine Learning, Web Development",
    "other_concerns": "Work-life balance"
}

print("Testing career assessment...")
print(f"Input: {test_form}\n")

try:
    result = assess_career(test_form)
    
    print("=" * 60)
    print("ASSESSMENT RESULT")
    print("=" * 60)
    
    # Check critical fields
    print(f"Processing Complete: {result.get('processing_complete')}")
    print(f"Error Occurred: {result.get('error_occurred')}")
    if result.get('error_occurred'):
        print(f"Error Message: {result.get('error_message')}")
    
    print(f"\nVIABILITY SCORE: {result.get('viability_score')}")
    print(f"ACADEMIC FIT SCORE: {result.get('academic_fit_score')}")
    print(f"PATH TAKEN: {result.get('path_taken')}")
    print(f"OVERALL FEASIBILITY: {result.get('overall_feasibility')}")
    
    print(f"\nExtracted Profile: {result.get('extracted_profile')}")
    
    # Check path-specific outputs
    if result.get('path_taken') == 'HARD_PATH':
        print(f"\nRoadmap Output: {result.get('roadmap_output')}")
        print(f"Financial Plan: {result.get('financial_plan_output')}")
    elif result.get('path_taken') == 'MEDIUM_PATH':
        print(f"\nRoadmap Medium Output: {result.get('roadmap_medium_output')}")
    else:
        print(f"\nRoadmap Light Output: {result.get('roadmap_light_output')}")
    
    print("\n" + "=" * 60)
    if result.get('viability_score') and result.get('academic_fit_score'):
        print("✓ SUCCESS: Scores calculated correctly!")
    else:
        print("✗ ISSUE: Scores are missing or zero")
        
except Exception as e:
    print(f"ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
