"""Profile Extractor Node - extracts structured profile from free text."""

from typing import Dict, Any
from state import EduQuestState
from agents.profile_extractor_llm import ProfileExtractorLLMAgent
import sys


def profile_extractor_node(state : EduQuestState , client) -> dict:
    """Return only modified fields."""
    try:
        agent = ProfileExtractorLLMAgent(client)
        raw = state.get("raw_inputs",{})
        
        # DEBUG
        dream_career = raw.get("dream_career", "")
        print(f"\nPROFILE EXTRACTOR DEBUG:", file=sys.stderr)
        print(f"  Input dream_career: '{dream_career}'", file=sys.stderr)
        
        result = agent.extract_profile(raw)
        
        # DEBUG
        print(f"  Extracted career_field: '{result.get('career_field', '')}'", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)
        
        return {"extracted_profile": result}

    except Exception as e:
        print(f"ERROR in profile extractor: {str(e)}", file=sys.stderr)
        return {"extracted_profile": {"status" : "error" , "message" : str(e)}}
