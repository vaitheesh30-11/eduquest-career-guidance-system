"""Input Validator Node - validates raw user inputs."""

from typing import Dict, Any
from state import EduQuestState
from agents.input_validator_agent import InputValidatorAgent
 


def input_validator_node(state: EduQuestState)->dict:
    """Return only modified fields."""
    try:
        agent=InputValidatorAgent()
        raw_inputs=state.get("raw_inputs", {})
        result=agent.validate_inputs(raw_inputs)
        
        return {
            "validation_errors": result.get("error", []),
            "parsing_complete": result.get("valid", False)
        }

    except Exception as e:
        return {
            "validation_errors": [str(e)],
            "parsing_complete": False
        }
