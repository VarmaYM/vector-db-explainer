"""Offline structural checks for the research deliverable."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "docs" / "decision-framework.md"
AUDIT = ROOT / "docs" / "source-audit.md"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not BRIEF.is_file():
        fail(f"missing {BRIEF}")
    if not AUDIT.is_file():
        fail(f"missing {AUDIT}")

    text = BRIEF.read_text(encoding="utf-8")
    required_headings = (
        "## System-role comparison",
        "## Workload decision matrix",
        "## Common anti-patterns",
        "## Reference hybrid architectures",
        "## Sources and evidence boundaries",
    )
    for heading in required_headings:
        if heading not in text:
            fail(f"missing heading: {heading}")

    required_terms = (
        "exact lookup",
        "transactions",
        "joins",
        "authorization",
        "aggregation",
        "current state",
        "calibrated decisions",
        "fraud",
        "anomaly detection",
        "deduplication",
        "RAG",
        "recommendations",
        "semantic search",
        "multimodal search",
        "code search",
        "agent memory",
    )
    lower_text = text.lower()
    for term in required_terms:
        if term.lower() not in lower_text:
            fail(f"missing requested workload: {term}")

    source_ids = set(re.findall(r"\[S(\d+)\]", text))
    declared_ids = set(re.findall(r"\| \*\*S(\d+)\*\* \|", text))
    if len(declared_ids) < 20:
        fail("expected at least 20 declared sources")
    undeclared = sorted(source_ids - declared_ids, key=int)
    if undeclared:
        fail(f"undeclared source tags: {', '.join('S' + item for item in undeclared)}")

    links = re.findall(r"https?://[^)\s]+", text)
    if len(links) < 20:
        fail("expected at least 20 source links")

    print(
        f"PASS: {BRIEF.relative_to(ROOT)} has the requested sections, "
        f"{len(declared_ids)} declared sources, and {len(links)} links"
    )


if __name__ == "__main__":
    main()
