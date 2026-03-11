"""Evidence packaging and redaction placeholders."""

from __future__ import annotations


def redact_text(raw: str) -> str:
    """Apply basic placeholder redaction rules."""
    return raw.replace("ID", "[REDACTED]")
