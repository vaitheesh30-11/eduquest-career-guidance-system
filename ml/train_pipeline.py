"""ML training pipeline orchestrator."""

from data_cleaning import clean_viability_dataset, clean_academic_dataset
from train_model import train_viability_model, train_academic_model
from evaluation import evaluate_all_models
import os
from evaluation.evaluate_models import evaluate_all_models




def run_full_pipeline(training_dir, evaluation_dir, output_dir, processed_dir):

    results = {}

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

        viability_clean.to_csv(viability_clean_path,index=False)
        academic_clean.to_csv(academic_clean_path,index=False)
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

    except Exception as e:
        results = {
            "status": "error",
            "message": (e)
        }
    
    return results

if __name__ == "__main__":
    training_dir="data/training_dataset"
    evaluation_dir="data/evaluation_dataset"
    output_dir="ml/models"
    processed_dir="data/processed"
    result = run_full_pipeline(training_dir, evaluation_dir, output_dir, processed_dir)
    print(result)