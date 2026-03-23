"""Reality Check Full LLM Agent - HARD path deep analysis."""

from typing import Dict, Any
from agents.base_llm_agent import BaseLLMAgent 
from agents.personalization import career_track, learning_mode

class RealityCheckFullLLMAgent(BaseLLMAgent):
    def generate_reality_check(
        self,
        ml_results : Dict[str,Any],
    ) -> Dict[str,Any]:
        viability = ml_results.get("viability_score",0.5)
        academic_fit = ml_results.get("academic_fit_score",0.5)
        career = ml_results.get("career_field", "this career")
        track = career_track(career)
        mode = learning_mode(ml_results.get("constraints_summary", ""))
        prompt = f"""
        Provide a realistic assessment of achieving this career.
        Viability Score: {viability}
        Academic Fit Score: {academic_fit}
        Give :
        -Honest assessment
        -major challenges (4)
        - success probability
        - mindset requirements (3)
        """
        try :
            response = self.generate(prompt,temperature =0.5,max_tokens =1000)
            challenge_map = {
                "data": ["Statistics and tooling depth", "Standing out with portfolio evidence", "Keeping pace with market expectations", "Balancing theory and practical work"],
                "product": ["Building strong product judgment", "Creating credible case studies", "Cross-functional communication", "Competing with experienced PM candidates"],
                "design": ["Portfolio quality bar", "User research depth", "Design critique and iteration speed", "Competition from specialized designers"],
                "marketing": ["Proving measurable campaign impact", "Keeping up with platform changes", "Building analytics fluency", "Crowded applicant pools"],
                "software": ["Strengthening engineering fundamentals", "Building real projects", "Interview preparation consistency", "Competition from experienced candidates"],
            }
            mindset = ["Consistency", "Long-term focus", "Adaptability"]
            if mode == "part_time":
                mindset.append("Disciplined scheduling around existing commitments")
            return {
                "honest_assessment":response[:200],
                "major_challenges": challenge_map[track],
                "success_probability": round(viability*100,1),
                "mindset_requirements": mindset,
                "status":"success",

            }
        except Exception :
            # Intelligent fallback assessment based on ML scores
            viability_pct = round(viability * 100, 1)
            academic_pct = round(academic_fit * 100, 1)
            
            # Determine assessment tone based on scores
            if viability >= 0.7:
                honest = f"Your career path is highly viable. With {viability_pct}% career viability score and {academic_pct}% academic fit, you have a strong foundation. Success depends on consistent effort, continuous learning, and adapting to market demands."
                challenges = [
                    "Rapidly evolving skill requirements in your field",
                    "High competition from other professionals",
                    "Balancing learning while building practical experience",
                    "Financial investment in upskilling and certifications"
                ]
                success = min(85, round(viability_pct + academic_pct / 2))
            elif viability >= 0.5:
                honest = f"Your career path is moderately viable ({viability_pct}% viability, {academic_pct}% fit). You have potential but need focused effort on skill gaps. Success requires intentional learning and project building."
                challenges = [
                    "Filling knowledge gaps through structured learning",
                    "Building practical portfolio and projects",
                    "Managing competition from better-prepared candidates",
                    "Time management between learning and current responsibilities"
                ]
                success = min(70, round(viability_pct + academic_pct / 2))
            else:
                honest = f"Your career path requires significant preparation ({viability_pct}% viability, {academic_pct}% fit). It's achievable but demands dedicated effort, skill building, and strategic planning."
                challenges = [
                    "Substantial skill foundation gaps to fill",
                    "Need for extended learning period",
                    "Highly competitive field with experienced candidates",
                    "Potential career transition costs and risks"
                ]
                success = min(55, round(viability_pct + academic_pct / 2))
            
            return {
                "honest_assessment": honest,
                "major_challenges": challenges,
                "success_probability": success,
                "mindset_requirements": [
                    "Consistent, disciplined effort and learning",
                    "Long-term perspective - growth over 2-3 years",
                    "Adaptability to changing market and technology",
                    "Resilience through setbacks and challenges",
                    "Proactive networking and community engagement"
                ],
                "status": "success",
            }
