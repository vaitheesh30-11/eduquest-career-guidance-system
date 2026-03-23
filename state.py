"""
EduQuest State Definition - TypedDict for workflow state management.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from datetime import datetime,timezone
from operator import add
import operator


def keep_first(existing,new):
    if existing :
        return existing
    return new

def set_true(existing,new):
    return existing or new


class EduQuestState(TypedDict,total=False):
    request_id:str
    analysis_timestamp:str
    error_occurred:bool
    error_messages:List[str]
    processing_complete:bool

    raw_inputs:Dict[str,Any]
    dream_career:str
    current_academics:str
    constraints:str
    interests:str
    other_concerns:str


    validation_errors:List[str]
    parsing_complete:bool
    extracted_profile:Dict[str,Any]
    profile_extraction_complete:bool
    career_field:str
    education_level:str
    experience:str
    overall_feasibility:float
  
    viability_score:float
    viability_status:str
    academic_fit_score:float

    path_taken:str
    daily_budget_tier:str
    reality_check_output:Dict[str,Any]
    financial_plan_output:Dict[str,Any]
    roadmap_output:Dict[str,Any]
    alternatives_output:Dict[str,Any]
    market_context:Dict[str,Any]
    
    reality_check_medium_output:Dict[str,Any]
    roadmap_medium_output:Dict[str,Any]
    market_context_medium:Dict[str,Any]
    
    reality_check_light_output:Dict[str,Any]
    roadmap_light_output:Dict[str,Any]
    market_context_light:Dict[str,Any]

    aggregated_output:Dict[str,Any]

def get_initial_state(form_data:Dict[str,Any])->EduQuestState:
    raw_inputs = {
        "dream_career": form_data.get("dream_career", ""),
        "current_academics": form_data.get("current_academics", ""),
        "constraints": form_data.get("constraints", ""),
        "interests": form_data.get("interests", ""),
        "other_concerns": form_data.get("other_concerns", "")
    }
    
    state:EduQuestState={
        "request_id":form_data.get("request_id",""),
        "analysis_timestamp":
        form_data.get("analysis_timestamp",datetime.now(timezone.utc).isoformat()),
        "error_occurred":False,
        "error_messages":[],
        "processing_complete":False,
        "raw_inputs": raw_inputs,
        "dream_career":form_data.get("dream_career",""),
        "current_academics":form_data.get("current_academics",""),
        "constraints":form_data.get("constraints",""),
        "interests":form_data.get("interests",""),
        "other_concerns":form_data.get("other_concerns",""),
        "validation_errors":[],
        "parsing_complete":False,
        "extracted_profile":{},
        "profile_extracted_complete":False,
        
        "viability_score":0.0,
        "academic_fit_score":0.0,
        "viability_status":"",
        "path_taken":"",
        "daily_budget_tier":"",
        "overall_feasibility":0.0,
       
        "aggregated_output":{}
    }
    return state


