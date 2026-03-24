"""
Main graph interface for EduQuest career guidance system.
Defines the complete StateGraph structure and orchestration.
"""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
import time
from typing import Dict, Any
from uuid import uuid4

from langgraph.graph import StateGraph, START, END
from state import EduQuestState, get_initial_state
from utils.cache_utils import TTLCache
from utils.gemini_client import GeminiClient
from utils.logging_utils import get_logger, log_event
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
try:
    from ml.observability import trace_block, tracing_session
except ModuleNotFoundError:
    from observability import trace_block, tracing_session

# Routing threshold constants
HARD_PATH_THRESHOLD = 0.6
MEDIUM_PATH_THRESHOLD = 0.3
logger = get_logger(__name__)
_assessment_cache = TTLCache(
    ttl_seconds=max(0, int(os.getenv("EDUQUEST_ASSESSMENT_CACHE_TTL_SECONDS", "600"))),
    max_entries=max(1, int(os.getenv("EDUQUEST_ASSESSMENT_CACHE_MAX_ENTRIES", "64"))),
)


def _assessment_cache_enabled() -> bool:
    return _assessment_cache.ttl_seconds > 0 and _assessment_cache.max_entries > 0


def _build_assessment_cache_key(form_data: Dict[str, Any]) -> str:
    stable_payload = {
        "dream_career": form_data.get("dream_career", ""),
        "current_academics": form_data.get("current_academics", ""),
        "constraints": form_data.get("constraints", ""),
        "interests": form_data.get("interests", ""),
        "other_concerns": form_data.get("other_concerns", ""),
    }
    serialized = json.dumps(stable_payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _prepare_cached_assessment_result(
    cached_result: Dict[str, Any],
    *,
    request_id: str,
    analysis_timestamp: str,
    workflow_duration_seconds: float,
) -> Dict[str, Any]:
    result = deepcopy(cached_result)
    result["request_id"] = request_id
    result["analysis_timestamp"] = analysis_timestamp
    result["processing_complete"] = True
    result["error_occurred"] = False

    workflow_observability = dict(result.get("workflow_observability", {}))
    workflow_observability.update(
        {
            "request_id": request_id,
            "workflow_name": "eduquest_assessment",
            "started_at": analysis_timestamp,
            "total_duration_seconds": workflow_duration_seconds,
            "processing_complete": True,
            "served_from_assessment_cache": True,
        }
    )
    result["workflow_observability"] = workflow_observability

    performance_summary = dict(result.get("performance_summary", {}))
    performance_summary.update(
        {
            "request_id": request_id,
            "workflow_duration_seconds": workflow_duration_seconds,
            "served_from_assessment_cache": True,
            "assessment_cache_lookup_seconds": workflow_duration_seconds,
            "assessment_cache_stats": _assessment_cache.stats(),
        }
    )
    result["performance_summary"] = performance_summary

    ml_observability = dict(result.get("ml_observability", {}))
    ml_observability["request_id"] = request_id
    result["ml_observability"] = ml_observability

    llm_observability = dict(result.get("llm_observability", {}))
    llm_observability["request_id"] = request_id
    llm_observability["served_from_assessment_cache"] = True
    result["llm_observability"] = llm_observability

    return result
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
    graph.add_node("alternatives_medium",lambda s:alternative_explorer_node(s,client))
    graph.add_node("alternatives_light",lambda s:alternative_explorer_node(s,client))
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
    graph.add_edge("roadmap_medium","alternatives_medium")
    graph.add_edge("alternatives_medium","market_medium")
    graph.add_edge("market_medium","aggregator")

    graph.add_edge("reality_light","roadmap_light")
    graph.add_edge("roadmap_light","alternatives_light")
    graph.add_edge("alternatives_light","market_light")
    graph.add_edge("market_light","aggregator")

    graph.add_edge("aggregator",END)
    return graph.compile()

def assess_career(form_data: Dict[str,str])-> Dict[str,Any]:
    try :
        workflow_started_at = time.perf_counter()
        form_data["request_id"]= str(uuid4())
        form_data["analysis_timestamp"] = datetime.now(timezone.utc).isoformat()
        request_id = form_data["request_id"]
        assessment_cache_key = _build_assessment_cache_key(form_data)

        trace_inputs = {
            "request_id": request_id,
            "dream_career": form_data.get("dream_career", ""),
            "has_current_academics": bool(form_data.get("current_academics")),
            "has_constraints": bool(form_data.get("constraints")),
            "has_interests": bool(form_data.get("interests")),
            "has_other_concerns": bool(form_data.get("other_concerns")),
        }

        with tracing_session(
            tags=["workflow", "career-guidance", "llm"],
            metadata={"request_id": request_id, "workflow_name": "eduquest_assessment"},
        ):
            with trace_block(
                "assess_career",
                run_type="chain",
                inputs=trace_inputs,
                tags=["workflow", "career-guidance"],
                metadata={"request_id": request_id, "workflow_name": "eduquest_assessment"},
            ) as run:
                if _assessment_cache_enabled():
                    cached_result = _assessment_cache.get(assessment_cache_key)
                    if cached_result is not None:
                        total_duration_seconds = round(time.perf_counter() - workflow_started_at, 4)
                        final_state = _prepare_cached_assessment_result(
                            cached_result,
                            request_id=request_id,
                            analysis_timestamp=form_data["analysis_timestamp"],
                            workflow_duration_seconds=total_duration_seconds,
                        )
                        log_event(
                            logger,
                            20,
                            "assessment_cache_hit",
                            request_id=request_id,
                            dream_career=form_data.get("dream_career", ""),
                            total_duration_seconds=total_duration_seconds,
                            workflow_observability=final_state.get("workflow_observability"),
                            performance_summary=final_state.get("performance_summary"),
                        )
                        if run is not None:
                            run.end(
                                outputs={
                                    "path_taken": final_state.get("path_taken"),
                                    "processing_complete": final_state.get("processing_complete"),
                                    "workflow_observability": final_state.get("workflow_observability"),
                                    "performance_summary": final_state.get("performance_summary"),
                                    "ml_observability": final_state.get("ml_observability"),
                                    "llm_observability": final_state.get("llm_observability"),
                                }
                            )
                        return final_state

                state = get_initial_state(form_data)
                client = GeminiClient()
                client.reset_session_metrics(
                    request_id=request_id,
                    workflow_name="eduquest_assessment",
                )
                log_event(logger, 20, "assessment_started", request_id=request_id, dream_career=form_data.get("dream_career", ""), gemini_status=client.debug_status())

                graph = build_eduquest_graph(client)
                final_state = graph.invoke(state)
                total_duration_seconds = round(time.perf_counter() - workflow_started_at, 4)
                final_state["processing_complete"] = True
                final_state['error_occured'] = False
                final_state["workflow_observability"] = {
                    "request_id": request_id,
                    "workflow_name": "eduquest_assessment",
                    "started_at": form_data["analysis_timestamp"],
                    "total_duration_seconds": total_duration_seconds,
                    "path_taken": final_state.get("path_taken"),
                    "processing_complete": True,
                }
                final_state["ml_observability"] = {
                    "request_id": request_id,
                    "predictions": [
                        final_state.get("viability_ml_observability", {}),
                        final_state.get("academic_ml_observability", {}),
                    ],
                    "successful_predictions": sum(
                        1
                        for item in [
                            final_state.get("viability_ml_observability", {}),
                            final_state.get("academic_ml_observability", {}),
                        ]
                        if item.get("status") in {"success", "fallback"}
                    ),
                    "failed_predictions": sum(
                        1
                        for item in [
                            final_state.get("viability_ml_observability", {}),
                            final_state.get("academic_ml_observability", {}),
                        ]
                        if item.get("status") == "error"
                    ),
                    "total_latency_seconds": round(
                        sum(
                            float(item.get("latency_seconds", 0.0))
                            for item in [
                                final_state.get("viability_ml_observability", {}),
                                final_state.get("academic_ml_observability", {}),
                            ]
                        ),
                        4,
                    ),
                }
                final_state["llm_observability"] = client.get_session_metrics()
                final_state["performance_summary"] = {
                    "request_id": request_id,
                    "workflow_duration_seconds": total_duration_seconds,
                    "ml_duration_seconds": final_state["ml_observability"]["total_latency_seconds"],
                    "llm_duration_seconds": final_state["llm_observability"]["total_latency_seconds"],
                    "llm_cache_hits": final_state["llm_observability"].get("cache_hits", 0),
                    "llm_cache_hit_rate": final_state["llm_observability"].get("cache_hit_rate", 0.0),
                    "structured_cache_hits": final_state["llm_observability"].get("structured_cache_hits", 0),
                    "structured_cache_hit_rate": final_state["llm_observability"].get("structured_cache_hit_rate", 0.0),
                    "llm_success_rate": final_state["llm_observability"].get("success_rate", 0.0),
                    "served_from_assessment_cache": False,
                    "assessment_cache_stats": _assessment_cache.stats(),
                }
                if _assessment_cache_enabled():
                    _assessment_cache.set(assessment_cache_key, deepcopy(final_state))
                    log_event(logger, 20, "assessment_cache_store", request_id=request_id, dream_career=form_data.get("dream_career", ""))
                log_event(
                    logger,
                    20,
                    "assessment_completed",
                    request_id=request_id,
                    path_taken=final_state.get("path_taken"),
                    total_duration_seconds=total_duration_seconds,
                    viability_score=final_state.get("viability_score"),
                    academic_fit_score=final_state.get("academic_fit_score"),
                    workflow_observability=final_state.get("workflow_observability"),
                    performance_summary=final_state.get("performance_summary"),
                    ml_observability=final_state.get("ml_observability"),
                    llm_observability=final_state.get("llm_observability"),
                )

                if run is not None:
                    run.end(
                        outputs={
                            "path_taken": final_state.get("path_taken"),
                            "processing_complete": final_state.get("processing_complete"),
                            "workflow_observability": final_state.get("workflow_observability"),
                            "performance_summary": final_state.get("performance_summary"),
                            "ml_observability": final_state.get("ml_observability"),
                            "llm_observability": final_state.get("llm_observability"),
                        }
                    )
                return final_state
    except Exception as e :
        total_duration_seconds = round(time.perf_counter() - workflow_started_at, 4)
        log_event(logger, 40, "assessment_failed", error=str(e), total_duration_seconds=total_duration_seconds)
        import traceback
        traceback.print_exc()
        return {
            "processing_complete":True,
            "error_occurred":True,
            "error_message":str(e),
            "workflow_observability": {
                "workflow_name": "eduquest_assessment",
                "total_duration_seconds": total_duration_seconds,
            },
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


    
