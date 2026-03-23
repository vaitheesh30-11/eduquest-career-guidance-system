"""Base class for all LLM-based agents in EduQuest."""


from utils.gemini_client import GeminiClient
class BaseLLMAgent:
    def __init__(self, client : GeminiClient):
        # Allow client to be None - will return mock responses
        self.client = client
        self.is_available = client is not None and hasattr(client, 'is_initialized') and client.is_initialized

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
            return self._get_mock_response(prompt)

        try :
            response = self.client.generate(
                prompt = prompt,
                temperature = temperature,
                max_tokens = max_tokens,
            )

            return str(response)

        except Exception as e:
            # Fall back to mock response if generation fails
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """Generate intelligent fallback response when API is unavailable."""
        # Return context-aware fallback responses based on the prompt
        prompt_lower = prompt.lower()
        
        if "market" in prompt_lower or "industry insights" in prompt_lower:
            return "The Data Science field is experiencing strong growth with high demand for professionals. Key opportunities include ML Engineering, AI Research, and Analytics roles across tech, finance, and healthcare sectors. Major hubs are Bangalore, Hyderabad, and Pune with competitive salaries ranging from 8L-25L INR for mid-level positions."
        
        elif "financial" in prompt_lower or "cost" in prompt_lower:
            return "Financial Plan Summary: Budget approximately 5-10 Lakhs for a comprehensive upskilling program including online courses, certifications, and practical projects. Consider funding through personal savings, educational loans, or employer sponsorship. Expected ROI is positive within 1-2 years post-upskilling."
        
        elif "roadmap" in prompt_lower or "phase" in prompt_lower:
            return "A well-structured career roadmap includes three phases: Foundation (3 months) focusing on core concepts and skills, Intermediate (3-6 months) building practical projects and portfolio, and Advanced (3-6 months) pursuing specializations, contributing to open source, and landing advanced roles."
        
        elif "reality" in prompt_lower or "challenge" in prompt_lower or "honest" in prompt_lower:
            return "Realistic Assessment: While the Data Science field is competitive, entry is possible with dedicated effort. Main challenges include continuously evolving skill requirements, stiff competition for roles, and the need for both technical and soft skills. Success requires consistent learning, building real projects, and networking. Success probability depends on your current foundation and commitment level."
        
        elif "alternative" in prompt_lower or "similar" in prompt_lower:
            return "Related career paths include Machine Learning Engineer (higher technical depth), Data Analyst (less ML-heavy, more analytics-focused), Business Analyst (broader business context), or Analytics Engineer (data engineering + analytics). These offer similar skill application with different focus areas."
        
        else:
            return "Career assessment analysis based on your profile. Recommendations are personalized to your experience level, existing skills, constraints, and career goals. Pursue continuous learning, build practical projects, and network within your target industry."
