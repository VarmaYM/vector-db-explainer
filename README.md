# Vector database decision framework and explainer

This repository contains a source-backed conceptual guide and interactive
animation for understanding where vector databases came from, what problem they
solve, when they help, and when they are the wrong abstraction. It starts with
SQL and NoSQL query contracts, then moves through inverted indexes, feature
vectors, embeddings, exact nearest-neighbor search, ANN, and production vector
retrieval.

The main written deliverable is
[`docs/decision-framework.md`](docs/decision-framework.md). The browser
animation is [`index.html`](index.html), and its 12-scene production plan is
[`docs/storyboard.md`](docs/storyboard.md).
The existing [`docs/source-audit.md`](docs/source-audit.md) records the
foundational embedding, ANN, RAG, and product-claim boundaries used by the
project.

## Requirements

- Python 3.11.2, pinned in [`.python-version`](.python-version)
- GNU Make
- Docker, only for the optional container workflow
- No third-party runtime dependencies; `requirements.lock` is intentionally
  empty apart from its explanatory comment

## Run and test locally

From this directory:

```bash
make test
```

`make test` runs offline documentation and animation validators. It checks that
the main brief contains the requested comparison/workload sections, that the
animation has its controls and internal source links, and that the storyboard
contains the conceptual arc.

To run the validator directly:

```bash
python3 tools/check_doc.py
python3 tools/check_animation.py
```

## Open the animation

The animation has no runtime dependencies and can be opened directly:

```bash
xdg-open index.html
```

Or serve it locally so browser navigation works consistently:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/>. Use the scene controls, keyboard arrows,
`P` for play/pause, and the checkpoint reveal buttons. The ANN budget slider is
conceptual; it is not a benchmark of a particular database.

## Run in Docker

```bash
docker build -t vector-database-decision-framework .
docker run --rm vector-database-decision-framework
```

The image runs the same offline validator and does not require credentials or
network access.

## Deploy or publish

The deliverables are static Markdown and one self-contained HTML file. Publish
`README.md`, `index.html`, and `docs/` through the repository's normal
documentation host, or copy them to an internal catalog. Before publishing a
refreshed edition, update the research date, re-check time-sensitive
documentation links, run `make test`, and review the source boundaries in the
final section.

## Repository layout

```text
docs/
  decision-framework.md  Main decision framework and source-backed tables
  source-audit.md        Source fact sheet and claim boundaries
  storyboard.md          12-scene animation plan
index.html                Self-contained conceptual animation
tools/
  check_doc.py            Offline documentation validator
  check_animation.py      Offline animation validator
Dockerfile                 Reproducible validator image
Makefile                   Single offline test command
```
