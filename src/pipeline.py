"""Pipeline orchestration for ingesting and storing contract data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from urllib.parse import quote

import pandas as pd

from src.etl.normalize import normalize_contract_record
from src.ml.anomaly import score_outliers
from src.ml.features import MODEL_FEATURE_COLUMNS, engineer_contract_features
from src.ocr.extract import extract_document_text
from src.storage import Repository


@dataclass(slots=True)
class PipelineResult:
    run_id: int
    processed_count: int
    case_ids: list[int]


def _fallback_source_url(source_name: str, external_id: str) -> str:
    return f"https://records.invalid/{quote(source_name)}/{quote(external_id)}"


def _collect_document_paths(raw_record: dict[str, Any]) -> list[str]:
    document_paths: list[str] = []
    single_path = raw_record.get("document_path")
    if isinstance(single_path, str) and single_path.strip():
        document_paths.append(single_path)
    multiple_paths = raw_record.get("document_paths") or []
    for item in multiple_paths:
        if isinstance(item, str) and item.strip():
            document_paths.append(item)
    for document in raw_record.get("documents") or []:
        if isinstance(document, dict):
            path = document.get("path") or document.get("local_path")
            if isinstance(path, str) and path.strip():
                document_paths.append(path)
    return document_paths


def _extract_record_document_text(raw_record: dict[str, Any]) -> str:
    existing_text = str(raw_record.get("document_text") or "").strip()
    extracted_parts = [existing_text] if existing_text else []
    for document_path in _collect_document_paths(raw_record):
        extracted = extract_document_text(document_path)
        if extracted:
            extracted_parts.append(extracted)
    return "\n\n".join(part for part in extracted_parts if part).strip()


def run_contract_pipeline(
    source_name: str,
    raw_records: Iterable[dict[str, Any]],
    repository: Repository,
    score_threshold: float = 0.55,
) -> PipelineResult:
    """Store raw records, normalize them, and create analyst cases."""
    repository.initialize()
    run_id = repository.create_fetch_run(source_name)
    processed_count = 0
    case_ids: list[int] = []
    normalized_records: list[dict[str, Any]] = []

    try:
        for raw_record in raw_records:
            external_id = str(
                raw_record.get("id")
                or raw_record.get("ocid")
                or raw_record.get("tender_id")
                or f"{source_name}-{processed_count + 1}"
            )
            source_url = raw_record.get("source_url") or raw_record.get("url") or _fallback_source_url(
                source_name, external_id
            )
            repository.record_raw_record(run_id, source_name, external_id, raw_record, source_url)

            document_text = _extract_record_document_text(raw_record)
            repository.record_transform(
                stage="ocr",
                source=source_name,
                record_key=external_id,
                status="completed",
                details={"document_text_length": len(document_text)},
            )

            normalized = normalize_contract_record(raw_record, source_url=source_url, document_text=document_text)
            normalized_records.append(normalized)

        if normalized_records:
            feature_frame = engineer_contract_features(pd.DataFrame(normalized_records))
            scored_frame = score_outliers(
                feature_frame,
                features=MODEL_FEATURE_COLUMNS,
                contamination=0.15,
                score_threshold=score_threshold,
            )
        else:
            scored_frame = pd.DataFrame()

        for index, normalized in enumerate(normalized_records):
            row = scored_frame.iloc[index] if not scored_frame.empty else pd.Series(dtype=object)
            computed_reasons = list(row.get("computed_flag_reasons", [])) if not row.empty else []
            merged_reasons = sorted(set(normalized.get("flag_reasons", [])) | set(computed_reasons))
            computed_score = float(row.get("computed_flag_score", 0.0)) if not row.empty else 0.0
            existing_score = float(normalized.get("flag_score") or 0.0)
            normalized["flag_score"] = max(existing_score, computed_score)
            normalized["flag_reasons"] = merged_reasons

            contract_id = repository.upsert_contract(normalized, source_name=source_name)
            repository.record_transform(
                stage="normalize",
                source=source_name,
                record_key=normalized["tender_id"],
                status="completed",
                details={"contract_id": contract_id, "source_url": normalized["source_url"]},
            )

            should_create_case = bool(merged_reasons) or normalized["flag_score"] >= score_threshold
            if should_create_case:
                case_id = repository.create_or_update_case(
                    contract_id=contract_id,
                    flag_score=normalized["flag_score"],
                    flag_reasons=merged_reasons,
                    corroborating_sources=max(1, int(normalized.get("corroborating_sources", 1))),
                )
                case_ids.append(case_id)

            processed_count += 1
    except Exception as exc:
        repository.record_transform(
            stage="pipeline",
            source=source_name,
            record_key="*",
            status="failed",
            details={"error": str(exc)},
        )
        repository.complete_fetch_run(run_id, status="failed", error=str(exc))
        raise

    repository.complete_fetch_run(run_id)
    return PipelineResult(run_id=run_id, processed_count=processed_count, case_ids=case_ids)
