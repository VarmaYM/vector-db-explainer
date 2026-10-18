"""Offline structural checks for the interactive explainer."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANIMATION = ROOT / "index.html"
STORYBOARD = ROOT / "docs" / "storyboard.md"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def main() -> None:
    if not ANIMATION.is_file():
        fail(f"missing {ANIMATION}")
    if not STORYBOARD.is_file():
        fail(f"missing {STORYBOARD}")

    html = ANIMATION.read_text(encoding="utf-8")
    storyboard = STORYBOARD.read_text(encoding="utf-8")
    scenes = re.findall(r'<article class="scene(?: active)?"', html)
    if len(scenes) < 8:
        fail(f"expected at least 8 interactive scenes, found {len(scenes)}")

    controls = (
        'id="prevButton"',
        'id="nextButton"',
        'id="playButton"',
        'id="pauseButton"',
        'id="budgetSlider"',
    )
    for control in controls:
        if control not in html:
            fail(f"missing interactive control: {control}")

    source_ids = set(re.findall(r'id="(source-[A-Z0-9]+)"', html))
    source_refs = set(re.findall(r'href="#(source-[A-Z0-9]+)"', html))
    missing_refs = sorted(source_refs - source_ids)
    if missing_refs:
        fail(f"missing internal source anchors: {', '.join(missing_refs)}")

    required_concepts = (
        "inverted index",
        "embedding",
        "nearest",
        "ANN",
        "hybrid",
        "anti-pattern",
        "source of truth",
    )
    lower_html = html.lower()
    for concept in required_concepts:
        if concept.lower() not in lower_html:
            fail(f"animation does not mention {concept}")

    if "Pinecone" not in html:
        fail("animation must label Pinecone as the optional product example")
    if any(term in lower_html for term in ("pricing", "funding", "series b", "revenue")):
        fail("animation contains vendor financial content")

    storyboard_count = len(re.findall(r"^## Scene ", storyboard, flags=re.MULTILINE))
    if storyboard_count < 10:
        fail("storyboard must contain at least 10 scenes")

    print(
        f"PASS: {ANIMATION.relative_to(ROOT)} has {len(scenes)} scenes, "
        f"{len(source_ids)} source anchors, and a {storyboard_count}-scene storyboard"
    )


if __name__ == "__main__":
    main()
