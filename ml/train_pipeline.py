"""ML training pipeline orchestrator."""

from __future__ import annotations

import os

from data_cleaning import clean_viability_dataset, clean_academic_dataset
from evaluation.evaluate_models import evaluate_all_models
from train_model import train_viability_model, train_academic_model

try:
    from ml.observability import trace_block, tracing_session
except ModuleNotFoundError:  # Supports running `python ml/train_pipeline.py`
    from observability import trace_block, tracing_session


def run_full_pipeline(training_dir, evaluation_dir, output_dir, processed_dir):
    results = {}
    trace_inputs = {
        "training_dir": training_dir,
        "evaluation_dir": evaluation_dir,
        "output_dir": output_dir,
        "processed_dir": processed_dir,
    }

    with tracing_session(tags=["ml", "pipeline"], metadata=trace_inputs):
        with trace_block(
            "run_full_pipeline",
            run_type="chain",
            inputs=trace_inputs,
            tags=["ml", "pipeline"],
            metadata={"pipeline": "training"},
        ) as run:
            try:
                os.makedirs(processed_dir, exist_ok=True)
                os.makedirs(output_dir, exist_ok=True)

                viability_clean = clean_viability_dataset(
                    f"{training_dir}/career_viability_training.csv"
                )
                academic_clean = clean_academic_dataset(
                    f"{training_dir}/academic_matcher_training.csv"
                )

                viability_clean_path = f"{processed_dir}/career_viability_clean.csv"
                academic_clean_path = f"{processed_dir}/academic_matcher_clean.csv"

                viability_clean.to_csv(viability_clean_path, index=False)
                academic_clean.to_csv(academic_clean_path, index=False)
                viability_model = train_viability_model(
                    viability_clean_path,
                    output_dir
                )

                academic_model = train_academic_model(
                    academic_clean_path,
                    output_dir
                )

                evaluation = evaluate_all_models(
                    evaluation_dir,
                    output_dir
                )

                results = {
                    "status": "success",
                    "data_cleaning": "completed",
                    "viability_training": viability_model,
                    "academic_training": academic_model,
                    "evaluation": evaluation
                }
                if run is not None:
                    run.end(outputs={"status": results["status"]})
            except Exception as e:
                results = {
                    "status": "error",
                    "message": str(e)
                }
                if run is not None:
                    run.end(error=str(e))

    return results

if __name__ == "__main__":
    training_dir="data/training_dataset"
    evaluation_dir="data/evaluation_dataset"
    output_dir="ml/models"
    processed_dir="data/processed"
    result = run_full_pipeline(training_dir, evaluation_dir, output_dir, processed_dir)
    print(result)
