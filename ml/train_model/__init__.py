"""Model training module."""

from .train_viability_scorer import train_viability_model
from .train_academic_matcher import train_academic_model

__all__ = ["train_viability_model", "train_academic_model"]
