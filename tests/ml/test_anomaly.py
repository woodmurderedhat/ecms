import pandas as pd

from src.ml.anomaly import score_outliers


def test_score_outliers_adds_expected_columns():
    df = pd.DataFrame({"value": [10.0, 11.0, 12.0, 999.0]})
    out = score_outliers(df, feature="value", contamination=0.25)
    assert "outlier_label" in out.columns
    assert "outlier_score" in out.columns
