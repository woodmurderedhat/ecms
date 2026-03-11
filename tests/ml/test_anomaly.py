import pandas as pd

from src.ml.anomaly import score_outliers
from src.ml.features import engineer_contract_features


def test_score_outliers_adds_expected_columns():
    df = pd.DataFrame({"value": [10.0, 11.0, 12.0, 999.0]})
    out = score_outliers(df, feature="value", contamination=0.25)
    assert "outlier_label" in out.columns
    assert "outlier_score" in out.columns


def test_score_outliers_generates_computed_reasons():
    df = pd.DataFrame(
        {
            "tender_id": ["A", "B", "C"],
            "buyer_org": ["Metro", "Metro", "Town"],
            "supplier": ["Alpha", "Alpha", "Bravo"],
            "award_date": ["2026-03-01", "2026-03-02", "2026-03-03"],
            "value": [1000.0, 2000.0, 900000.0],
            "currency": ["ZAR", "ZAR", "ZAR"],
            "document_text": ["routine award", "extension for urgent works", "emergency deviation"],
            "corroborating_sources": [2, 1, 1],
            "source_url": [
                "https://example.org/A",
                "https://example.org/B",
                "https://example.org/C",
            ],
        }
    )

    featured = engineer_contract_features(df)
    out = score_outliers(featured, features=[column for column in featured.columns if column.endswith("centrality") or column in {"value_log1p", "supplier_award_count", "buyer_award_count", "buyer_supplier_pair_count", "supplier_value_share", "document_keyword_hits", "document_length", "low_corroboration"}], contamination=0.34)

    assert "computed_flag_score" in out.columns
    assert "computed_flag_reasons" in out.columns
    assert any(out["computed_flag_reasons"].map(bool))
