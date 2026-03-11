"""SQLite-backed persistence helpers for ECMS pipeline state."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator


DEFAULT_DB_PATH = Path("data/ecms.db")


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS fetch_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    status TEXT NOT NULL,
    error TEXT
);

CREATE TABLE IF NOT EXISTS raw_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fetch_run_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    source_url TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    FOREIGN KEY(fetch_run_id) REFERENCES fetch_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id TEXT NOT NULL,
    buyer_org TEXT NOT NULL,
    supplier TEXT NOT NULL,
    award_date TEXT NOT NULL,
    value REAL NOT NULL,
    currency TEXT NOT NULL,
    description TEXT,
    document_text TEXT NOT NULL DEFAULT '',
    flag_score REAL,
    flag_reasons TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_name TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    UNIQUE(tender_id, source_url)
);

CREATE TABLE IF NOT EXISTS transform_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage TEXT NOT NULL,
    source TEXT NOT NULL,
    record_key TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_id INTEGER NOT NULL UNIQUE,
    state TEXT NOT NULL,
    flag_score REAL,
    flag_reasons TEXT NOT NULL,
    corroborating_sources INTEGER NOT NULL DEFAULT 1,
    legal_review_status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS evidence_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    redacted_payload TEXT NOT NULL,
    export_status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL,
    FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE
);
"""


def _utc_now() -> str:
    return datetime.now(tz=UTC).isoformat()


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _deserialize_case(row: sqlite3.Row) -> dict[str, Any]:
    payload = dict(row)
    payload["flag_reasons"] = json.loads(payload["flag_reasons"])
    payload["contract"] = {
        "id": payload.pop("contract_db_id"),
        "tender_id": payload.pop("tender_id"),
        "buyer_org": payload.pop("buyer_org"),
        "supplier": payload.pop("supplier"),
        "award_date": payload.pop("award_date"),
        "value": payload.pop("value"),
        "currency": payload.pop("currency"),
        "description": payload.pop("description"),
        "document_text": payload.pop("document_text"),
        "source_url": payload.pop("source_url"),
        "source_name": payload.pop("source_name"),
    }
    return payload


class Repository:
    """Lightweight repository for contracts, cases, and provenance."""

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connection() as conn:
            conn.executescript(SCHEMA)

    def create_fetch_run(self, source: str, status: str = "running") -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO fetch_runs(source, started_at, status) VALUES (?, ?, ?)",
                (source, _utc_now(), status),
            )
            return int(cursor.lastrowid)

    def complete_fetch_run(self, run_id: int, status: str = "completed", error: str | None = None) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE fetch_runs
                SET completed_at = ?, status = ?, error = ?
                WHERE id = ?
                """,
                (_utc_now(), status, error, run_id),
            )

    def record_raw_record(
        self,
        fetch_run_id: int,
        source: str,
        external_id: str,
        payload: dict[str, Any],
        source_url: str,
    ) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO raw_records(fetch_run_id, source, external_id, payload, source_url, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (fetch_run_id, source, external_id, _json_dumps(payload), source_url, _utc_now()),
            )
            return int(cursor.lastrowid)

    def record_transform(
        self,
        stage: str,
        source: str,
        record_key: str,
        status: str,
        details: dict[str, Any],
    ) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO transform_logs(stage, source, record_key, status, details, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (stage, source, record_key, status, _json_dumps(details), _utc_now()),
            )

    def upsert_contract(self, record: dict[str, Any], source_name: str) -> int:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO contracts(
                    tender_id,
                    buyer_org,
                    supplier,
                    award_date,
                    value,
                    currency,
                    description,
                    document_text,
                    flag_score,
                    flag_reasons,
                    source_url,
                    source_name,
                    last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(tender_id, source_url) DO UPDATE SET
                    buyer_org = excluded.buyer_org,
                    supplier = excluded.supplier,
                    award_date = excluded.award_date,
                    value = excluded.value,
                    currency = excluded.currency,
                    description = excluded.description,
                    document_text = excluded.document_text,
                    flag_score = excluded.flag_score,
                    flag_reasons = excluded.flag_reasons,
                    source_name = excluded.source_name,
                    last_updated = excluded.last_updated
                """,
                (
                    record["tender_id"],
                    record["buyer_org"],
                    record["supplier"],
                    record["award_date"],
                    record["value"],
                    record["currency"],
                    record.get("description"),
                    record.get("document_text", ""),
                    record.get("flag_score"),
                    _json_dumps(record.get("flag_reasons", [])),
                    record["source_url"],
                    source_name,
                    _utc_now(),
                ),
            )
            row = conn.execute(
                "SELECT id FROM contracts WHERE tender_id = ? AND source_url = ?",
                (record["tender_id"], record["source_url"]),
            ).fetchone()
            return int(row["id"])

    def create_or_update_case(
        self,
        contract_id: int,
        flag_score: float | None,
        flag_reasons: list[str],
        corroborating_sources: int = 1,
        legal_review_status: str = "pending",
    ) -> int:
        with self.connection() as conn:
            conn.execute(
                """
                INSERT INTO cases(
                    contract_id,
                    state,
                    flag_score,
                    flag_reasons,
                    corroborating_sources,
                    legal_review_status,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contract_id) DO UPDATE SET
                    flag_score = excluded.flag_score,
                    flag_reasons = excluded.flag_reasons,
                    corroborating_sources = excluded.corroborating_sources,
                    updated_at = excluded.updated_at,
                    legal_review_status = excluded.legal_review_status
                """,
                (
                    contract_id,
                    "pending_verification",
                    flag_score,
                    _json_dumps(flag_reasons),
                    corroborating_sources,
                    legal_review_status,
                    _utc_now(),
                    _utc_now(),
                ),
            )
            row = conn.execute("SELECT id FROM cases WHERE contract_id = ?", (contract_id,)).fetchone()
            return int(row["id"])

    def get_case(self, case_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT
                    c.id,
                    c.contract_id,
                    c.state,
                    c.flag_score,
                    c.flag_reasons,
                    c.corroborating_sources,
                    c.legal_review_status,
                    c.created_at,
                    c.updated_at,
                    contracts.id AS contract_db_id,
                    contracts.tender_id,
                    contracts.buyer_org,
                    contracts.supplier,
                    contracts.award_date,
                    contracts.value,
                    contracts.currency,
                    contracts.description,
                    contracts.document_text,
                    contracts.source_url,
                    contracts.source_name
                FROM cases c
                JOIN contracts ON contracts.id = c.contract_id
                WHERE c.id = ?
                """,
                (case_id,),
            ).fetchone()
        if row is None:
            return None
        return _deserialize_case(row)

    def list_cases(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    c.id,
                    c.contract_id,
                    c.state,
                    c.flag_score,
                    c.flag_reasons,
                    c.corroborating_sources,
                    c.legal_review_status,
                    c.created_at,
                    c.updated_at,
                    contracts.id AS contract_db_id,
                    contracts.tender_id,
                    contracts.buyer_org,
                    contracts.supplier,
                    contracts.award_date,
                    contracts.value,
                    contracts.currency,
                    contracts.description,
                    contracts.document_text,
                    contracts.source_url,
                    contracts.source_name
                FROM cases c
                JOIN contracts ON contracts.id = c.contract_id
                ORDER BY c.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [_deserialize_case(row) for row in rows]

    def update_case(
        self,
        case_id: int,
        *,
        state: str | None = None,
        legal_review_status: str | None = None,
        corroborating_sources: int | None = None,
    ) -> dict[str, Any] | None:
        updates: list[str] = []
        params: list[Any] = []
        if state is not None:
            updates.append("state = ?")
            params.append(state)
        if legal_review_status is not None:
            updates.append("legal_review_status = ?")
            params.append(legal_review_status)
        if corroborating_sources is not None:
            updates.append("corroborating_sources = ?")
            params.append(int(corroborating_sources))

        if not updates:
            return self.get_case(case_id)

        updates.append("updated_at = ?")
        params.append(_utc_now())
        params.append(case_id)
        query = f"UPDATE cases SET {', '.join(updates)} WHERE id = ?"
        with self.connection() as conn:
            conn.execute(query, tuple(params))
        return self.get_case(case_id)

    def get_case_summary(self) -> dict[str, Any]:
        with self.connection() as conn:
            case_counts = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_cases,
                    SUM(CASE WHEN state = 'pending_verification' THEN 1 ELSE 0 END) AS pending_cases,
                    SUM(CASE WHEN legal_review_status = 'approved' THEN 1 ELSE 0 END) AS approved_cases,
                    COALESCE(AVG(flag_score), 0) AS avg_flag_score
                FROM cases
                """
            ).fetchone()
            evidence_counts = conn.execute(
                """
                SELECT
                    COUNT(*) AS evidence_packages,
                    SUM(CASE WHEN export_status = 'ready_for_publication' THEN 1 ELSE 0 END) AS ready_publication_packages
                FROM evidence_packages
                """
            ).fetchone()

        return {
            "total_cases": int(case_counts["total_cases"] or 0),
            "pending_cases": int(case_counts["pending_cases"] or 0),
            "approved_cases": int(case_counts["approved_cases"] or 0),
            "avg_flag_score": float(case_counts["avg_flag_score"] or 0.0),
            "evidence_packages": int(evidence_counts["evidence_packages"] or 0),
            "ready_publication_packages": int(evidence_counts["ready_publication_packages"] or 0),
        }

    def create_evidence_package(
        self,
        case_id: int,
        redacted_payload: dict[str, Any],
        export_status: str = "draft",
    ) -> int:
        with self.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO evidence_packages(case_id, redacted_payload, export_status, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (case_id, _json_dumps(redacted_payload), export_status, _utc_now()),
            )
            return int(cursor.lastrowid)

    def get_evidence_package(self, package_id: int) -> dict[str, Any] | None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id, case_id, redacted_payload, export_status, created_at FROM evidence_packages WHERE id = ?",
                (package_id,),
            ).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["redacted_payload"] = json.loads(payload["redacted_payload"])
        return payload

    def list_evidence_packages(self, case_id: int, limit: int = 10) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, case_id, redacted_payload, export_status, created_at
                FROM evidence_packages
                WHERE case_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (case_id, limit),
            ).fetchall()
        payloads: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["redacted_payload"] = json.loads(payload["redacted_payload"])
            payloads.append(payload)
        return payloads
