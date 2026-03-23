"""Workflow orchestration and utilities for EduQuest.

This module provides helper functions and orchestration utilities.
The actual graph definition is in graph.py
"""

from typing import Dict, Any



def get_workflow_metadata() -> Dict[str, Any]:

    return {
        "workflow_name": "EduQuest Career Guidance System",
        "version": "1.0",
        "description": "AI driven career viability analysis and roadmap generation system",
        "entry_point": "graph.build_graph",
        "graph_builder": "graph.build_graph"
    }

def get_routing_logic() -> Dict[str, Any]:

    return {
        "thresholds": {
            "HARD_PATH": {"max":0.3},
            "MEDIUM_PATH": {"min":0.3, "max":0.6},
            "EASY_PATH": {"min": 0.6}
        },
        "budget_tokens": {
            "HARD_PATH": 5000,
            "MEDIUM_PATH": 3000,
            "EASY_PATH": 1500
        }
    }

def get_parallel_execution_info() -> Dict[str, Any]:

    return {
        "parallel_stages": [
            "career_viabilty_scorer_node",
            "academic_career_matcher_node"
        ],
        "sequential_stages": [
            "input_validator_node",
            "profile_extractor_node",
            "ml_results_merger_node",
            "viability_router_node",
            "output_aggregator_node"
        ]
    }

def get_token_budget_info() -> Dict[str, Any]:

    return {
        "total_tokens_per_path": {
            "HARD_PATH": 5000,
            "MEDIUM_PATH": 3000,
            "EASY_PATH": 1500
        },
        "tokens_per_agent": {
            "profile_extractor": 500,
            "market_context": 700,
            "reality_check": 800,
            "roadmap_builder": 900,
            "financal_planner": 600,
            "alternative_explorer": 500
        }
    }

def get_execution_strategy() -> Dict[str, Any]:

    return {
        "execution_model": "LangGraph StateGraph",
        "state_management": "TypeDict based shared state",
        "error_handling": "Node-level try/except with state error fields.",
        "client_pattern": "LLM client passed to nodes requiring LLM agents",
        "compilation_strategy": "Graph compiled once and reused"
    }
