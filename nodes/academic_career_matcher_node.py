"""Academic Career Matcher Node - ML predictions."""

from state import EduQuestState 
from agents.academic_career_matcher_ml import AcademicCareerMatcherMLAgent
import sys

def academic_career_matcher_node(state: EduQuestState)->dict:
    """Return only modified fields to avoid concurrent update conflicts."""
    try:
        agent=AcademicCareerMatcherMLAgent()
        profile=state.get("extracted_profile", {})
        
        print(f"DEBUG: Profile in academic matcher: {profile}", file=sys.stderr)
        
        result=agent.predict_fit(profile)
        
        print(f"DEBUG: Academic fit result: {result}", file=sys.stderr)
        
        # Return only modified fields
        return {
            "academic_fit_score": result.get("academic_fit_score"),
            "academic_status": result.get("status")
        }

    except Exception as e:
        print(f"DEBUG: Academic matcher exception: {str(e)}", file=sys.stderr)
        # Return only modified fields
        return {
            "academic_fit_score": None,
            "academic_status": "error",
            "academic_error": str(e)
        }
