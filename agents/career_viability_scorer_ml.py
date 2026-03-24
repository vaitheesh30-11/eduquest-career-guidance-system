"""Career Viability Scorer ML Agent - predicts career viability (0-1 score)."""

import pickle 
import os
from typing import Dict, Any
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


class CareerViabilityScorerMLAgent:
    _shared_model = None
    _shared_ready = False

    def __init__(self):
        self.model=None

        project_root=os.path.dirname(os.path.dirname(__file__))
        model_dir=os.path.join(project_root, "ml", "models")
        model_path=os.path.join(model_dir, "career_viability_model.pkl")
        training_path = os.path.join(project_root, "data", "training_dataset", "career_viability_training.csv")

        if CareerViabilityScorerMLAgent._shared_ready:
            self.model = CareerViabilityScorerMLAgent._shared_model
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

        CareerViabilityScorerMLAgent._shared_model = self.model
        CareerViabilityScorerMLAgent._shared_ready = True

    def _train_model(self, training_path: str):
        df = pd.read_csv(training_path)
        required_cols = [
            "career_field",
            "current_education_level",
            "budget_constraint",
            "timeline_urgency",
            "years_of_experience",
            "gpa_percentile",
            "research_experience_months",
            "project_portfolio_count",
            "viability_score",
        ]
        df = df[required_cols].copy()
        y = df["viability_score"].astype(float)
        X = df.drop(columns=["viability_score"])

        cat_cols = ["career_field", "current_education_level", "budget_constraint", "timeline_urgency"]
        num_cols = ["years_of_experience", "gpa_percentile", "research_experience_months", "project_portfolio_count"]

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
        years = profile.get("years_of_experience", 0)
        gpa = profile.get("gpa_percentile", 0.5)
        research = profile.get("research_experience_months", 0)
        projects = profile.get("project_portfolio_count", 0)
        return pd.DataFrame(
            [
                {
                    "career_field": profile.get("career_field", "Unknown"),
                    "current_education_level": profile.get("current_education_level", "Unknown"),
                    "budget_constraint": profile.get("budget_constraints", "Moderate"),
                    "timeline_urgency": profile.get("timeline_urgency", "Medium"),
                    "years_of_experience": 0 if years is None else years,
                    "gpa_percentile": 0.5 if gpa is None else gpa,
                    "research_experience_months": 0 if research is None else research,
                    "project_portfolio_count": 0 if projects is None else projects,
                }
            ]
        )

    def _career_modifier(self, career: str) -> float:
        text = (career or "").lower()
        if any(token in text for token in ["doctor", "surgeon", "pilot", "judge", "lawyer", "civil service", "ias"]):
            return -0.06
        if any(token in text for token in ["data", "software", "designer", "teacher", "marketing", "analyst"]):
            return 0.03
        return 0.0

    def _fallback_score(self, profile: Dict[str, Any])->float:
        '''
        Simple rule-based viability estimation if model unavailable
        '''
        score=0.35

        gpa=profile.get("gpa_percentile", 0.5)
        experience=profile.get("years_of_experience", 0)
        research=profile.get("research_experience_months", 0)
        projects=profile.get("project_portfolio_count",0)
        gpa = 0.5 if gpa is None else gpa
        experience = 0 if experience is None else experience
        research = 0 if research is None else research
        projects = 0 if projects is None else projects
        interests=len(profile.get("interests_list", []) or [])
        concerns=len(profile.get("concerns_list", []) or [])
        timeline = (profile.get("timeline_urgency", "") or "").lower()
        budget = (profile.get("budget_constraints", "") or "").lower()
        career = profile.get("career_field", "")

        score+=gpa*0.25
        score+=min(experience/6,1)*0.15
        score+=min(research/12,1)*0.05
        score+=min(projects/6,1)*0.10
        score+=min(interests/5,1)*0.06
        score-=min(concerns/6,1)*0.05
        score+=self._career_modifier(career)
        if timeline == "high":
            score -= 0.04
        elif timeline == "low":
            score += 0.03
        if budget == "limited":
            score -= 0.03
        elif budget == "adequate":
            score += 0.03

        return max(0.0, min(score,1.0))

    def predict_viability(self, profile: Dict[str, Any])->Dict[str, Any]:
        try:

            if self.model is not None:
                features_df = self._build_feature_frame(profile)
                prediction=self.model.predict(features_df)[0]
                score = float(prediction) + self._career_modifier(profile.get("career_field", ""))
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
