"""Career Viability Scorer ML Agent - predicts career viability (0-1 score)."""

import pickle 
import os
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# CRITICAL: Set scikit-learn thread control to avoid deadlocks in parallel execution
os.environ['SCIKIT_LEARN_ASSUME_FINITE'] = 'True'
os.environ['SKLEARN_THREADING_CONTROL'] = 'true'


class CareerViabilityScorerMLAgent:
    def __init__(self):
        self.model=None

        try:
            project_root=os.path.dirname(os.path.dirname(__file__))
            model_dir=os.path.join(project_root, "ml", "models")
            model_path=os.path.join(model_dir, "career_viability_model.pkl")

            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.model=pickle.load(f)

        except Exception:
            self.model=None

    def _fallback_score(self, profile: Dict[str, Any])->float:
        '''
        Simple rule-based viability estimation if model unavailable
        '''
        score=0.5

        gpa=profile.get("gpa_percentile", 0.5)
        experience=profile.get("years_of_experience", 0)
        research=profile.get("research_experience_months", 0)
        projects=profile.get("project_portfolio_count",0)

        score+=gpa*0.3
        score+=min(experience/5,1)*0.1
        score+=min(research/12,1)*0.05
        score+=min(projects/5,1)*0.05

        return max(0.0, min(score,1.0))

    def predict_viability(self, profile: Dict[str, Any])->Dict[str, Any]:
        try:

            if self.model is not None:

                features=[
                    profile.get("gpa_percentile", 0),
                    profile.get("years_of_experience", 0),
                    profile.get("research_experience_months", 0),
                    profile.get("project_portfolio_count",0),
                ]

                prediction=self.model.predict([features])[0]
                score = float(prediction)
            else:
                score=self._fallback_score(profile)

            score=max(0.0, min(score, 1.0))

            return{
                "viability_score":score,
                "status":"success"
            }

        except Exception :
            return{
                "viability_score":0.5,
                "status":"fallback",
            }
