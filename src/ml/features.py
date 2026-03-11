"""Feature engineering utilities for risk scoring."""

from __future__ import annotations

import math

import pandas as pd


def add_log_value_feature(df: pd.DataFrame, column: str = "value") -> pd.DataFrame:
    """Add log-transformed value feature for model stability."""
    out = df.copy()
    out["value_log1p"] = (out[column].clip(lower=0) + 1).map(math.log)
    return out
