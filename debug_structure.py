#!/usr/bin/env python3
"""Debug script to inspect actual output structure."""

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
print("ACTUAL DATA STRUCTURE FOR DISPLAY")
print("="*80)

# Check roadmap structure
print("\n[ROADMAP OUTPUT]")
roadmap = result.get("roadmap_output", {})
print(json.dumps(roadmap, indent=2)[:500])

# Check financial plan structure
print("\n[FINANCIAL PLAN OUTPUT]")
financial = result.get("financial_plan_output", {})
print(json.dumps(financial, indent=2)[:500])

# Check market context
print("\n[MARKET CONTEXT]")
market = result.get("market_context", {})
print(json.dumps(market, indent=2)[:500])

# Check reality check
print("\n[REALITY CHECK OUTPUT]")
reality = result.get("reality_check_output", {})
print(json.dumps(reality, indent=2)[:500])

# Check alternatives
print("\n[ALTERNATIVES OUTPUT]")
alternatives = result.get("alternatives_output", {})
print(json.dumps(alternatives, indent=2)[:500])

# Check aggregated_output
print("\n[AGGREGATED OUTPUT]")
agg = result.get("aggregated_output", {})
print("Keys:", list(agg.keys()))
for key in ['roadmap', 'financial_plan', 'market_context', 'reality_check', 'alternatives']:
    if key in agg:
        print(f"\n  {key}:")
        print(json.dumps(agg[key], indent=2)[:300])
