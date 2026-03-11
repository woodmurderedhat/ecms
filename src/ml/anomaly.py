"""Baseline anomaly detection wrappers."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest


def score_outliers(df: pd.DataFrame, feature: str = "value", contamination: float = 0.01) -> pd.DataFrame:
    """Assign outlier labels and scores based on a single numeric feature."""
    model = IsolationForest(contamination=contamination, random_state=42)
    frame = df.copy()
    model.fit(frame[[feature]])
    frame["outlier_label"] = model.predict(frame[[feature]])
    frame["outlier_score"] = model.decision_function(frame[[feature]])
    return frame
