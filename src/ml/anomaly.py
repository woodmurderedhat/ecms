"""Baseline anomaly detection wrappers."""

from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest

from src.ml.features import MODEL_FEATURE_COLUMNS, build_rule_based_flag_reasons


def _normalize_scores(raw_scores: pd.Series) -> pd.Series:
    if raw_scores.empty:
        return raw_scores
    minimum = float(raw_scores.min())
    maximum = float(raw_scores.max())
    if abs(maximum - minimum) < 1e-9:
        return pd.Series(0.0, index=raw_scores.index, dtype=float)
    return (raw_scores - minimum) / (maximum - minimum)


def score_outliers(
    df: pd.DataFrame,
    feature: str = "value",
    contamination: float = 0.01,
    features: list[str] | None = None,
    score_threshold: float = 0.55,
) -> pd.DataFrame:
    """Assign multivariate outlier labels, scores, and computed case reasons."""
    frame = df.copy()
    feature_columns = features or [feature]
    for column in feature_columns:
        if column not in frame.columns:
            raise KeyError(f"Missing feature column: {column}")

    numeric = frame[feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    if len(frame) < 2 or numeric.nunique().sum() <= len(feature_columns):
        frame["outlier_label"] = 1
        frame["outlier_score"] = 0.0
    else:
        effective_contamination = min(max(contamination, 1 / len(frame)), 0.5)
        model = IsolationForest(contamination=effective_contamination, random_state=42)
        model.fit(numeric)
        frame["outlier_label"] = model.predict(numeric)
        raw_scores = pd.Series(-model.decision_function(numeric), index=frame.index)
        frame["outlier_score"] = _normalize_scores(raw_scores)

    rule_reasons = build_rule_based_flag_reasons(frame)
    computed_scores: list[float] = []
    computed_reasons: list[list[str]] = []

    for index, reasons in rule_reasons.items():
        item_reasons = list(reasons)
        anomaly_score = float(frame.at[index, "outlier_score"])
        if int(frame.at[index, "outlier_label"]) == -1:
            item_reasons.append("anomaly_model")
        combined_score = min(1.0, anomaly_score * 0.7 + min(len(item_reasons), 4) * 0.1)
        computed_scores.append(combined_score)
        computed_reasons.append(sorted(set(item_reasons)))

    frame["computed_flag_score"] = computed_scores
    frame["computed_flag_reasons"] = computed_reasons
    frame["is_case_candidate"] = frame["computed_flag_reasons"].map(bool) | (frame["computed_flag_score"] >= score_threshold)
    return frame
