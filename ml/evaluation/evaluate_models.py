"""Evaluate trained ML models on evaluation datasets."""

import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np



def evaluate_viability_model(evaluation_file, model_dir):

    df = pd.read_csv(evaluation_file)

    y = df["viabilty_score"]
    X = df.drop(columns=["viability_score"])

    model = pickle.load(open(f"{model_dir}/viability_model.pkl", "rb"))
    scaler = pickle.load(open(f"{model_dir}/viability_scaler.pkl", "rb"))

    x_scaled = scaler.transform(X)
    preds = model.predict(x_scaled)

    return {
        "status": "succees",
        "model_name": "viability_model",
        "samples": len(df),
        "r2": float(r2_score(y, preds)),
        "mae": float(mean_absolute_error(y, preds)),
        "rmse": float(np.sqrt(mean_squared_error(y, preds))),
    }

def evaluate_academic_model(evaluation_file, model_dir):

    df = pd.read_csv(evaluation_file)

    y = df["academic_fit_score"]
    X = df.drop(columns=["academic_fit_score"])

    model = pickle.load(open(f"{model_dir}/academic_model.pkl", "rb"))
    scaler = pickle.load(open(f"{model_dir}/academic_scaler.pkl", "rb"))

    x_scaled = scaler.transform(X)
    preds = model.predict(x_scaled)

    return {
        "status": "succees",
        "model_name": "academic_model",
        "samples": len(df),
        "r2": float(r2_score(y, preds)),
        "mae": float(mean_absolute_error(y, preds)),
        "rmse": float(np.sqrt(mean_squared_error(y, preds)))
    }

def evaluate_all_models(evaluation_dir, model_dir):

    results = {}

    try:
        viability = evaluate_viability_model(
            f"{evaluation_dir}/viability_eval.csv",
            model_dir
        )

        academic = evaluate_academic_model(
            f"{evaluation_dir}/academic_eval.csv",
            model_dir
        )

        results["status"] = "success"
        results["model"] = {
            "viability": viability,
            "academic": academic
        }

    except Exception as e:

        results = {
            "status": "error",
            "message": str(e)
        }
    
    return results
