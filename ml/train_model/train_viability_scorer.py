"""Train career viability scorer ML model."""

from __future__ import annotations

import pickle

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

try:
    from ml.observability import trace_block
except ModuleNotFoundError:  # Supports running `python ml/train_pipeline.py`
    from observability import trace_block


def train_viability_model(training_file, output_dir):
    trace_inputs = {
        "training_file": training_file,
        "output_dir": output_dir,
    }
    trace_metadata = {
        "model_family": "career_viability",
        "estimator": "RandomForestRegressor",
    }
    with trace_block(
        "train_viability_model",
        run_type="tool",
        inputs=trace_inputs,
        tags=["ml", "training", "viability"],
        metadata=trace_metadata,
    ) as run:
        try:
            df = pd.read_csv(training_file)

            y = df["viability_score"]
            X = df.drop(columns=["viability_score"])
            categorical_cols = [
                "career_field",
                "current_education_level",
                "budget_constraint",
                "timeline_urgency",
            ]
            numeric_cols = [
                "years_of_experience",
                "gpa_percentile",
                "research_experience_months",
                "project_portfolio_count",
            ]

            preprocessor = ColumnTransformer(
                transformers=[
                    (
                        "cat",
                        Pipeline(
                            steps=[
                                ("imputer", SimpleImputer(strategy="most_frequent")),
                                ("onehot", OneHotEncoder(handle_unknown="ignore")),
                            ]
                        ),
                        categorical_cols,
                    ),
                    (
                        "num",
                        Pipeline(
                            steps=[("imputer", SimpleImputer(strategy="median"))]
                        ),
                        numeric_cols,
                    ),
                ]
            )
            model = Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    (
                        "regressor",
                        RandomForestRegressor(
                            n_estimators=200,
                            min_samples_leaf=1,
                            max_features="sqrt",
                            random_state=42,
                        ),
                    ),
                ]
            )
            x_train, x_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            model.fit(x_train, y_train)

            train_r2 = r2_score(y_train, model.predict(x_train))
            test_r2 = r2_score(y_test, model.predict(x_test))

            pickle.dump(model, open(f"{output_dir}/career_viability_model.pkl", "wb"))
            pickle.dump(model, open(f"{output_dir}/viability_model.pkl", "wb"))

            result = {
                "status": "success",
                "train_r2": float(train_r2) if pd.notna(train_r2) else 0.0,
                "test_r2": float(test_r2) if pd.notna(test_r2) else 0.0,
                "model_type": "Pipeline(RandomForestRegressor)",
                "feature_count": X.shape[1],
                "row_count": int(len(df)),
            }
            if run is not None:
                run.end(outputs=result)
            return result
        except Exception as exc:
            if run is not None:
                run.end(error=str(exc))
            raise
