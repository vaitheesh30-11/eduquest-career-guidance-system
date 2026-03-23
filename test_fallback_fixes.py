#!/usr/bin/env python3
"""Test improved fallback responses."""

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
print("TESTING IMPROVED FALLBACK RESPONSES")
print("="*80)

# Check for any "Mock LLM" or "Fallback" strings
mock_count = 0
fallback_count = 0

def check_string(obj, target_low):
    count = 0
    if isinstance(obj, str):
        if target_low in obj.lower():
            count += 1
    elif isinstance(obj, dict):
        for v in obj.values():
            count += check_string(v, target_low)
    elif isinstance(obj, list):
        for item in obj:
            count += check_string(item, target_low)
    return count

mock_count = check_string(result, "mock llm")
fallback_count = check_string(result, "fallback recommendations")

print(f"\n[CHECK] 'Mock LLM' occurrences: {mock_count}")
print(f"[CHECK] 'Fallback recommendations' occurrences: {fallback_count}")

print("\n" + "-"*80)
print("MARKET CONTEXT INSIGHTS:")
print("-"*80)
market = result.get("market_context", {})
insights = market.get("industry_insights", "")
print(f"{insights[:200]}...")

print("\n" + "-"*80)
print("REALITY CHECK ASSESSMENT:")
print("-"*80)
reality = result.get("reality_check_output", {})
assessment = reality.get("honest_assessment", "")
print(f"{assessment[:200]}...")

print("\n" + "-"*80)
print("ALTERNATIVES SUMMARY:")
print("-"*80)
alternatives = result.get("alternatives_output", {})
summary = alternatives.get("summary", "")
alternatives_list = alternatives.get("alternatives", [])
print(f"Summary: {summary}")
if alternatives_list:
    print(f"First alternative: {alternatives_list[0].get('career')}")
    print(f"Reasoning: {alternatives_list[0].get('reasoning', '')[:150]}...")

print("\n" + "="*80)
if mock_count == 0 and fallback_count == 0:
    print("[SUCCESS] No more Mock LLM or Fallback messages!")
else:
    print("[WARNING] Still found mock/fallback messages")
print("="*80)
