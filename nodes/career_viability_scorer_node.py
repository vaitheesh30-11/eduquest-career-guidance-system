"""Career Viability Scorer Node - ML predictions."""

from state import EduQuestState
from agents.career_viability_scorer_ml import CareerViabilityScorerMLAgent
import sys


def career_viability_scorer_node(state: EduQuestState)->dict:
    """Return only modified fields to avoid concurrent update conflicts."""
    try: 
        agent=CareerViabilityScorerMLAgent()
        profile=state.get("extracted_profile",{})
        
        print(f"DEBUG: Profile in viability scorer: {profile}", file=sys.stderr)
        
        result=agent.predict_viability(profile)
        
        print(f"DEBUG: Viability result: {result}", file=sys.stderr)
        
        # Return only modified fields
        return {
            "viability_score": result.get("viability_score"),
            "viability_status": result.get("status")
        }

    except Exception as e:
        print(f"DEBUG: Viability scorer exception: {str(e)}", file=sys.stderr)
        # Return only modified fields
        return {
            "viability_score": None,
            "viability_status": "error",
            "viability_error": str(e)
        }
