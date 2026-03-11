"""Callable scheduled live-run entry points for ECMS."""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import requests

from src.ingest.etenders import fetch_etender_releases
from src.ingest.gazette import fetch_gazette_page, parse_gazette_contract_records
from src.ingest.municipal import fetch_municipal_resource
from src.ingest.municipal import parse_municipal_contract_records
from src.pipeline import PipelineResult, run_contract_pipeline
from src.storage import Repository


DEFAULT_CONFIG_PATH = Path("config/default.json")


@dataclass(slots=True)
class SourceRunSummary:
    source: str
    processed_count: int
    case_ids: list[int]
    error: str | None = None


def load_runtime_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load JSON runtime configuration for live fetch cycles."""
    return json.loads(Path(config_path).read_text(encoding="utf-8"))


def _coerce_records(payload: Any, source_url: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        items = payload.get("items") or payload.get("results") or payload.get("data") or []
    else:
        items = []

    records: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        record = dict(item)
        record.setdefault("source_url", f"{source_url}#record-{index}")
        records.append(record)
    return records


def _summarize_pipeline_result(source: str, result: PipelineResult) -> SourceRunSummary:
    return SourceRunSummary(source=source, processed_count=result.processed_count, case_ids=result.case_ids)


def run_scheduled_cycle(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    repository: Repository | None = None,
    session: requests.sessions.Session | None = None,
) -> dict[str, Any]:
    """Run one live pipeline cycle for all configured contract-capable sources."""
    config = load_runtime_config(config_path)
    repo = repository or Repository()
    repo.initialize()
    source_config = config.get("sources", {})
    pipeline_config = config.get("pipeline", {})
    summaries: list[SourceRunSummary] = []

    etender_records = fetch_etender_releases(
        source_config["etender_base_url"],
        max_pages=int(pipeline_config.get("etender_max_pages", 1)),
        timeout=int(pipeline_config.get("request_timeout_seconds", 30)),
        session=session,
    )
    summaries.append(
        _summarize_pipeline_result(
            "etenders",
            run_contract_pipeline(
                source_name="etenders",
                raw_records=etender_records,
                repository=repo,
                score_threshold=float(pipeline_config.get("score_threshold", 0.55)),
            ),
        )
    )

    for resource in source_config.get("municipal_resources", []):
        payload = fetch_municipal_resource(
            source_config["municipal_data_url"],
            resource,
            timeout=int(pipeline_config.get("request_timeout_seconds", 30)),
            session=session,
        )
        municipal_source_url = f"{source_config['municipal_data_url'].rstrip('/')}/{resource.lstrip('/')}"
        records = parse_municipal_contract_records(payload, resource=resource, source_url=municipal_source_url)
        if not records:
            summaries.append(SourceRunSummary(source=f"municipal:{resource}", processed_count=0, case_ids=[]))
            continue
        summaries.append(
            _summarize_pipeline_result(
                f"municipal:{resource}",
                run_contract_pipeline(
                    source_name=f"municipal:{resource}",
                    raw_records=records,
                    repository=repo,
                    score_threshold=float(pipeline_config.get("score_threshold", 0.55)),
                ),
            )
        )

    for path in source_config.get("gazette_paths", []):
        html = fetch_gazette_page(
            source_config["gazette_url"],
            path=path,
            timeout=int(pipeline_config.get("request_timeout_seconds", 30)),
            session=session,
        )
        gazette_source_url = f"{source_config['gazette_url'].rstrip('/')}/{path.lstrip('/')}"
        records = parse_gazette_contract_records(html, source_url=gazette_source_url)
        if not records:
            summaries.append(SourceRunSummary(source=f"gazette:{path}", processed_count=0, case_ids=[]))
            continue
        summaries.append(
            _summarize_pipeline_result(
                f"gazette:{path}",
                run_contract_pipeline(
                    source_name=f"gazette:{path}",
                    raw_records=records,
                    repository=repo,
                    score_threshold=float(pipeline_config.get("score_threshold", 0.55)),
                ),
            )
        )

    return {
        "environment": config.get("environment", "unknown"),
        "poll_interval_minutes": int(pipeline_config.get("poll_interval_minutes", 0)),
        "sources": [asdict(summary) for summary in summaries],
    }


def run_recurring(
    config_path: str | Path = DEFAULT_CONFIG_PATH,
    interval_seconds: int = 0,
    max_cycles: int | None = None,
    repository: Repository | None = None,
    session: requests.sessions.Session | None = None,
) -> list[dict[str, Any]]:
    """Run repeated cycles for local daemon-style execution when desired."""
    results: list[dict[str, Any]] = []
    cycles = 0
    while True:
        result = run_scheduled_cycle(config_path=config_path, repository=repository, session=session)
        results.append(result)
        cycles += 1
        if max_cycles is not None and cycles >= max_cycles:
            break
        if interval_seconds <= 0:
            break
        time.sleep(interval_seconds)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ECMS live fetch cycles")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to runtime config JSON")
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=0,
        help="Delay between cycles. Use 0 to run once and exit.",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=1,
        help="Maximum number of cycles before exit. Ignored when interval is 0.",
    )
    args = parser.parse_args()
    max_cycles = args.max_cycles if args.interval_seconds > 0 else 1
    results = run_recurring(config_path=args.config, interval_seconds=args.interval_seconds, max_cycles=max_cycles)
    print(json.dumps(results[-1], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()