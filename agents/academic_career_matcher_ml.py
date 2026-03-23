"""Academic Career Matcher ML Agent - predicts academic-career fit (0-100 score)."""

import pickle
import os
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')

# CRITICAL: Set scikit-learn thread control to avoid deadlocks in parallel execution
os.environ['SCIKIT_LEARN_ASSUME_FINITE'] = 'True'
os.environ['SKLEARN_THREADING_CONTROL'] = 'true'

SKILL_GAP_CATEGORIES = ["Low", "Medium", "High"]


class AcademicCareerMatcherMLAgent:
    def __init__(self):
        self.model=None
        self.scaler=None
        self.encoder=None

        try:
            project_root=os.path.dirname(os.path.dirname(__file__))
            model_dir=os.path.join(project_root, "ml", "models")
            model_path=os.path.join(model_dir, "academic_matcher_model.pkl")
            
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.model=pickle.load(f)
        
        except Exception:
            self.model=None

    def _simple_rule_score(self, profile: Dict[str, Any])->float:
        '''
        Fallback scoring logic if ML model unavailable
        '''

        score=50.0
        gpa=profile.get("gpa_percentile",0.5)
        research=profile.get("research_experience_months", 0)
        projects=profile.get("project_portfolio_count", 0)

        score+=gpa*30
        score+=min(research/12,1)*10
        score+=min(projects/5,1)*10
        
        return max(0, min(score, 100))

    def predict_fit(self, profile: Dict[str, Any])->Dict[str, Any]:
        try:
            if self.model is not None:
                
                prediction=self.model.predict(profile)
                score=float(prediction)
            else:
                score=self._simple_rule_score(profile)
            
            score=max(0, min(score,100))

            return{
                "academic_fit_score":score,
                "status": "success"
            }
        except Exception:
            return{
                "academic_fit_score": 50.0,
                "status":"fallback"
            }
