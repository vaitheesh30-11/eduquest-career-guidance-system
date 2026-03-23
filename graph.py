"""
Main graph interface for EduQuest career guidance system.
Defines the complete StateGraph structure and orchestration.
"""

from datetime import datetime, timezone
from typing import Dict, Any
from uuid import uuid4

from langgraph.graph import StateGraph, START, END
from state import EduQuestState, get_initial_state
from utils.gemini_client import GeminiClient
from nodes import (
    input_validator_node,
    profile_extractor_node,
    career_viability_scorer_node,
    academic_career_matcher_node,
    ml_results_merger_node,
    viability_router_node,
    reality_check_full_node,
    reality_check_medium_node,
    reality_check_light_node,
    financial_planner_node,
    roadmap_builder_full_node,
    roadmap_builder_medium_node,
    roadmap_builder_light_node,
    alternative_explorer_node,
    market_context_full_node,
    market_context_medium_node,
    market_context_light_node,
    output_aggregator_node,
)

# Routing threshold constants
HARD_PATH_THRESHOLD = 0.6
MEDIUM_PATH_THRESHOLD = 0.3
def build_eduquest_graph(client:GeminiClient):
    graph = StateGraph(EduQuestState)
    graph.add_node("validator",input_validator_node)
    graph.add_node("extractor",lambda s:profile_extractor_node(s, client))

    graph.add_node("viability_ml",career_viability_scorer_node)
    graph.add_node("academic_ml",academic_career_matcher_node)

    graph.add_node("ml_merge",ml_results_merger_node)

    graph.add_node("router",viability_router_node)

    graph.add_node("reality_full",lambda s:reality_check_full_node(s,client))
    graph.add_node("financial",lambda s: financial_planner_node(s,client))
    graph.add_node("roadmap_full",lambda s: roadmap_builder_full_node(s,client))
    graph.add_node("alternatives",lambda s:alternative_explorer_node(s,client))
    graph.add_node("market_full",lambda s:market_context_full_node(s,client))

    graph.add_node("reality_medium",lambda s:reality_check_medium_node(s,client))
    graph.add_node("roadmap_medium",lambda s: roadmap_builder_medium_node(s,client))
    graph.add_node("market_medium",lambda s: market_context_medium_node(s,client))

    graph.add_node("reality_light",lambda s:reality_check_light_node(s,client))
    graph.add_node("roadmap_light",lambda s: roadmap_builder_light_node(s,client))
    graph.add_node("market_light",lambda s: market_context_light_node(s,client))

    graph.add_node("aggregator", output_aggregator_node)

    graph.add_edge(START,"validator")
    graph.add_edge("validator","extractor")
    graph.add_edge("extractor","viability_ml")
    graph.add_edge("extractor","academic_ml")

    graph.add_edge("viability_ml","ml_merge")
    graph.add_edge("academic_ml","ml_merge")

    graph.add_edge("ml_merge","router")

    def route_paths(state:EduQuestState)->str:
        path = state.get("path_taken", "LIGHT_PATH")

        if path == "HARD_PATH":
            return "reality_full"
        elif path == "MEDIUM_PATH":
            return "reality_medium"
        else:
            return "reality_light"

    graph.add_conditional_edges(
        "router",
        route_paths,
        {
            "reality_full":"reality_full",
            "reality_medium":"reality_medium",
            "reality_light":"reality_light",
        },
    )

    graph.add_edge("reality_full","financial")
    graph.add_edge("financial","roadmap_full")
    graph.add_edge("roadmap_full","alternatives")
    graph.add_edge("alternatives","market_full")
    graph.add_edge("market_full","aggregator")

    graph.add_edge("reality_medium","roadmap_medium")
    graph.add_edge("roadmap_medium","market_medium")
    graph.add_edge("market_medium","aggregator")

    graph.add_edge("reality_light","roadmap_light")
    graph.add_edge("roadmap_light","market_light")
    graph.add_edge("market_light","aggregator")

    graph.add_edge("aggregator",END)
    return graph.compile()

def assess_career(form_data: Dict[str,str])-> Dict[str,Any]:
    try :
        form_data["request_id"]= str(uuid4())
        form_data["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()

        state = get_initial_state(form_data)
        client = GeminiClient()

        graph = build_eduquest_graph(client)
        final_state = graph.invoke(state)
        final_state["processing_complete"] = True
        final_state['error_occured'] = False
        
        import sys
        print(f"DEBUG: Final state keys: {list(final_state.keys())}", file=sys.stderr)
        print(f"DEBUG: viability_score={final_state.get('viability_score')}", file=sys.stderr)
        print(f"DEBUG: academic_fit_score={final_state.get('academic_fit_score')}", file=sys.stderr)
        print(f"DEBUG: path_taken={final_state.get('path_taken')}", file=sys.stderr)
        
        return final_state
    except Exception as e :
        import sys
        print(f"DEBUG: Exception in assess_career: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            "processing_complete":True,
            "error_occurred":True,
            "error_message":str(e),
        }



def get_career_summary(assessment_result: Dict[str,Any]) -> Dict[str,Any]:
    return {
        "user_profile": assessment_result.get("extracted_profile"),
        "ml_predictions":{
            "viability_score": assessment_result.get("viability_score"),
            "academic_fit_score": assessment_result.get("academic_fit_score"),
            "overall_feasibility": assessment_result.get("overall_feasibility"),
        },
        "path_analysis":{
            "path_taken": assessment_result.get("path_taken"),
            "daily_budget_tier":assessment_result.get("daily_budget_tier"),
        },
        "outputs":assessment_result.get("aggregated_output"),
        "system_metadata":{
            "request_id":assessment_result.get("request_id"),
            "analysis_timestamp":assessment_result.get("analysis_timestamp"),
        }
    }

def get_workflow_structure()-> Dict[str,Any]:
    return {
        "workflow_name": "EduQuest",
        "total_nodes":20,
        "paths":{
            "HARD_PATH":[
                "reality_check_full",
                "financial_planner",
                "roadmap_builder_full",
                "alternative_explorer",
                "market_context_full",
            ],
            "MEDIUM_PATH":[
                "reality_check_medium",
                "roadmap_builder_medium",
                "market_context_medium",
            ],
            "EASY_PATH": [
                "reality_check_light",
                "roadmap_builder_light",
                "market_context_light",
            ]
        }
    }

def get_workflow_info():
    structure = get_workflow_structure()
    return {
        "workflow":"EduQuest Career Guidance",
        "structure":structure,
    }


    



