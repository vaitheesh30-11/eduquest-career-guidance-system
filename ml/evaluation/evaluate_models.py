"""Evaluate trained ML models on evaluation datasets."""

from __future__ import annotations

import os
import pickle
from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, KFold, cross_validate
from sklearn.base import clone


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def _model_path(model_dir: str, primary: str, fallback: str | None = None) -> str:
    primary_path = os.path.join(model_dir, primary)
    if os.path.exists(primary_path):
        return primary_path
    if fallback:
        fallback_path = os.path.join(model_dir, fallback)
        if os.path.exists(fallback_path):
            return fallback_path
    raise FileNotFoundError(f"Model file not found: {primary} (fallback: {fallback})")


def _metrics(y_true: np.ndarray, y_pred: np.ndarray, target_range: float) -> Dict[str, Any]:
    abs_err = np.abs(y_true - y_pred)
    mae = _safe_float(mean_absolute_error(y_true, y_pred))
    rmse = _safe_float(np.sqrt(mean_squared_error(y_true, y_pred)))
    baseline_pred = np.full_like(y_true, np.mean(y_true), dtype=float)
    baseline_mae = _safe_float(mean_absolute_error(y_true, baseline_pred))
    skill_over_baseline = 0.0
    if baseline_mae > 0:
        # Do not clip: negative values are useful diagnostics.
        skill_over_baseline = 1.0 - (mae / baseline_mae)
    consistency_warning = bool(_safe_float(r2_score(y_true, y_pred)) > 0.5 and skill_over_baseline < 0.05)
    return {
        "samples": int(len(y_true)),
        "r2": _safe_float(r2_score(y_true, y_pred)),
        "mae": mae,
        "rmse": rmse,
        "nmae": _safe_float(mae / target_range),
        "nrmse": _safe_float(rmse / target_range),
        "baseline_mae": baseline_mae,
        "skill_over_baseline": _safe_float(skill_over_baseline),
        "consistency_warning": consistency_warning,
        "mean_error": _safe_float(np.mean(y_pred - y_true)),
        "p90_abs_error": _safe_float(np.percentile(abs_err, 90)),
    }


def _cross_validation_summary(model, X: pd.DataFrame, y: np.ndarray, target_range: float) -> Dict[str, Any]:
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_validate(
        clone(model),
        X,
        y,
        cv=cv,
        scoring={
            "r2": "r2",
            "mae": "neg_mean_absolute_error",
            "rmse": "neg_root_mean_squared_error",
        },
        n_jobs=1,
        error_score="raise",
    )
    r2_vals = scores["test_r2"]
    mae_vals = -scores["test_mae"]
    rmse_vals = -scores["test_rmse"]
    return {
        "folds": 5,
        "r2_mean": _safe_float(np.mean(r2_vals)),
        "r2_std": _safe_float(np.std(r2_vals)),
        "mae_mean": _safe_float(np.mean(mae_vals)),
        "mae_std": _safe_float(np.std(mae_vals)),
        "rmse_mean": _safe_float(np.mean(rmse_vals)),
        "rmse_std": _safe_float(np.std(rmse_vals)),
        "nmae_mean": _safe_float(np.mean(mae_vals) / target_range),
        "nrmse_mean": _safe_float(np.mean(rmse_vals) / target_range),
    }


def evaluate_viability_model(evaluation_file: str, model_dir: str) -> Dict[str, Any]:
    df = pd.read_csv(evaluation_file)

    if "viability_score" not in df.columns:
        raise ValueError("viability_score column missing in viability evaluation dataset")

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    y = test_df["viability_score"].astype(float).values

    # Build only the features expected by the current viability model pipeline.
    X = pd.DataFrame(
        {
            "career_field": test_df.get("career_field", "Unknown").fillna("Unknown"),
            "current_education_level": test_df.get("current_education_level", "Unknown").fillna("Unknown"),
            "budget_constraint": test_df.get("budget_constraint", "Moderate").fillna("Moderate"),
            "timeline_urgency": test_df.get("timeline_urgency", "Medium").fillna("Medium"),
            "years_of_experience": pd.to_numeric(test_df.get("years_of_experience", 0), errors="coerce"),
            "gpa_percentile": pd.to_numeric(test_df.get("gpa_percentile", 0.5), errors="coerce"),
            "research_experience_months": pd.to_numeric(test_df.get("research_experience_months", 0), errors="coerce"),
            "project_portfolio_count": pd.to_numeric(test_df.get("project_portfolio_count", 0), errors="coerce"),
        }
    )

    model_path = _model_path(model_dir, "career_viability_model.pkl", "viability_model.pkl")
    model = pickle.load(open(model_path, "rb"))
    preds = model.predict(X)
    preds = np.clip(np.asarray(preds, dtype=float), 0.0, 1.0)
    cv_summary = _cross_validation_summary(model, X, y, target_range=1.0)

    return {
        "status": "success",
        "model_name": "career_viability_model",
        "model_path": model_path,
        "dataset_used": evaluation_file,
        "split": "20% holdout from dataset",
        "cv": cv_summary,
        **_metrics(y, preds, target_range=1.0),
    }


def evaluate_academic_model(evaluation_file: str, model_dir: str) -> Dict[str, Any]:
    df = pd.read_csv(evaluation_file)

    if "academic_fit_score" not in df.columns:
        raise ValueError("academic_fit_score column missing in academic evaluation dataset")

    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    y = test_df["academic_fit_score"].astype(float).values

    X = pd.DataFrame(
        {
            "current_degree_field": test_df.get("current_degree_field", "Unknown").fillna("Unknown"),
            "gpa_percentile": pd.to_numeric(test_df.get("gpa_percentile", 0.5), errors="coerce"),
            "research_experience_months": pd.to_numeric(test_df.get("research_experience_months", 0), errors="coerce"),
            "project_portfolio_count": pd.to_numeric(test_df.get("project_portfolio_count", 0), errors="coerce"),
        }
    )

    model_path = _model_path(model_dir, "academic_matcher_model.pkl", "academic_model.pkl")
    model = pickle.load(open(model_path, "rb"))
    preds = model.predict(X)
    preds = np.clip(np.asarray(preds, dtype=float), 0.0, 100.0)
    cv_summary = _cross_validation_summary(model, X, y, target_range=100.0)

    return {
        "status": "success",
        "model_name": "academic_matcher_model",
        "model_path": model_path,
        "dataset_used": evaluation_file,
        "split": "20% holdout from dataset",
        "cv": cv_summary,
        **_metrics(y, preds, target_range=100.0),
    }


def evaluate_all_models(evaluation_dir: str | None = None, model_dir: str | None = None) -> Dict[str, Any]:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    evaluation_dir = evaluation_dir or os.path.join(project_root, "data", "training_dataset")
    model_dir = model_dir or os.path.join(project_root, "ml", "models")

    viability_candidates = [
        os.path.join(evaluation_dir, "career_viability_training.csv"),
        os.path.join(evaluation_dir, "career_viability_evaluation.csv"),
    ]
    academic_candidates = [
        os.path.join(evaluation_dir, "academic_matcher_training.csv"),
        os.path.join(evaluation_dir, "academic_matcher_evaluation.csv"),
    ]

    viability_file = next((p for p in viability_candidates if os.path.exists(p)), viability_candidates[0])
    academic_file = next((p for p in academic_candidates if os.path.exists(p)), academic_candidates[0])

    results: Dict[str, Any] = {"status": "success", "evaluation_dir": evaluation_dir, "model_dir": model_dir, "models": {}}

    try:
        results["models"]["viability"] = evaluate_viability_model(viability_file, model_dir)
    except Exception as exc:
        results["models"]["viability"] = {"status": "error", "message": str(exc)}
        results["status"] = "partial_success"

    try:
        results["models"]["academic"] = evaluate_academic_model(academic_file, model_dir)
    except Exception as exc:
        results["models"]["academic"] = {"status": "error", "message": str(exc)}
        results["status"] = "partial_success"

    if all(model_res.get("status") == "error" for model_res in results["models"].values()):
        results["status"] = "error"

    return results
