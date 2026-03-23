#!/usr/bin/env python3
"""Quick test script to verify fixes work."""

import sys
import traceback
from graph import assess_career

# Sample input
test_input = {
    "dream_career": "Data Scientist",
    "current_academics": "B.Tech Computer Science",
    "constraints": "Moderate Budget",
    "interests": "ML, AI, Data Analysis",
    "other_concerns": "Competition for entry-level roles"
}

print("=" * 60)
print("Testing Career Assessment with Fixes")
print("=" * 60)

try:
    print("\n[1] Running assessment...")
    result = assess_career(test_input)
    
    print("\n[2] Assessment completed successfully!")
    print("\n[3] Checking results:")
    
    if result:
        print(f"  - Viability Score: {result.get('viability_score', 'N/A')}")
        print(f"  - Academic Fit: {result.get('academic_fit_score', 'N/A')}")
        print(f"  - Path Taken: {result.get('path_taken', 'N/A')}")
        print(f"  - Aggregated Output Keys: {list(result.get('aggregated_output', {}).keys())}")
        
        agg = result.get('aggregated_output', {})
        print(f"\n[4] Aggregated output structure:")
        for key in agg.keys():
            print(f"  - {key}: {type(agg[key]).__name__}")
    else:
        print("  No result returned!")
    
    print("\n" + "=" * 60)
    print("✅ TEST PASSED - No errors occurred")
    print("=" * 60)

except Exception as e:
    print("\n" + "=" * 60)
    print("❌ TEST FAILED - Error occurred:")
    print("=" * 60)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    traceback.print_exc()
    sys.exit(1)
