"""ML Results Merger Node - pure logic node."""

from state import EduQuestState

def ml_results_merger_node(state:EduQuestState)->dict:
    """Return only modified fields."""
    try:
        viability = state.get("viability_score",0)
        academic_fit = state.get("academic_fit_score",0)
        academic_scaled = academic_fit/100 if academic_fit else 0
        overall = (0.6*viability) +(0.4*academic_scaled) if viability else 0
        overall = max(0.0,min(1.0,overall))
        
        return {'overall_feasibility': overall}
    except Exception as e:
        return {'overall_feasibility': None, 'ml_merge_error': str(e)}
        

