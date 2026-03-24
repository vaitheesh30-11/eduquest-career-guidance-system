"""Alternative Explorer Node - HARD path only."""

from state import EduQuestState
from agents.alternative_explorer_llm import AlternativeExplorerLLMAgent
import sys


def alternative_explorer_node(state: EduQuestState, client)-> dict:
    """Return only modified fields."""
    try:
        agent=AlternativeExplorerLLMAgent(client)
        profile=state.get("extracted_profile",{})
        viability_score=state.get("viability_score", 0)
        
        # DEBUG
        career_field = profile.get("career_field", "")
        print(f"\nALTERNATIVE EXPLORER DEBUG:", file=sys.stderr)
        print(f"  Profile career_field: '{career_field}'", file=sys.stderr)
        print(f"  Viability score: {viability_score}", file=sys.stderr)

        result=agent.explore_alternatives(profile, {"viability_score": viability_score})
        
        # DEBUG
        alternatives = result.get("alternatives", [])
        if alternatives:
            print(f"  Generated alternatives: {[alt.get('career') for alt in alternatives[:2]]}", file=sys.stderr)
        print(f"{'='*70}\n", file=sys.stderr)
        
        return {"alternatives_output": result}
        
    except Exception as e:
        print(f"ERROR in alternative explorer: {str(e)}", file=sys.stderr)
        return {"alternatives_output": {"status":"error","message":str(e)}}
