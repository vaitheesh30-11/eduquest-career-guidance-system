"""Input Validator Agent - validates raw user inputs."""

from typing import Dict, Any, List 

MIN_LENGTH = 50
MAX_LENGTH = 2000



class InputValidatorAgent:
    def validate_inputs(self, raw_inputs: Dict[str, str])->Dict[str, Any]:
        errors: List[str]=[]

        for field, value in raw_inputs.items():
            if value is None or str(value).strip()=="":
                error.append(f"{field} cannot be empty")
                continue

            if len(value)<MIN_LENGTH:
                errors.append(f"{field} must be at least {MIN_LENGTH} characters")
            if len(value)>MAX_LENGTH:
                errors.append(f"{field} exceeds max length {MAX_LENGTH}")

        return{
            "validation_errors":errors,
            "is_valid":len(errors)==0,
            "status":"success",
        }
