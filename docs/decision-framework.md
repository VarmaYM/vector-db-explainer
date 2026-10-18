# Vector databases: a decision framework

**Research date:** 2026-10-18
**Scope:** technology selection and architecture. No vendor pricing, revenue, or
other vendor-specific financial claims are included.

## The short answer

Use a vector database when the question is:

> **Which stored items are nearest to this query in a representation learned by
> an embedding model?**

Use another system, or a hybrid, when the question is instead:

- **Which exact record is this?** Use a key-value or relational lookup.
- **Can these changes commit atomically?** Use a transactional database.
- **Which rows satisfy these predicates, joins, or aggregates?** Use SQL,
  document queries, a graph database, or an analytical/time-series system.
- **Is this caller allowed to see or change it?** Enforce authorization in a
  policy-aware source of truth and re-check before returning or acting.
- **What is the current value?** Use a current-state store or feature store.
- **What probability or action should we produce?** Use a trained, evaluated,
  and calibrated model behind model serving; use a feature store for its
  point-in-time and online features.

The practical default is often **source of truth + vector retrieval + a
deterministic or learned second stage**. A vector result is a ranked candidate,
not proof that an item is correct, authorized, current, unique, anomalous, or
safe to act on.

## What a vector database actually contributes

An embedding model maps an object and a query into vectors. A vector index then
retrieves nearest candidates under a distance or similarity function. ANN
methods such as HNSW reduce search work, but expose trade-offs among recall,
latency, memory, build time, and update behavior [S1][S2][S3]. Sentence-level
embeddings make semantic-similarity retrieval practical in evaluated settings,
but the result depends on the model, data, metric, and task [S4].

That means a vector database is a **retrieval component**. It does not supply
meaning independently of its embedding model, and a similarity score is not a
calibrated probability. Treat the vector record as a derived, versioned index
over a canonical record whenever correctness, deletion, auditability, or
authorization matters.

## Fast selection flow

1. **Write down the output contract.** Is the output a candidate list, an
   exact record, a current fact, an aggregate, a graph path, a probability, or
   an action?
2. **List hard constraints.** Exact identifiers, numeric/date predicates,
   uniqueness, transactions, joins, ACLs, freshness, and audit requirements
   are filters or sources of truth; do not delegate them to similarity.
3. **Check the retrieval signal.** If relevance is semantic, cross-modal, or
   tolerant of paraphrase, test an embedding model. If relevance is literal,
   identifier-heavy, or must explain term matches, include full-text or exact
   retrieval.
4. **Check whether ANN is needed.** For a small corpus, exact nearest-neighbor
   search or a database extension may be simpler. Add a separate vector system
   when scale, latency, index operations, or workload isolation justify it.
5. **Design the second stage before the index.** Plan filtering, ACL checks,
   metadata hydration, reranking, business rules, model serving, aggregation,
   and logging. Then evaluate recall and end-to-end correctness on real queries.
6. **Version the derived state.** Store source ID, source version, tenant/ACL
   scope, embedding model and dimension, chunk or feature version, timestamps,
   and deletion status with every vector record.

## System-role comparison

The rows describe the primary role of each system family. A product may combine
several roles, but the interface and guarantees still need to be checked rather
than assumed.

| System | Primary job and strengths | Where a vector database is stronger | Where a vector database is weaker | Sensible hybrid architecture |
| --- | --- | --- | --- | --- |
| **Vector database / ANN index** | Retrieve top-*k* items near a query vector; useful for semantic, multimodal, recommendation-candidate, and approximate-neighbor workloads [S1][S3][S4]. | It directly optimizes learned-space nearest-neighbor retrieval and can return metadata with candidates. | Similarity does not provide exact identity, joins, transactions, authorization policy, aggregates, current state, or calibrated decisions. ANN can miss true neighbors. | Canonical source + embedding pipeline + vector index + lexical/exact filters + reranker/model + source-of-truth hydration. |
| **Relational database** | Typed rows, constraints, transactions, joins, grouping, aggregates, and policy mechanisms. SQL supports joins and table expressions [S5][S6], aggregates [S7], and row-level security [S8]. | Semantic candidate generation over text or other embeddings, especially when paired with relational filters. | It is the wrong primitive for learned-space similarity unless extended with a vector index; it is not automatically a semantic retriever. | Keep entities, permissions, facts, and workflow state in SQL; maintain vectors as a projection and join candidate IDs back to SQL. |
| **Full-text search** | Inverted-index retrieval for terms, phrases, fields, token statistics, and explainable lexical relevance. BM25 exposes term-frequency and document-length parameters [S9]. | Paraphrase, cross-lingual, visual, or concept-level matches where words do not overlap. | Exact terms, identifiers, error messages, rare tokens, and phrase constraints can be poorly represented by dense embeddings. | Hybrid lexical + dense retrieval, metadata filters, then a learned or rule-based reranker; preserve lexical hits for explainability. |
| **Document store** | Flexible, nested records organized around access patterns; embedding can reduce joins by storing related data together [S10]. Document operations and, where needed, multi-document transactions are supported by systems such as MongoDB [S11]. | Semantic search across heterogeneous document content or nested objects. | It does not replace document identity, schema validation, atomic workflow state, or document-level authorization. | Store canonical documents and their versions in the document store; index selected fields/chunks in the vector system; hydrate and authorize from the document store. |
| **Key-value store** | Fast exact access by key, counters, sets, streams, and other simple data structures; Redis documents O(1) set membership and ordered sets [S12]. | Approximate related-item lookup when a key is not known. | Exact key lookup, atomic counters, TTL/state, idempotency keys, and cache semantics. | Use KV for hot current state, cache, rate limits, and idempotency; use vectors only for the semantic lookup path. |
| **Graph database** | Nodes, relationships, and declarative path/pattern matching, including variable-length paths and shortest paths [S13]. | Similarity candidate generation over node/edge representations or retrieval of related descriptions. | Explicit relationship traversal, constraints over paths, graph reachability, provenance of edges, and relationship-centric authorization. | Graph for identity and relationship truth; vector index for semantic node/edge candidate generation; graph query validates paths and permissions. |
| **Warehouse / time-series system** | Scan-oriented analytical joins, groupings, statistical aggregates, and time-windowed facts. Analytical systems such as DuckDB target large scans, joins, and aggregations [S14]; time-series extensions add time partitioning and continuous aggregates [S15]. | Nearest historical episodes or similar time-series windows as a search feature. | Sums, percentiles, cohorts, trends, windows, retention, point-in-time facts, and reproducible analysis. | Warehouse/time-series system computes features and aggregates; vector index retrieves similar entities/windows; model or SQL layer makes the conclusion. |
| **Feature store** | Consistent offline training retrieval and low-latency online feature retrieval. Point-in-time joins prevent future leakage, while online stores keep the latest values for an entity [S16][S17]. | Similar-item or similar-entity features can be one input to a model. | Feature freshness, point-in-time correctness, feature definitions, and online/offline parity. | Feature store supplies features to a ranker, fraud/anomaly model, or policy; vector search supplies candidates or analogs. |
| **Ordinary ML model serving** | Package and expose a trained model and dependencies as an inference endpoint [S18]. A model can produce a calibrated probability only after calibration and evaluation; modern neural models can be poorly calibrated [S19]. | Retrieval can supply candidates, context, or nearest examples to the model. | It does not search a corpus by itself, and a vector distance is not a model prediction or calibrated confidence. | Vector retrieval → feature assembly → model endpoint → calibrated threshold/policy → audited action. |

## Workload decision matrix

“Good fit” refers to a vector database being useful in the overall solution,
not necessarily being the only system. “Poor fit” identifies the part that
should not be delegated to vector similarity. Confidence describes the
confidence in the architectural guidance, not an expected benchmark result.

| Workload | Good fit for vectors | Poor fit / preferred system | Hybrid architecture | Common failure modes | Confidence |
| --- | --- | --- | --- | --- | --- |
| **Exact lookup** | Semantic fallback when the user does not know the ID, or alias/typo candidate generation. | Exact ID, hash, uniqueness, and deterministic existence checks belong in KV, relational, or document indexes [S10][S12]. | Exact lookup first; vector fallback only for unresolved natural-language queries; hydrate by canonical ID. | Returning a merely similar record; duplicate IDs; hiding a missing record behind a high similarity score. | **High** |
| **Transactions** | Index committed records asynchronously after the transaction. | Atomic multi-step updates, isolation, durability, and constraints belong in a transactional store [S5][S11]. | Commit source data and an outbox/change event; update or rebuild the vector projection; tolerate and monitor lag. | Vector entry exists without source row; deleted source remains searchable; retries create duplicate or mixed-version records. | **High** |
| **Joins** | Retrieve a small candidate set before expensive relational or graph joins. | Arbitrary joins and referential integrity belong in SQL or graph/document modeling [S6][S10][S13]. | Vector candidate IDs → relational/graph join → final filters and hydration. | Filtering after top-*k* drops all authorized/eligible candidates; stale IDs; top-*k* is too small after joins. | **High** |
| **Authorization** | Metadata prefilters can reduce the candidate set when the index supports them. | Identity, policy evaluation, row-level access, and final authorization belong in the source/policy layer [S8]. | Bind tenant/ACL predicates to the query, retrieve only allowed candidates, then re-check against current policy before display or action. | Cross-tenant leakage; stale ACL metadata; treating namespace/metadata as complete security; authorization after generation. | **High** |
| **Aggregation** | Find similar cohorts, records, or time windows to investigate. | Counts, sums, percentiles, groupings, and time-window facts belong in SQL, warehouses, or time-series systems [S7][S14][S15]. | Aggregate the authoritative filtered set; use vector search only to select examples or cohorts. | Presenting top-*k* composition as a population statistic; approximate recall changes the aggregate; untracked sampling bias. | **High** |
| **Current state** | Semantic search over current records, if freshness and deletes are explicitly managed. | “What is the current balance/status/configuration?” belongs in a current-state KV, relational, document, or feature store [S12][S17]. | Read current state by key; use vectors to find related history or candidates, then re-read current state. | Stale embeddings; old versions outrank current versions; delete/update lag; multiple records for one entity. | **High** |
| **Calibrated decisions** | Candidate generation, nearest historical cases, or similarity features. | Probability, risk threshold, and action selection require an evaluated model, calibration, features, and policy [S16][S18][S19]. | Feature store → model serving → calibration/threshold → deterministic policy; vector retrieval is an optional input. | Treating cosine/distance as probability; threshold copied across models; no abstain path; drift and class-imbalance errors. | **High** |
| **Fraud** | Retrieve similar cases, entities, devices, narratives, or graph-neighborhood candidates; use as features or analyst search. | Final fraud disposition should use event/relationship truth, point-in-time features, a tested model, rules, and review workflows [S13][S16][S18][S19]. | Immutable event ledger + graph features + feature store + model serving/rules; vectors provide analog/candidate retrieval. | Fraudsters imitate common patterns; semantically similar benign cases create false positives; future leakage; adversarial or poisoned content. | **Medium** |
| **Anomaly detection** | Neighbor-distance or similar-window features can flag unusual items for investigation. | A vector index is not an anomaly detector; thresholds and outlier methods need a fitted distribution or detector [S28]. | Time-series/feature pipeline → anomaly model or density method → optional vector nearest-neighbor explanation → alert policy. | Global distance threshold across clusters; embeddings erase magnitude/seasonality; no novelty-vs-outlier distinction; alert score treated as calibrated. | **High** |
| **Deduplication / entity resolution** | Strong candidate generation for paraphrased or near-duplicate text, images, and records. | Final merge/identity decision needs exact keys, blocking, fields, labels, and a classifier or review; entity matching is a classification task in evaluated systems [S27]. | Normalize/hash exact matches → vector blocking → field-aware matcher → canonical identity table and merge audit. | False merges from generic text; false splits from model drift; transitive closure errors; no human review for borderline pairs. | **High** |
| **RAG** | Core retrieval component for external passages and semantic recall; RAG combines parametric and non-parametric memory [S20]. | Source authority, freshness, ACLs, citation provenance, answer verification, and generation are outside nearest-neighbor search [S20][S21]. | Object/document store + lexical/vector hybrid retrieval + ACL filter + reranker + context assembler + generator + citation checks. | Bad chunking; stale/deleted passages; prompt injection in retrieved text; low recall; “nearest” passage is not evidence; long-context use degrades [S22]. | **High** |
| **Recommendations** | Candidate generation for related items, user/item embeddings, and approximate retrieval at scale. | Final ranking, diversity, freshness, policy, exposure, and calibrated outcomes need a ranker and business/user constraints. Industrial systems commonly separate candidate generation from ranking [S25]. | Event log + feature store → vector candidate generation → ranker → diversity/safety/business rules → feedback logging. | Popularity bias; cold start; stale user vectors; feedback loops; candidate set lacks eligible inventory; distance mistaken for utility. | **High** |
| **Semantic search** | Primary fit when relevance is conceptual, paraphrastic, multilingual, or tolerant of vocabulary mismatch [S1][S4]. | Exact terms, quoted phrases, identifiers, rare tokens, and structured filters need lexical/exact retrieval [S9]. | BM25/inverted index + dense ANN + metadata filters + learned reranker; evaluate recall and ranking separately. | Embedding model mismatch; rare-token loss; score scales combined naively; no relevance labels; ANN recall or filter interaction is unknown. | **High** |
| **Multimodal search** | Good fit when a shared embedding space supports text↔image or other cross-modal queries; CLIP demonstrates image/text representation and zero-shot transfer [S23]. | Pixel-level equality, OCR, exact metadata, temporal media constraints, and modality-specific safety checks. | Object store + OCR/metadata index + modality encoders + vector search + lexical/structured filters + reranker. | No shared semantic alignment; captions omit details; image transformations change rank; sensitive content lacks modality-specific controls. | **Medium–High** |
| **Code search** | Semantic search from natural-language intent to relevant functions or snippets; CodeSearchNet defines this as a distinct retrieval task [S24]. | Exact symbol/API/reference lookup, version compatibility, call-graph traversal, security constraints, and compilation/tests. | Lexical + AST/symbol index + dependency graph + vector retrieval → compile/test and version/ACL validation. | Similar code has incompatible behavior; identifiers and literals disappear; stale branches; retrieved code is copied without tests or license/provenance checks. | **High** |
| **Agent memory** | Episodic/semantic recall of observations, past interactions, and useful summaries; generative-agent research retrieves memories dynamically [S26]. | Authoritative profile, permissions, balances, task state, deadlines, and contradictions need structured state and event logs. | Append-only experience log + relational/KV profile/task state + vector memory + recency/importance filters + provenance/expiry + conflict resolver. | Memory poisoning or prompt injection; stale preferences; contradictory summaries; unbounded growth; private data retrieved for the wrong task; treating recall as truth. | **High** |

## Common anti-patterns

| Anti-pattern | Why it fails | Better pattern | Evidence / confidence |
| --- | --- | --- | --- |
| **Vector database as the system of record** | Derived vectors can lag, duplicate, or outlive canonical rows; index maintenance is not the same as transactional truth. | Keep canonical records and audit history in a transactional/document/event store; rebuild the index from versioned source data. | [S5][S10][S11] — **High** |
| **Embedding every query, including exact keys and numbers** | Semantic similarity can turn “account 123” or a literal error code into a near match. | Route exact/structured clauses to exact, lexical, SQL, or graph retrieval; add dense retrieval only where it contributes recall. | [S9][S12] — **High** |
| **Using nearest-neighbor distance as a probability, anomaly score, or authorization decision** | Distance depends on model, metric, corpus, normalization, and index settings; it has no automatic calibration or policy semantics. | Calibrate a trained predictor; fit and validate anomaly thresholds; enforce policy independently. | [S19][S28] — **High** |
| **Vector-only search for every text task** | Dense retrieval can miss rare identifiers, exact phrases, and literal constraints. | Use hybrid lexical+dense retrieval and measure both recall and ranking quality. | [S9][S20][S21] — **High** |
| **No embedding/model/index version in the record** | Re-embedding changes neighborhoods; old and new spaces are not safely comparable. | Version model, dimension, metric, preprocessing, chunking, and index build; support dual-read migration and backfill. | [S1][S3][S4] — **Medium–High** |
| **Chunking without provenance or lifecycle metadata** | The generator cannot reliably cite or remove content, and chunks can lose context. | Store source URI/ID, offsets, title, version, ACL, timestamps, parent document, and deletion state. | [S20][S21][S22] — **High** |
| **Filtering after a small top-*k*** | The eligible set may have no surviving candidates even when relevant authorized items exist. | Apply safe prefilters where possible, over-retrieve, then re-check authorization and constraints on the source of truth. | [S8][S20] — **Medium–High** |
| **Unbounded agent-memory dump** | Repeated, conflicting, or malicious observations crowd out useful recall and increase privacy exposure. | Separate event history, structured state, summarized memory, retention, provenance, and conflict resolution. | [S26][S21] — **Medium–High** |
| **Choosing a new vector service before a workload benchmark** | ANN behavior depends on corpus, dimensionality, updates, filters, *k*, hardware, recall target, and query distribution. | Establish an exact-search baseline, test representative queries, and compare end-to-end quality/latency/freshness. | [S1][S2][S3] — **High** |

## Reference hybrid architectures

### Search and RAG

```text
source documents/object store
        ├── lexical index (terms, phrases, identifiers)
        └── embedding pipeline ──> vector index (chunks + provenance + ACL scope)
                                      │
query ──> exact/metadata/ACL filters ──> over-retrieve ──> rerank
                                      │
                         source-of-truth hydration and citation checks
                                      │
                                  generator / UI
```

Keep the document store authoritative. Record embedding/chunk versions and
deletion events. For a multi-tenant system, authorization is a query and source
validation concern, not merely a namespace convention.

### Recommendations

```text
events ──> offline warehouse + feature definitions ──> online feature store
                                                          │
user/item representation ──> vector candidate retrieval ──> ranker
                                                          │
                                     eligibility, diversity, freshness, policy
                                                          │
                                                        response
```

The vector stage should maximize useful candidate recall. The ranker and policy
stage decide what is eligible and useful for this request; feedback must include
exposure and negative outcomes to avoid reinforcing only retrieved items [S16][S25].

### Fraud and anomaly investigation

```text
immutable events + current entities ──> time-window features / graph features
                                              │
                         feature store ──> calibrated model + rules + review
                                              ▲
                 vector search for similar cases, entities, or explanations
```

This makes vector search an investigative or feature-generation aid. It avoids
making a distance score the final disposition, while retaining structured event
time, relationship, and audit semantics [S13][S16][S18][S19][S28].

### Agent memory

```text
observations ──> append-only log ──> summaries / durable structured state
                         └───────> vector memory (scoped, expiring, sourced)

agent request ──> task/profile/permission lookup
              └─> memory retrieval ─> recency/importance/ACL/conflict checks
                                  └─> model context ─> action policy / tool call
```

Use vector memory for recall, not as the authoritative representation of a
user, permission, task, or external-world fact [S26].

## Evaluation and operational gates

Before production, require evidence for all of the following:

1. **Task relevance:** a labeled query set with recall@*k* and ranking metrics;
   include paraphrases, rare tokens, multilingual or multimodal cases as
   appropriate.
2. **Exactness:** tests for IDs, numbers, dates, joins, deletes, updates,
   duplicate prevention, and current-state reads.
3. **Authorization:** cross-tenant, revoked-access, changed-group, and
   reindexed-document tests; validate both prefilter and post-retrieval checks.
4. **Freshness:** measure source-to-index lag, update/delete completion, and
   behavior during partial ingestion or model migration.
5. **Model validity:** compare embedding versions, record out-of-distribution
   cases, and keep candidate retrieval separate from calibrated model decisions.
6. **Resilience:** test missing index, stale index, duplicate events, partial
   writes, empty results, malformed vectors, and fallback routing.
7. **Observability:** log query/model/index versions, candidate IDs, filters,
   final decisions, and enough provenance to reproduce a result without logging
   unnecessary sensitive content.

## Sources and evidence boundaries

The sources below support the primitive capabilities and cited application
patterns. The “good fit” judgments are architecture synthesis; they are not
claims that one product, index algorithm, embedding model, or benchmark wins on
all workloads. Source pages were checked on 2026-10-18.

| ID | Source | What it supports |
| --- | --- | --- |
| **S1** | Indyk & Motwani, [Approximate Nearest Neighbors](https://doi.org/10.1145/276698.276876), 1998. | ANN as a deliberate approximate alternative to exact nearest-neighbor search. |
| **S2** | Jégou, Douze & Schmid, [Product Quantization for Nearest Neighbor Search](https://doi.org/10.1109/TPAMI.2010.57), 2011. | Vector compression and accuracy/storage trade-offs. |
| **S3** | Malkov & Yashunin, [HNSW](https://arxiv.org/abs/1603.09320), 2016/2018 revision. | Layered proximity graphs and tunable ANN behavior. |
| **S4** | Reimers & Gurevych, [Sentence-BERT](https://arxiv.org/abs/1908.10084), 2019. | Sentence embeddings for efficient similarity comparison in the evaluated tasks. |
| **S5** | PostgreSQL, [Transactions](https://www.postgresql.org/docs/current/tutorial-transactions.html). | Atomicity, visibility, durability, commit, and rollback. |
| **S6** | PostgreSQL, [Table expressions and joins](https://www.postgresql.org/docs/current/queries-table-expressions.html). | SQL joins, predicates, grouping, and table expressions. |
| **S7** | PostgreSQL, [Aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html). | Aggregation and statistical aggregate semantics. |
| **S8** | PostgreSQL, [Row security policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html). | Policy-based per-user row visibility and modification. |
| **S9** | Apache Lucene, [BM25Similarity](https://lucene.apache.org/core/10_1_0/core/org/apache/lucene/search/similarities/BM25Similarity.html). | Lexical scoring based on term statistics, term frequency, and document length. |
| **S10** | MongoDB, [Data modeling](https://www.mongodb.com/docs/manual/data-modeling/). | Flexible documents, access-pattern-oriented modeling, embedding, and referencing. |
| **S11** | MongoDB, [Transactions](https://www.mongodb.com/docs/manual/core/transactions/). | Single-document atomicity and multi-document ACID transaction support. |
| **S12** | Redis, [Data types](https://redis.io/docs/latest/develop/data-types/). | Key/value-oriented data structures, exact set membership, streams, and time-series types. |
| **S13** | Neo4j, [Graph patterns](https://neo4j.com/docs/cypher-manual/current/patterns/). | Declarative node/relationship pattern and path matching. |
| **S14** | DuckDB, [Why DuckDB](https://duckdb.org/why_duckdb). | Analytical scans, joins, aggregations, and columnar/vectorized execution. |
| **S15** | Tiger Data, [TimescaleDB documentation](https://docs.timescale.com/). | Time partitioning, continuous aggregates, retention, and SQL time-series workflows. |
| **S16** | Feast, [Feature retrieval](https://docs.feast.dev/getting-started/concepts/feature-retrieval.md). | Offline/online retrieval, feature services, point-in-time joins, and leakage prevention. |
| **S17** | Feast, [Online store](https://docs.feast.dev/getting-started/components/online-store.md). | Low-latency serving of latest feature values by entity. |
| **S18** | MLflow, [Model serving](https://mlflow.org/docs/latest/ml/deployment/). | Packaging a model and dependencies behind inference endpoints. |
| **S19** | Guo et al., [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599), ICML 2017. | Confidence calibration as a separate problem; modern neural predictions may be poorly calibrated. |
| **S20** | Lewis et al., [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), NeurIPS 2020. | RAG combining parametric generation with a dense non-parametric index. |
| **S21** | Gao et al., [RAG for LLMs: A Survey](https://arxiv.org/abs/2312.10997), 2023/2024 revision. | Retrieval, augmentation, generation stages and recurring RAG challenges. |
| **S22** | Liu et al., [Lost in the Middle](https://arxiv.org/abs/2307.03172), 2023. | Long-context use can depend on evidence position; retrieval does not guarantee use. |
| **S23** | Radford et al., [CLIP](https://arxiv.org/abs/2103.00020), 2021. | Shared image/text representation and cross-modal zero-shot transfer. |
| **S24** | Husain et al., [CodeSearchNet Challenge](https://arxiv.org/abs/1909.09436), 2019/2020 revision. | Semantic code search as natural-language-to-code retrieval. |
| **S25** | Covington, Adams & Sargin, [Deep Neural Networks for YouTube Recommendations](https://research.google/pubs/deep-neural-networks-for-youtube-recommendations/), 2016. | Separate candidate-generation and ranking stages in a recommender architecture. |
| **S26** | Park et al., [Generative Agents](https://arxiv.org/abs/2304.03442), 2023. | Storing, reflecting on, and dynamically retrieving agent experiences. |
| **S27** | Li et al., [Deep Entity Matching with Pre-Trained Language Models](https://arxiv.org/abs/2004.00584), VLDB 2021. | Entity matching as a learned pair-classification task and the need for matching logic beyond candidate similarity. |
| **S28** | scikit-learn, [Novelty and outlier detection](https://scikit-learn.org/stable/modules/outlier_detection.html), current guide. | Anomaly/outlier definitions, fitted scores, thresholds, and the difficulty of high-dimensional detection. |
