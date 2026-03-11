"""OCR entry points for scanned document text extraction."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


PRINTABLE_CHUNK_PATTERN = re.compile(rb"[A-Za-z0-9][A-Za-z0-9\s,.;:@#%&()/_\-]{8,}")


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_with_pdftotext(file_path: Path) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", "-q", str(file_path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return ""
    return _normalize_whitespace(result.stdout)


def _extract_printable_chunks(raw_bytes: bytes) -> str:
    snippets = [
        chunk.decode("latin-1", errors="ignore")
        for chunk in PRINTABLE_CHUNK_PATTERN.findall(raw_bytes)
    ]
    return _normalize_whitespace(" ".join(snippets))


def extract_document_text(file_path: str) -> str:
    """Extract best-effort text from a local document path."""
    path = Path(file_path)
    raw_bytes = path.read_bytes()

    if path.suffix.lower() in {".txt", ".md", ".csv", ".json"}:
        return _normalize_whitespace(raw_bytes.decode("utf-8", errors="ignore"))

    if path.suffix.lower() == ".pdf":
        extracted = _extract_with_pdftotext(path)
        if extracted:
            return extracted

    return _extract_printable_chunks(raw_bytes)


def extract_text_from_pdf(file_path: str) -> str:
    """Backward-compatible PDF extraction entry point."""
    return extract_document_text(file_path)
