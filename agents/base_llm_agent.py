"""Base class for all LLM-based agents in EduQuest."""

import re
from utils.gemini_client import GeminiClient
from utils.logging_utils import get_logger, log_event

logger = get_logger(__name__)


def extract_career_from_prompt(prompt: str) -> str:
    """Extract the dream career from the prompt."""
    # Look for patterns like "dream_career: X" or "User career: X" or "for X"
    patterns = [
        # Pattern 1: "dream_career: Data Scientist" or "dream career: Data Scientist"
        r"(?:dream\s*career|dream_career)\s*[:=]\s*([^\n,}]+?)(?:\n|,|$)",
        # Pattern 2: "User dream career: X"
        r"user\s+dream\s+career\s*[:=]\s*([^\n,}]+?)(?:\n|,|$)",
        # Pattern 3: "User career: X" or "target career: X"
        r"(?:user|target|the)\s+(?:dream\s+)?career\s*[:=]\s*([^\n,}]+?)(?:\n|,|$)",
        # Pattern 4: "for pursuing a career in X"
        r"(?:for pursuing|to pursue|pursuing)\s+(?:a\s+)?career\s+in\s+([^\n,}]+?)(?:\n|,|$)",
        # Pattern 5: "Dream Career: X" (case insensitive)
        r"[Dd]ream\s+[Cc]areer\s*[:=]\s*([^\n,}]+?)(?:\n|,|$)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            career = match.group(1).strip()
            # Clean up the extracted career
            career = re.sub(r'\s+', ' ', career)  # Normalize whitespace
            career = career.rstrip(',.:;')  # Remove trailing punctuation
            if career and len(career) > 2 and len(career) < 100:  # Reasonable length
                return career
    
    # Fallback: look for any common career keywords with context
    keywords = [
        r"data scientist", r"software engineer", r"product manager", 
        r"ux designer", r"machine learning engineer", r"ml engineer",
        r"full stack developer", r"backend developer", r"devops engineer",
        r"cloud architect", r"solutions architect", r"developer", 
        r"analyst", r"architect", r"engineer", r"scientist", r"specialist"
    ]
    
    for keyword in keywords:
        if re.search(keyword, prompt, re.IGNORECASE):
            # Extract context around the keyword
            match = re.search(rf"([a-zA-Z\s]*{keyword}(?:\s+[a-z]+)*)", prompt, re.IGNORECASE)
            if match:
                career = match.group(1).strip()
                return career
    
    return "technology career"  # Default fallback


def _infer_track_from_career(career: str) -> str:
    text = (career or "").lower()
    if any(token in text for token in ["data", "ai", "ml", "analytics"]):
        return "data"
    if any(token in text for token in ["product", "manager", "strategy", "business analyst"]):
        return "product"
    if any(token in text for token in ["design", "ux", "ui", "graphic"]):
        return "design"
    if any(token in text for token in ["marketing", "sales", "seo", "growth"]):
        return "marketing"
    if any(token in text for token in ["teacher", "teaching", "educator", "professor", "lecturer", "tutor", "faculty", "school"]):
        return "education"
    if any(token in text for token in ["software", "developer", "engineer", "cloud", "devops"]):
        return "software"
    return "general"


class BaseLLMAgent:
    def __init__(self, client : GeminiClient):
        # Allow client to be None - will return mock responses
        self.client = client
        self.is_available = client is not None and hasattr(client, 'is_initialized') and client.is_initialized

    def _trace_metadata(self, operation: str, **extra: object) -> dict:
        return {
            "agent_name": self.__class__.__name__,
            "operation": operation,
            "client_model": getattr(self.client, "model", None),
            **extra,
        }

    def _with_response_source(self, payload: dict, source: str) -> dict:
        enriched = dict(payload)
        enriched["response_source"] = source
        return enriched

    def generate(
        self,
        prompt : str,
        temperature : float = 0.6,
        max_tokens : int = 1000,
    ) -> str:
        """Wrapper method for calling Gemini LLM.
        Returns mock response if client is not available.
        """
        
        # Return mock response if no client available
        if not self.is_available:
            log_event(
                logger,
                30,
                "llm_client_unavailable",
                agent_name=self.__class__.__name__,
                initialized=getattr(self.client, "is_initialized", False),
                last_error=getattr(self.client, "last_error", None),
            )
            return self._get_mock_response(prompt)

    def generate_direct(
        self,
        prompt: str,
        temperature: float = 0.6,
        max_tokens: int = 1000,
    ) -> str:
        """
        Call Gemini directly without mock fallback.
        Raises if client is unavailable or call fails.
        """
        if not self.is_available:
            raise ValueError(
                f"Gemini client unavailable (initialized={getattr(self.client, 'is_initialized', False)}, "
                f"last_error={getattr(self.client, 'last_error', None)})"
            )
        if hasattr(self.client, "generate_content"):
            return str(
                self.client.generate_content(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    trace_name=f"{self.__class__.__name__}.generate_direct",
                    trace_tags=["llm-agent", self.__class__.__name__],
                    trace_metadata=self._trace_metadata(
                        "generate_direct",
                        response_format="text",
                    ),
                )
            )
        if hasattr(self.client, "generate"):
            return str(
                self.client.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
        raise AttributeError("Gemini client does not support generate/generate_content")

        try :
            if hasattr(self.client, "generate_content"):
                response = self.client.generate_content(
                    prompt = prompt,
                    temperature = temperature,
                    max_tokens = max_tokens,
                )
            elif hasattr(self.client, "generate"):
                response = self.client.generate(
                    prompt = prompt,
                    temperature = temperature,
                    max_tokens = max_tokens,
                )
            else:
                raise AttributeError("Gemini client does not support generate/generate_content")

            return str(response)

        except Exception as e:
            # Fall back to mock response if generation fails
            log_event(logger, 30, "llm_generation_failed", agent_name=self.__class__.__name__, error=str(e))
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate intelligent fallback response when API is unavailable."""
        # Extract the career from the prompt
        career = extract_career_from_prompt(prompt)
        track = _infer_track_from_career(career)
        
        # Return context-aware fallback responses based on the prompt and career
        prompt_lower = prompt.lower()
        
        if "market" in prompt_lower or "industry insights" in prompt_lower:
            demand = {
                "data": "high demand in analytics, fintech, SaaS, and AI teams",
                "product": "strong demand in startups and digital product organizations",
                "design": "steady demand in product design and user research teams",
                "marketing": "strong demand for digital growth and performance roles",
                "education": "steady demand in K-12, coaching, and EdTech institutions",
                "software": "very high demand across product, platform, and cloud teams",
                "general": "stable demand with role-specific variation by sector",
            }[track]
            return f"The {career} market shows {demand}. Salary progression is competitive, and hiring remains active in Bengaluru, Hyderabad, Pune, Mumbai, and remote-first teams. Growth outlook is positive over the next 3-5 years for candidates with portfolio-backed skills."
        
        elif "financial" in prompt_lower or "cost" in prompt_lower:
            investment = {
                "data": "2-6 Lakhs",
                "product": "2-7 Lakhs",
                "design": "1.5-5 Lakhs",
                "marketing": "1-4 Lakhs",
                "education": "1-3 Lakhs",
                "software": "2-8 Lakhs",
                "general": "2-6 Lakhs",
            }[track]
            return f"Financial Plan for {career}: Typical investment is {investment} for focused upskilling, projects, and interview readiness. Funding can come from savings, scholarships, loans, or employer support. ROI is usually visible within 12-24 months with consistent execution."
        
        elif "roadmap" in prompt_lower or "phase" in prompt_lower:
            focus = {
                "data": "statistics, SQL/Python, and analysis projects",
                "product": "product thinking, case studies, and stakeholder communication",
                "design": "UX foundations, portfolio projects, and design critiques",
                "marketing": "channel strategy, analytics, and campaign experiments",
                "education": "subject depth, pedagogy, classroom practice, and student outcomes",
                "software": "core programming, projects, and system fundamentals",
                "general": "domain fundamentals, hands-on projects, and job readiness",
            }[track]
            return f"Career Roadmap for {career}: Phase 1 (1-3 months) build foundations. Phase 2 (3-6 months) focus on {focus}. Phase 3 (2-4 months) finalize interview prep and targeted applications. Typical timeline is 6-13 months based on current baseline."
        
        elif "reality" in prompt_lower or "challenge" in prompt_lower or "honest" in prompt_lower:
            challenge = {
                "data": "demonstrating strong project depth beyond basic models",
                "product": "presenting high-quality product case studies",
                "design": "building a portfolio that demonstrates real user impact",
                "marketing": "showing measurable campaign outcomes",
                "education": "demonstrating effective teaching practice and classroom outcomes",
                "software": "proving strong coding and problem-solving consistency",
                "general": "translating learning into role-relevant evidence",
            }[track]
            return f"Reality Assessment for {career}: This path is achievable but competitive. The biggest challenge is {challenge}. Success depends on consistent skill-building, practical proof of work, and focused applications. With steady execution, outcomes can be strong."
        
        elif "alternative" in prompt_lower or "similar" in prompt_lower:
            return f"Alternative paths related to {career}: consider adjacent roles that reuse your core strengths while improving short-term employability. Prioritize options with high skill overlap, visible portfolio potential, and clear transition steps."
        
        else:
            return f"Career Analysis for {career}: Your progression should combine structured learning, practical execution, and targeted networking. Build role-specific proof of work and iterate based on feedback from mentors and hiring expectations."

    def generate_structured_json(
        self,
        prompt: str,
        required_fields: list,
        temperature: float = 0.6,
        max_tokens: int = 1200,
    ) -> dict:
        """
        Generate structured JSON directly from the LLM.
        This method does not use mock responses, so callers can clearly detect
        true API failures and decide fallback behavior explicitly.
        """
        if not self.is_available:
            raise ValueError(
                f"Gemini client unavailable (initialized={getattr(self.client, 'is_initialized', False)}, "
                f"last_error={getattr(self.client, 'last_error', None)})"
            )
        if not hasattr(self.client, "generate_structured_json"):
            raise AttributeError("Gemini client does not support structured JSON generation")
        return self.client.generate_structured_json(
            prompt=prompt,
            required_fields=required_fields,
            temperature=temperature,
            max_tokens=max_tokens,
            trace_name=f"{self.__class__.__name__}.generate_structured_json",
            trace_tags=["llm-agent", self.__class__.__name__],
            trace_metadata=self._trace_metadata(
                "generate_structured_json",
                response_format="json",
                required_fields=",".join(required_fields),
            ),
        )
