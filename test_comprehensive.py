#!/usr/bin/env python3
"""Comprehensive end-to-end test to verify all fixes."""

import sys
import json
import traceback
from graph import assess_career

test_cases = [
    {
        "name": "High-viability Data Scientist path",
        "input": {
            "dream_career": "Data Scientist",
            "current_academics": "B.Tech Computer Science, GPA 3.8",
            "constraints": "Moderate Budget, 6 months timeline",
            "interests": "ML, AI, Computer Vision, Kaggle competitions",
            "other_concerns": "Fear of competition"
        }
    }
]

def verify_result(result):
    """Verify required fields exist and have proper values."""
    issues = []
    
    # Check top-level scoring fields
    viability = result.get('viability_score')
    if viability is None or viability == 'N/A':
        issues.append("viability_score is None or N/A")
    elif not isinstance(viability, (int, float)):
        issues.append(f"viability_score is wrong type: {type(viability)}")
    else:
        print(f"  ✓ viability_score = {viability}")
    
    academic = result.get('academic_fit_score')
    if academic is None or academic == 'N/A':
        issues.append("academic_fit_score is None or N/A")
    elif not isinstance(academic, (int, float)):
        issues.append(f"academic_fit_score is wrong type: {type(academic)}")
    else:
        print(f"  ✓ academic_fit_score = {academic}")
    
    path = result.get('path_taken')
    if not path or path == 'N/A':
        issues.append("path_taken is empty or N/A")
    else:
        print(f"  ✓ path_taken = {path}")
    
    # Check aggregated output structure
    agg_output = result.get('aggregated_output')
    if not agg_output:
        issues.append("aggregated_output is missing or empty")
    else:
        print(f"  ✓ aggregated_output exists with keys: {list(agg_output.keys())}")
        
        # Verify nested structure
        required_agg_keys = ['profile', 'roadmap', 'financial_plan', 'market_context', 'reality_check']
        for key in required_agg_keys:
            if key not in agg_output:
                issues.append(f"aggregated_output missing key: {key}")
            else:
                print(f"    ✓ aggregated_output.{key} exists")
    
    return issues

print("=" * 70)
print("COMPREHENSIVE END-TO-END VERIFICATION TEST")
print("=" * 70)

total_passed = 0
total_failed = 0

for test in test_cases:
    print(f"\nTest: {test['name']}")
    print("-" * 70)
    
    try:
        result = assess_career(test['input'])
        issues = verify_result(result)
        
        if not issues:
            print("\n✅ TEST PASSED - All validations passed!")
            total_passed += 1
        else:
            print("\n❌ TEST FAILED - Issues found:")
            for issue in issues:
                print(f"  - {issue}")
            total_failed += 1
            
    except Exception as e:
        print(f"\n❌ TEST FAILED - Exception occurred:")
        print(f"  Error: {str(e)}")
        print(f"  Type: {type(e).__name__}")
        traceback.print_exc()
        total_failed += 1

print("\n" + "=" * 70)
print(f"RESULTS: {total_passed} passed, {total_failed} failed")
print("=" * 70)

if total_failed > 0:
    sys.exit(1)
