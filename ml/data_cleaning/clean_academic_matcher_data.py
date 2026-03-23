"""Data cleaning for academic career matcher training dataset."""

import pandas as pd
import numpy as np

def clean_academic_dataset(input_file)->pd.DataFrame:
    df= pd.read_csv(input_file)
    df = df.dropna()
    
    df= df[(df["gpa_percentile"]>=0) & (df["gpa_percentile"]<=1)]
    df= df[(df["research_experience_months"]>=0)]
    df= df[(df["project_portfolio_count"]>=0)]
    df= df[(df["academic_fit_score"]>=0) & (df["academic_fit_score"]<=100)]
    numeric_cols=[
        
        "gpa_percentile",
        "research_experience_months",
        "project_portfolio_count",
        "academic_fit_score"
    ]

    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5*IQR
        upper = Q3 + 1.5*IQR

        df = df[(df[col] >= lower) & (df[col] <= upper)]

    return df.reset_index(drop=True)
     
