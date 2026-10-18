# Vector database decision framework

This repository contains a source-backed research brief for deciding when a
vector database is useful, when another data or ML system is a better fit, and
when a hybrid architecture is required.

The main deliverable is [`docs/decision-framework.md`](docs/decision-framework.md).
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

`make test` runs the offline documentation validator. It checks that the main
brief exists, contains the requested comparison/workload sections, includes the
source key and links, and has no unresolved source tags.

To run the validator directly:

```bash
python3 tools/check_doc.py
```

## Run in Docker

```bash
docker build -t vector-database-decision-framework .
docker run --rm vector-database-decision-framework
```

The image runs the same offline validator and does not require credentials or
network access.

## Deploy or publish

The deliverable is static Markdown. Publish `README.md` and `docs/` through the
repository's normal documentation host, or copy them to an internal Markdown
catalog. Before publishing a refreshed edition, update the research date,
re-check time-sensitive documentation links, run `make test`, and review the
source boundaries in the final section.

## Repository layout

```text
docs/
  decision-framework.md  Main decision framework and source-backed tables
  source-audit.md        Existing animation/source fact sheet
tools/
  check_doc.py           Offline structural validator
Dockerfile               Reproducible validator image
Makefile                 Single offline test command
```
