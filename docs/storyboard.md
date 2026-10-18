# Storyboard: From Database Queries to Vector Retrieval

This storyboard teaches the conceptual origin and evolution of vector databases.
It moves from systems that answer exact, lexical, and structured questions to
learned representations and nearest-neighbor retrieval, then ends with the
production architecture that makes vector search useful and safe.

Source IDs below refer to `docs/source-audit.md` and
`docs/decision-framework.md`. Confidence describes the claim being taught, not
an expected benchmark result.

## Scene 1 — The first contract: exact facts and structured questions

**Visual direction**

Open on a canonical table labeled `orders`. A user asks three questions in
sequence: `status = 'open'`, `JOIN customers`, and `COMMIT payment + inventory`.
Animate a SQL predicate selecting rows, a join line connecting tables, and a
transaction boundary that either commits both writes or rolls both back. Keep
the source-of-truth database visually solid and authoritative.

**Narration**

“Database search began with explicit contracts. SQL predicates select rows that
match conditions; joins combine related facts; aggregates summarize a defined
set; and transactions make related changes commit or roll back together. These
systems answer questions about identity, state, relationships, and invariants.
Those guarantees are different from ‘which item is most similar to this
query?’”

**Animation state**

`state: canonical-structured-data` — rows, constraints, relationships, and
transaction state are visible. On each question, show a deterministic result or
an explicit transaction failure; no similarity score appears yet.

**Checkpoint question**

“If the required output is an exact row, a join, an aggregate, or an atomic
write, what should own that responsibility?”

**Source IDs**

`[S5] [S6] [S7] [S8]`

**Confidence / caveats**

**High.** This is a role-level summary of relational capabilities. Specific
transaction isolation, constraint, and policy behavior depends on the database
and configuration; similarity search does not replace those guarantees.

## Scene 2 — When the question is words: the inverted index

**Visual direction**

Transform a document shelf into a term dictionary. Show `refund`, `late`, and
`invoice` as dictionary entries pointing to posting lists of document IDs. A
query highlights matching terms and phrases; term frequency and document length
briefly influence a lexical score. Keep the matching words glowing so the
viewer can see why a result was returned.

**Narration**

“Full-text search changed the unit of retrieval from a row predicate to a word
or phrase. An inverted index maps terms to the documents that contain them, so
the system can retrieve and explain literal matches at scale. This is powerful
for identifiers, rare tokens, quoted phrases, and error messages—but two texts
can express the same idea without sharing the same words.”

**Animation state**

`state: lexical-retrieval` — `query terms → postings → lexical ranking`. Toggle
between a shared term that retrieves a document and a paraphrase that produces
no lexical hit.

**Checkpoint question**

“Which search signal is necessary when the user’s phrase, identifier, or error
code must be matched literally?”

**Source IDs**

`[S9] [R2]`

**Confidence / caveats**

**High.** Inverted indexes and term-statistic ranking support literal retrieval
and explainability. A lexical score is not semantic understanding, and the best
lexical ranking depends on analyzer, language, fields, and workload.

## Scene 3 — Access patterns beyond tables: key-value and documents

**Visual direction**

Split the screen into two paths. On the left, a key-value map answers
`user:42 → current session` in one direct hop and shows a counter and TTL. On
the right, a nested document groups an order, line items, and shipping details
because that is the application’s read pattern. Animate an exact key lookup,
document update, and optional multi-document transaction; do not make either
path look like a similarity search.

**Narration**

“NoSQL systems made the access pattern explicit. A key-value store is excellent
when the key is known and the application needs fast current state, counters,
sets, or idempotency. A document store shapes nested records around how they are
read and updated. These systems reduce friction for particular workloads, but
document identity, atomicity, freshness, and authorization remain explicit
responsibilities.”

**Animation state**

`state: access-pattern-routing` — route exact-key requests to the key-value
path, nested-record requests to the document path, and state-changing requests
through the appropriate write boundary. A “similar record” route remains
disabled.

**Checkpoint question**

“If the application knows the key or needs current document state, why would it
replace that exact access path with nearest-neighbor similarity?”

**Source IDs**

`[S10] [S11] [S12]`

**Confidence / caveats**

**High.** These are primary roles and common access patterns, not a claim that
all products expose identical consistency or transaction semantics. A document
store can also host search features; that does not make identity or state
semantic.

## Scene 4 — Feature vectors: turning an object into coordinates

**Visual direction**

Show three objects—an image, a product description, and a sensor window—each
passing through a feature-extraction panel. The outputs become coordinate
vectors such as `[0.2, 0.8, ...]`; plot a small 2-D projection where nearby
points share a visible feature. Label the axes `feature 1` and `feature 2`, not
“meaning.”

**Narration**

“A vector is a representation: a fixed-length list of numbers that makes some
properties available to computation. Early and classical systems used designed
or learned feature vectors for tasks such as ranking, classification, and
similarity. The useful geometry comes from how features are chosen and how
distance is defined. A vector is not the object, and its coordinates are not
universally meaningful on their own.”

**Animation state**

`state: feature-space` — objects become points; the camera briefly zooms out to
show clusters, then returns to the original objects and their source IDs.
Preserve the mapping `object ID ↔ vector`; never replace the source object with
the point.

**Checkpoint question**

“What determines whether two points being close is useful: the vector alone, or
the features, task, metric, and data that produced it?”

**Source IDs**

`[F1] [F2] [A1]`

**Confidence / caveats**

**High for the representation concept; medium for any broad historical story.**
F1 and F2 document particular word-vector methods, not every feature pipeline or
modern embedding. A 2-D projection is illustrative and can hide structure in
the original dimensions.

## Scene 5 — Embeddings: learned geometry for queries and items

**Visual direction**

Replace the hand-built feature panel with an embedding model. Feed in
“how do I get my money back?” and “refund policy” through the same model (or
compatible query/document encoders), then place their vectors near each other.
Show a different model producing a different arrangement. Put a clear label on
the model: `model + data + task → vector space`.

**Narration**

“An embedding model learns to encode useful relationships as numbers. Sentence
embeddings can put paraphrases near one another even when their words differ.
The model—not the database—creates the representation, and the training
objective, data, preprocessing, normalization, dimension, and metric all shape
what ‘near’ means. The database stores and searches the resulting space; it does
not create meaning independently.”

**Animation state**

`state: learned-representation` — animate query and corpus items through the
model, then draw their vectors and a similarity function. Swap the model label
to show neighborhoods changing while source IDs remain stable.

**Checkpoint question**

“If the embedding model changes, can the old and new vectors be assumed to share
the same neighborhoods without evaluation and migration?”

**Source IDs**

`[F3] [F4] [S4]`

**Confidence / caveats**

**High for the cited sentence-embedding results; medium for generalization.**
Sentence-BERT supports efficient comparison in its evaluated settings, but no
embedding model guarantees semantic relevance for every domain, language,
modality, or query distribution.

## Scene 6 — Exact nearest-neighbor search: the honest baseline

**Visual direction**

Show a query point entering a small vector collection. Draw a distance line from
the query to every stored vector, compute each distance, sort the list, and
highlight the true top-*k*. Keep the whole corpus visible and count every
comparison. Beside the result, display `exact = all candidates evaluated`.

**Narration**

“Nearest-neighbor search asks for the stored vectors closest to a query under a
chosen distance or similarity function. Exact search evaluates the query against
the corpus and returns the true top-*k* for that metric. It is conceptually
simple and provides the reference point for recall, even if a full scan becomes
too expensive as the corpus or query rate grows.”

**Animation state**

`state: exact-knn` — all points are inspected; the sorted candidate list is
stable and marked `ground truth for this metric and corpus`. Add a small side
counter for comparisons and latency.

**Checkpoint question**

“Before introducing an approximate index, what result and metric should be used
as the recall baseline?”

**Source IDs**

`[A1] [A4] [S1]`

**Confidence / caveats**

**High.** Exactness is always relative to the chosen vectors, metric, corpus,
and preprocessing. The nearest item is a candidate under that representation,
not automatically the correct answer in the application.

## Scene 7 — ANN indexes: reducing work by accepting a trade-off

**Visual direction**

Start from the exact-search scan, then fade most distance lines. Build a layered
proximity graph over the points: a query enters at a sparse upper layer, follows
short hops, and descends to a denser layer. In a second beat, show compressed
vector blocks labeled `memory ↓` with a small `recall ↔` dial. Display a persistent
caption: `approximate ≠ exact`.

**Narration**

“Approximate nearest-neighbor indexes reduce search work by organizing or
compressing the vector space. HNSW navigates layered proximity graphs; product
quantization compresses vectors; other implementations make other choices. The
benefit is a tunable trade-off among recall, latency, memory, build cost, and
update behavior. ANN is not automatically faster or equally accurate for every
workload.”

**Animation state**

`state: ann-search` — show a route through an index rather than a full scan.
Expose controls for `search effort`, `recall`, and `memory`; moving one control
changes the illustrative result and highlights that the true neighbor may be
missed.

**Checkpoint question**

“Which measured trade-off matters for this workload, and what exact-search
baseline will reveal the recall loss?”

**Source IDs**

`[A1] [A2] [A3] [A4] [S1] [S2] [S3]`

**Confidence / caveats**

**High for the algorithmic trade-offs; medium for any performance comparison.**
HNSW and product quantization are important techniques, not universal product
implementations. Latency and recall depend on corpus, dimension, hardware,
parameters, filters, updates, and query distribution.

## Scene 8 — The vector database: a production derived retrieval system

**Visual direction**

Reveal the production pipeline around the ANN index. A canonical document or
entity is written to a source-of-truth store, then an ingestion worker creates a
versioned embedding record containing `source_id`, `source_version`, `model`,
`dimension`, `metadata`, timestamps, and deletion state. The vector index
returns IDs and scores; a second arrow hydrates the authoritative records.
Animate an update and delete event moving through the pipeline with a visible
source-to-index lag indicator.

**Narration**

“A vector database is more than a file of coordinates: it is a production
retrieval component around vector storage, indexing, metadata, updates, and
queries. Its useful state is usually derived from canonical records. The
embedding pipeline and index make semantic candidates available, while the
source of truth preserves identity, current state, audit history, deletion, and
authorization. A similarity score is a ranking signal, not a probability or
proof.”

**Animation state**

`state: derived-vector-projection` — canonical data remains the thick, solid
line; ingestion and reindexing are dashed derived paths. Show `fresh`, `lagging`,
and `rebuilding` states, plus model/index version labels on every vector record.

**Checkpoint question**

“If a vector record is stale, duplicated, unauthorized, or deleted at the
source, which system must resolve the truth before the result is shown or used?”

**Source IDs**

`[A3] [A4] [S1] [S3] [S4]`

**Confidence / caveats**

**High for the derived-retrieval architecture; medium for the product boundary.**
The source audit describes a common operational role, not a formal industry
standard. APIs, consistency, filtering, index families, and update guarantees
vary; a vector database does not supply meaning without its model.

## Scene 9 — Application value: candidates become useful work

**Visual direction**

Fan one vector-retrieval result into three application lanes. In semantic search,
show a paraphrased question finding a relevant passage. In RAG, pass retrieved
chunks through provenance and citation checks before a generator. In
recommendations, pass item candidates to a ranker, then through eligibility,
diversity, and freshness rules. Optionally flash a text-to-image query sharing a
cross-modal space. Keep a bright label over all lanes: `candidate generation`.

**Narration**

“The application value is recall of useful candidates when the query is semantic,
paraphrased, multimodal, or too large for exhaustive comparison. Retrieved
passages can give a generator external context; similar items can seed a
recommender; related cases can help an analyst. In each case, later stages still
verify, rank, filter, explain, or act. Retrieval helps a system find possibilities;
it does not make a passage true, a recommendation eligible, or an action safe.”

**Animation state**

`state: retrieval-to-decision` — `query → embeddings → top-k candidates →
second stage → application output`. Let a distractor candidate enter the first
stage, then be rejected by provenance, ranking, or policy to make the boundary
visible.

**Checkpoint question**

“What must happen after candidate retrieval before the system can answer, rank,
display, or act?”

**Source IDs**

`[R1] [R2] [R3] [R4] [R5] [S20] [S23] [S25] [S26]`

**Confidence / caveats**

**High for the staged retrieval patterns; medium for application outcomes.**
The cited papers support evaluated retrieval or architecture patterns, not a
guarantee of factuality, recommendation utility, citation correctness, or model
use of every retrieved item.

## Scene 10 — Anti-patterns: similarity is not every database guarantee

**Visual direction**

Show a decision board with requests arriving at a vector index: `account 123`,
`commit transfer`, `JOIN invoices`, `is this user allowed?`, `current balance`,
and `probability of fraud`. Route each request to a red “wrong primitive” card
when it is delegated to similarity, then reroute it to exact, transactional,
relational, policy, current-state, feature-store, or model-serving components.
Leave semantic candidate generation green.

**Narration**

“The most expensive mistake is treating nearest-neighbor distance as a universal
database primitive. Do not embed exact keys, numbers, or transaction workflows.
Do not use a top-*k* list as an aggregate, a current-state read, an authorization
decision, a probability, or an anomaly detector. Filtering and similarity can
help narrow candidates, but the authoritative system and the evaluated second
stage must enforce the contract.”

**Animation state**

`state: workload-router` — each request receives a contract label: `exact`,
`transactional`, `relational`, `policy`, `current`, `model`, or `semantic`. Only
the semantic route enters ANN; mixed requests split into multiple paths.

**Checkpoint question**

“Is the requested output a candidate list, an exact fact, a current value, an
aggregate, a permission decision, a probability, or an action?”

**Source IDs**

`[S5] [S6] [S7] [S8] [S12] [S16] [S17] [S18] [S19] [S28]`

**Confidence / caveats**

**High for the separation of system roles.** A vector index can be useful as a
candidate or feature source in several of these workloads, but distance depends
on model, metric, corpus, normalization, and index settings; it is not an
automatic probability, policy result, or calibrated anomaly score.

## Scene 11 — Hybrid architecture: compose guarantees instead of replacing them

**Visual direction**

Assemble a layered architecture from left to right:

```text
canonical source ──┬─> exact / SQL / graph / document access
                   ├─> inverted index for terms and phrases
                   └─> embedding pipeline ─> ANN vector index
                                             │
query ─> exact + metadata + ACL filters ─> over-retrieve
                                             │
                                  lexical+dense reranker
                                             │
                              source hydration + final policy check
```

Animate a query with a rare identifier and a paraphrase. The lexical branch
finds the identifier, the dense branch finds the paraphrase, filters narrow the
eligible set, and the reranker combines candidates. End with the canonical
record and provenance attached to the response.

**Narration**

“The mature design is usually hybrid: keep structured truth in its source,
preserve lexical and exact signals, add dense retrieval for semantic recall, and
make authorization and metadata constraints part of the query and final check.
For small corpora, exact search may be simpler. At larger scale, ANN can produce
a broad candidate set, after which a reranker, business rule, model, or source
lookup decides what is useful and allowed.”

**Animation state**

`state: hybrid-retrieval` — parallel branches converge at `eligible candidates`,
then pass through `rerank → hydrate → authorize → respond`. Display evaluation
badges for recall, exactness, freshness, authorization, and end-to-end quality.

**Checkpoint question**

“Which signal supplies semantic recall, and which layer supplies exactness,
freshness, authorization, provenance, and the final decision?”

**Source IDs**

`[S1] [S5] [S6] [S8] [S9] [S10] [S11] [S12] [S13] [S16] [S20] [S21]`

**Confidence / caveats**

**High as an architecture pattern; medium for implementation-specific behavior.**
Prefiltering, over-retrieval, reranking, and post-retrieval authorization must
be tested together. Filtering a small top-*k* after retrieval can remove every
eligible result; metadata or namespace conventions alone are not a complete
security model.

## Scene 12 — Optional coda: Pinecone as one documented implementation

**Visual direction**

Only after the conceptual arc is complete, place a small label, `Pinecone — one
product example`, beside the generic hybrid diagram. Animate its documented
workflow: extract and chunk source files, embed with an integrated or external
model, upsert vectors with IDs and metadata, query for top-*k*, and apply metadata
filters. Show dense, sparse, and hybrid search as product options, not as the
definition of vector databases. Keep the canonical files and application policy
outside the product box.

**Narration**

“Pinecone is an optional concrete example of the production role just described.
Its documentation shows flows for dense and sparse vectors, integrated or
bring-your-own embeddings, IDs, metadata, namespaces, filtering, and hybrid
search. Those are documented product capabilities, not the conceptual definition
of a vector database and not evidence that one implementation is universally
faster, more accurate, or safer. The architecture still needs a canonical source,
versioned ingestion, evaluation, and application-level authorization.”

**Animation state**

`state: product-mapping` — map generic concepts to product API boxes without
changing the previous guarantees: `embedding choice`, `index`, `metadata
filter`, and `top_k` remain explicit. End on the question, “Which parts are
general architecture, and which parts are this product’s current API?”

**Checkpoint question**

“When adopting a product, which claims require its current documentation and
your own workload benchmark rather than a generic vector-database assumption?”

**Source IDs**

`[P1] [P2] [P3] [P4] [P5] [P6] [P7]`

**Confidence / caveats**

**High for the documented Pinecone flows; product-specific and time-sensitive.**
The source audit does not establish Pinecone’s internal ANN algorithm, recall,
latency, uptime, cost, or scale from these API pages. Product behavior and
limits can change, and namespaces or metadata filters should not be presented as
a universal security guarantee.
