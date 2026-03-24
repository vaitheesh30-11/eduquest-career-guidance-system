"""Academic Career Matcher ML Agent - predicts academic-career fit (0-100 score)."""

import pickle
import os
from typing import Dict, Any, List
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

# CRITICAL: Set scikit-learn thread control to avoid deadlocks in parallel execution
os.environ['SCIKIT_LEARN_ASSUME_FINITE'] = 'True'
os.environ['SKLEARN_THREADING_CONTROL'] = 'true'

SKILL_GAP_CATEGORIES = ["Low", "Medium", "High"]


class AcademicCareerMatcherMLAgent:
    _shared_model = None
    _shared_ready = False

    def __init__(self):
        self.model=None
        self.scaler=None
        self.encoder=None

        project_root=os.path.dirname(os.path.dirname(__file__))
        model_dir=os.path.join(project_root, "ml", "models")
        model_path=os.path.join(model_dir, "academic_matcher_model.pkl")
        training_path = os.path.join(project_root, "data", "training_dataset", "academic_matcher_training.csv")

        if AcademicCareerMatcherMLAgent._shared_ready:
            self.model = AcademicCareerMatcherMLAgent._shared_model
            return

        try:
            if os.path.exists(model_path) and os.path.getsize(model_path) > 100:
                with open(model_path, "rb") as f:
                    self.model=pickle.load(f)
            elif os.path.exists(training_path):
                self.model = self._train_model(training_path)
                os.makedirs(model_dir, exist_ok=True)
                with open(model_path, "wb") as f:
                    pickle.dump(self.model, f)
        
        except Exception:
            self.model=None

        AcademicCareerMatcherMLAgent._shared_model = self.model
        AcademicCareerMatcherMLAgent._shared_ready = True

    def _train_model(self, training_path: str):
        df = pd.read_csv(training_path)
        required_cols = [
            "current_degree_field",
            "gpa_percentile",
            "research_experience_months",
            "project_portfolio_count",
            "academic_fit_score",
        ]
        df = df[required_cols].copy()
        y = df["academic_fit_score"].astype(float)
        X = df.drop(columns=["academic_fit_score"])

        cat_cols = ["current_degree_field"]
        num_cols = ["gpa_percentile", "research_experience_months", "project_portfolio_count"]

        preprocessor = ColumnTransformer(
            transformers=[
                ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
                ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), num_cols),
            ]
        )
        model = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("regressor", LinearRegression()),
            ]
        )
        model.fit(X, y)
        return model

    def _build_feature_frame(self, profile: Dict[str, Any]) -> pd.DataFrame:
        gpa = profile.get("gpa_percentile", 0.5)
        research = profile.get("research_experience_months", 0)
        projects = profile.get("project_portfolio_count", 0)
        return pd.DataFrame(
            [
                {
                    "current_degree_field": profile.get("current_degree_field", profile.get("career_field", "Unknown")),
                    "gpa_percentile": 0.5 if gpa is None else gpa,
                    "research_experience_months": 0 if research is None else research,
                    "project_portfolio_count": 0 if projects is None else projects,
                }
            ]
        )

    def _career_adjustment(self, career: str) -> float:
        text = (career or "").lower()
        if any(token in text for token in ["doctor", "surgeon", "lawyer", "judge"]):
            return -4.0
        if any(token in text for token in ["teacher", "designer", "developer", "analyst", "marketing", "data scientist", "software"]):
            return 2.0
        return 0.0

    def _education_adjustment(self, level: str) -> float:
        text = (level or "").lower()
        if "phd" in text:
            return 8.0
        if "master" in text:
            return 5.0
        if "bachelor" in text:
            return 2.0
        if "high school" in text:
            return -5.0
        return 0.0

    def _simple_rule_score(self, profile: Dict[str, Any])->float:
        '''
        Fallback scoring logic if ML model unavailable
        '''

        score=42.0
        gpa=profile.get("gpa_percentile",0.5)
        research=profile.get("research_experience_months", 0)
        projects=profile.get("project_portfolio_count", 0)
        experience=profile.get("years_of_experience", 0)
        gpa = 0.5 if gpa is None else gpa
        research = 0 if research is None else research
        projects = 0 if projects is None else projects
        experience = 0 if experience is None else experience
        concerns=len(profile.get("concerns_list", []) or [])
        interests=len(profile.get("interests_list", []) or [])
        career = profile.get("career_field", "")
        edu = profile.get("current_education_level", "")

        score+=gpa*30
        score+=min(research/12,1)*8
        score+=min(projects/6,1)*8
        score+=min(experience/8,1)*6
        score+=min(interests/5,1)*5
        score-=min(concerns/6,1)*4
        score+=self._career_adjustment(career)
        score+=self._education_adjustment(edu)
        
        return max(0, min(score, 100))

    def predict_fit(self, profile: Dict[str, Any])->Dict[str, Any]:
        try:
            if self.model is not None:
                features_df = self._build_feature_frame(profile)
                prediction = self.model.predict(features_df)[0]
                score=float(prediction) + self._career_adjustment(profile.get("career_field", "")) + (0.5 * self._education_adjustment(profile.get("current_education_level", "")))
            else:
                score=self._simple_rule_score(profile)
            
            score=max(0, min(score,100))

            return{
                "academic_fit_score":score,
                "status": "success",
                "response_source":"ml_model" if self.model is not None else "fallback",
            }
        except Exception:
            return{
                "academic_fit_score": 50.0,
                "status":"fallback",
                "response_source":"fallback",
            }
