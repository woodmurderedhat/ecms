"""Feature engineering utilities for risk scoring."""

from __future__ import annotations

import math

import networkx as nx
import pandas as pd


RISK_KEYWORDS = (
    "urgent",
    "emergency",
    "variation",
    "extension",
    "sole source",
    "deviation",
)

MODEL_FEATURE_COLUMNS = [
    "value_log1p",
    "supplier_award_count",
    "buyer_award_count",
    "buyer_supplier_pair_count",
    "supplier_value_share",
    "document_keyword_hits",
    "document_length",
    "low_corroboration",
    "supplier_degree_centrality",
    "buyer_degree_centrality",
]


def add_log_value_feature(df: pd.DataFrame, column: str = "value") -> pd.DataFrame:
    """Add log-transformed value feature for model stability."""
    out = df.copy()
    out["value_log1p"] = (out[column].clip(lower=0) + 1).map(math.log)
    return out


def _count_keywords(text: str) -> int:
    lowered = text.lower()
    return sum(lowered.count(keyword) for keyword in RISK_KEYWORDS)


def _centrality_maps(frame: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    graph = nx.Graph()
    for row in frame.itertuples(index=False):
        buyer = f"buyer::{row.buyer_org}"
        supplier = f"supplier::{row.supplier}"
        graph.add_edge(buyer, supplier)

    if len(graph) <= 1:
        return {}, {}

    centrality = nx.degree_centrality(graph)
    supplier_map = {
        supplier.replace("supplier::", "", 1): score
        for supplier, score in centrality.items()
        if supplier.startswith("supplier::")
    }
    buyer_map = {
        buyer.replace("buyer::", "", 1): score
        for buyer, score in centrality.items()
        if buyer.startswith("buyer::")
    }
    return supplier_map, buyer_map


def engineer_contract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build batch-level risk features used for anomaly detection and case scoring."""
    out = add_log_value_feature(df)
    out["award_date"] = pd.to_datetime(out["award_date"], errors="coerce")
    out["corroborating_sources"] = pd.to_numeric(out.get("corroborating_sources", 1), errors="coerce").fillna(1)
    out["supplier_award_count"] = out.groupby("supplier")["tender_id"].transform("count").astype(float)
    out["buyer_award_count"] = out.groupby("buyer_org")["tender_id"].transform("count").astype(float)
    out["buyer_supplier_pair_count"] = out.groupby(["buyer_org", "supplier"])["tender_id"].transform("count").astype(float)
    total_value = float(out["value"].sum()) or 1.0
    out["supplier_total_value"] = out.groupby("supplier")["value"].transform("sum")
    out["supplier_value_share"] = out["supplier_total_value"] / total_value
    out["document_text"] = out.get("document_text", "").fillna("").astype(str)
    out["document_length"] = out["document_text"].str.len().astype(float)
    out["document_keyword_hits"] = out["document_text"].map(_count_keywords).astype(float)
    out["low_corroboration"] = (out["corroborating_sources"] < 2).astype(float)

    supplier_centrality, buyer_centrality = _centrality_maps(out)
    out["supplier_degree_centrality"] = out["supplier"].map(supplier_centrality).fillna(0.0)
    out["buyer_degree_centrality"] = out["buyer_org"].map(buyer_centrality).fillna(0.0)

    numeric_columns = MODEL_FEATURE_COLUMNS + ["supplier_total_value"]
    for column in numeric_columns:
        out[column] = pd.to_numeric(out[column], errors="coerce").fillna(0.0)
    return out


def build_rule_based_flag_reasons(df: pd.DataFrame) -> pd.Series:
    """Generate per-record rule-based risk reasons from engineered features."""
    if df.empty:
        return pd.Series(dtype=object)

    frame = df.copy()
    defaults: dict[str, float | str] = {
        "value": 0.0,
        "supplier_award_count": 0.0,
        "buyer_supplier_pair_count": 0.0,
        "low_corroboration": 0.0,
        "document_keyword_hits": 0.0,
        "supplier_degree_centrality": 0.0,
    }
    for column, default in defaults.items():
        if column not in frame.columns:
            frame[column] = default

    high_value_threshold = float(frame["value"].quantile(0.9)) if len(frame) > 1 else float(frame["value"].max())
    centrality_threshold = float(frame["supplier_degree_centrality"].quantile(0.75)) if len(frame) > 1 else 0.0

    def _reasons(row: pd.Series) -> list[str]:
        reasons: list[str] = []
        if float(row["value"]) >= high_value_threshold and high_value_threshold > 0:
            reasons.append("high_value")
        if float(row["supplier_award_count"]) > 1:
            reasons.append("repeat_supplier")
        if float(row["buyer_supplier_pair_count"]) > 1:
            reasons.append("repeat_buyer_supplier_pair")
        if float(row["low_corroboration"]) >= 1:
            reasons.append("low_corroboration")
        if float(row["document_keyword_hits"]) > 0:
            reasons.append("document_keyword_match")
        if float(row["supplier_degree_centrality"]) >= centrality_threshold and centrality_threshold > 0:
            reasons.append("supplier_network_centrality")
        return reasons

    return frame.apply(_reasons, axis=1)
