---
title: "Changelog"
description: "Release history for Semantica. All notable changes by version."
---

<Note>
  The latest stable release is **v0.5.0**. Changes listed under **Unreleased** are merged to `main` but not yet published to PyPI.
</Note>

---

## Unreleased

### Added

- **Public API Ingestion** — `PublicAPIIngestor` for credential-free REST endpoints; 6 pre-configured examples (`jsonplaceholder`, `rest_countries_all`, `data_gov_datasets`, `open_meteo_forecast`); JSON/CSV/XML auto-detection; `batch_public_apis()`; `ingest(..., source_type="public_api")`; 21 tests

### Fixed

- **Public API XML XXE hardening** — `defusedxml` replaces stdlib XML parser; lxml fallback with `resolve_entities=False`
- **`validate_no_auth` string coercion** — `bool("false")` returned `True`; replaced with `_coerce_bool()` mapping `"false"/"0"/"no"/"off"` → `False`
- **Auth detection in URL query strings** — `detect_public_api()` now scans endpoint URLs for auth params via `urllib.parse.parse_qs`
- **NERExtractor LLM silent fallback** (#554) — fixed silent exception swallowing, `response_format=json_object` sent to incompatible gateways, and absent fallback in `generate_typed` repair loop; 17 regression tests

### Security

- GitHub Actions workflow permissions hardened (`permissions: contents: read` + `security-events: write`)
- DOMPurify upgraded to 3.4.0+ — fixes 6 Dependabot alerts including prototype pollution → XSS and mutation-XSS bypasses
- `uuid` upgraded to 13.0.1+ — fixes buffer bounds check in `v3`/`v5`/`v6` APIs (CVE-2026-41907)
- Vite upgraded to 6.4.3 — resolves path traversal (CVE-2026-39365) and esbuild CORS issue
- Leaked Groq API keys removed from 10 cookbook notebooks — revoke affected keys in the Groq console

---

## v0.5.0 — May 11, 2026

```bash
pip install semantica==0.5.0
```

### Added

**Ontology Hub** — Full ontology lifecycle in the browser: visual class/property editor, SHACL Studio with shape generation (permissive/standard/strict), Alignments tab with suggestion scoring, Health Dashboard with per-ontology quality scoring, Versions & Proposals review workflow, Entity Search panel, SKOS Vocabulary Manager. 16 backend endpoints under `/api/ontology`.

**Distance Intelligence** — Semantic neighborhoods, N×N distance matrices, ego-mode visualization with depth slider 1–8, distance band classification (direct/near/mid-range/distant), per-session embedding cache with revision-based invalidation. 57 new tests.

**Parquet Ingestion** — `ParquetIngestor` with PyArrow: single file, partitioned directories, Hive-style discovery, selective column reading. 32 tests.

**Graph Explorer** — Landing page redesign, bidirectional path finding (`directed=false`), indexed search (0.004ms on 118k nodes via purpose-built inverted index + LRU cache), `PathResponse` with `hop_count` and `distance_band`.

**DuplicateDetector result controls** — `max_results`, `top_k_per_entity`, `min_similarity`, `sort_by` with construction-time validation; 15 new tests.

### Fixed

- `ConflictDetector.detect_conflicts()` duplicate definition — merged dispatcher into single method with `method` param support
- `semantica[all]` fails on Windows — removed `faiss-gpu` from `[all]` extra
- `UnicodeEncodeError` on Windows cp1252 — 5 `sys.stdout.write()` calls in progress display replaced with `_safe_write()`
- Circular import in `semantic_extract` — shared types extracted to `types.py`; `TripleExtractor` alias added
- Lazy-load optional ingest backends — `except ImportError` narrowed to `except ModuleNotFoundError`
- OWLExporter Turtle syntax — invalid multi-block output fixed; 43 tests added

### Security

12 vulnerability fixes including eval injection (CWE-95), pickle deserialization (CWE-502), SQL injection (CWE-89), XXE (CWE-611), missing security headers, overpermissive CORS, prompt injection (CWE-1336), dynamic `__import__` (CWE-95), ReDoS (CWE-1333), path traversal (CWE-22), unbounded SPARQL (CWE-400). SSRF in Ontology Hub URL fetch blocked via `socket.getaddrinfo` loopback/private address rejection.

---

## v0.4.0 — April 8, 2026

```bash
pip install semantica==0.4.0
```

### Added

**Temporal Intelligence** — Bi-temporal data model (`BiTemporalFact`, `TemporalBound`), point-in-time query engine (`TemporalGraphQuery.reconstruct_at_time()`), full Allen interval algebra (all 13 relations), `TemporalNormalizer` (zero LLM calls, pure regex + dateutil), `TemporalQueryRewriter` for natural-language temporal intent extraction, OWL-Time export, `ContextGraph.state_at(timestamp)` snapshots.

**Knowledge Explorer API** — Full FastAPI backend with graph, analytics, decisions, temporal, enrichment, and export/import routes; 12 export formats; WebSocket progress; thread-safe `RLock` sessions; audit trail and rollback protection; 99 integration tests. `pip install semantica[explorer]`

**Ontology** — SHACL generation/validation (basic/standard/strict tiers) with plain-English explanations; SKOS vocabulary module; Ontology Alignment API (`create_alignment()`, `suggest_alignments()`); Ontology Diff & Migration (`diff_ontologies()`, CRITICAL/HIGH/MEDIUM/INFO impact classification).

**Agno Integration** — 5 components: `AgnoContextStore` (graph-backed memory), `AgnoKnowledgeGraph` (multi-hop GraphRAG), `AgnoDecisionKit` (6 tools), `AgnoKGToolkit` (7 tools), `AgnoSharedContext` (team coordinator). 110 tests; 3 cookbook notebooks. `pip install semantica[agno]`

**Datalog Reasoning** — Pure-Python bottom-up semi-naive fixpoint engine; recursive Horn clause rules with guaranteed termination.

**Novita AI Provider** — OpenAI-compatible provider for 200+ open-weight models. `NOVITA_API_KEY`.

### Fixed

- Pattern Matcher: dead code silently overwrote `_match_pattern` regex with `re.escape`, breaking transitivity/symmetry rules
- OllamaProvider `base_url` ignored — `ollama.Client(host=self.base_url)` fix by @AlexeyMyslin
- `find_path` always used BFS regardless of algorithm param
- `ChangeCategory` enum typo `"potenitally_breaking"` → `"potentially_breaking"`

### Security

- CWE-312/359/532: removed `api_key` debug `print` blocks from extractors
- SHACL path traversal: replaced length-heuristic with `os.path.exists()`
- SPARQL injection in `search_concepts`, `list_alignments`, `build_values_clause`

---

## v0.3.0 — March 10, 2026

```bash
pip install semantica==0.3.0
```

### Added

- `ContextNode`/`ContextEdge` gain `valid_from`/`valid_until` with `is_active(at_time)`
- `ContextGraph.find_active_nodes(node_type, at_time)` — temporal node filtering
- `get_neighbors(min_weight)` — confidence-filtered BFS
- `link_graph()`, `navigate_to()`, `resolve_links()`, `cross_graph_path()` — cross-graph navigation

### Fixed

- `is_active()` tz-aware/naive datetime normalization
- `valid_from`/`valid_until` serialization in `to_dict()`/`from_dict()`
- Cross-graph link phantom-node prevention
- `ProvenanceTracker` added to `semantica/kg/__init__.py` exports

---

## v0.3.0-beta — March 7, 2026

### Added

- Multi-founder LLM extraction: unmatched subjects/objects produce `UNKNOWN` entity; `_match_pattern` rewritten with pre-bound variable resolution
- TTL export aliases: `"ttl"/"nt"/"xml"/"rdf"/"json-ld"` resolve correctly
- Incremental/delta processing: native delta computation via SPARQL, `delta_mode`, `prune_versions()`
- Deduplication v2: multi-key/phonetic blocking (63.6% faster), two-stage scoring prefilter (18–25% faster), semantic relationship deduplication (6.98× speedup)
- ArangoDB AQL Export with batch processing — 17 tests (by @tibisabau)
- Apache Parquet Export with configurable compression — 25 tests (by @tibisabau)

---

## v0.3.0-alpha — February 19, 2026

### Added

- **Decision Tracking System** — complete lifecycle: `record_decision()` → `add_causal_relationship()` → `find_similar_decisions()` → `trace_decision_chain()` → `analyze_decision_impact()` → `check_decision_rules()` → `get_decision_insights()`
- **Advanced KG Algorithms** — Node2Vec embeddings, betweenness/closeness/eigenvector centrality, Louvain community detection
- **PgVector Store** — HNSW/IVFFlat indexing, JSONB metadata filtering, SQL injection protection; 36+ tests
- **Apache AGE Backend** — `AgeStore` with `GraphStore` API compatibility
- **ResourceScheduler Deadlock Fix** — `threading.Lock` → `threading.RLock`; 6 regression tests

---

## v0.2.7 — February 9, 2026

```bash
pip install semantica==0.2.7
```

### Added

- **Snowflake Connector** — multi-auth (password/OAuth/key-pair/SSO), SQL injection prevention; 24 tests. `pip install semantica[db-snowflake]`
- **Apache Arrow Export** — explicit Arrow schemas, Pandas/DuckDB compatible; 20 tests
- **Benchmark Suite** — 137+ benchmarks across all 10 modules, Z-score regression detection, GitHub Actions workflow

---

## v0.2.6 — February 3, 2026

```bash
pip install semantica==0.2.6
```

### Added

- **W3C PROV-O Provenance Tracking** — comprehensive lineage across all 17 modules; InMemory/SQLite backends; SHA-256 integrity; FDA 21 CFR Part 11, SOX, HIPAA compliance; 237 tests
- **Enhanced Change Management** — `TemporalVersionManager`/`OntologyVersionManager`; SHA-256 checksums; 104 tests; 17.6ms for 10k entities
- **CSV Ingestion Enhancements** — auto-detect encoding (chardet) and delimiter (csv.Sniffer)

### Fixed

- `temperature=None` now omits the parameter so APIs use model defaults (by @F0rt1s @IGES-Institut)
- `JenaStore` empty graph: `if self.graph is None:` replaces implicit falsy check in 5 methods

---

## v0.2.5 — January 27, 2026

```bash
pip install semantica==0.2.5
```

### Added

- **Pinecone Vector Store** — serverless and pod-based indexes, namespace support, metadata filtering
- **Configurable LLM Retry Logic** — `max_retries` parameter (default 3) in all extractors
- **Bring Your Own Model (BYOM)** — custom HuggingFace models; custom tokenizer; runtime `model=` overrides
- Enhanced NER: IOB/BILOU parsing, configurable aggregation strategies, confidence scoring
- Relation Extraction: entity marker technique for sequence classification models
- Triplet Extraction: Seq2Seq model support (REBEL)

---

## v0.2.4 — January 22, 2026

```bash
pip install semantica==0.2.4
```

### Added

- **Ontology Ingestion Module** — `OntologyIngestor` for Turtle/RDF-XML/JSON-LD/N3; `ingest(source_type="ontology")`

---

## v0.2.3 — January 20, 2026

```bash
pip install semantica==0.2.3
```

### Added

- Amazon Neptune dev environment — CloudFormation template
- `VectorStore.add_documents()` with batching and parallel processing (`max_workers=6`)

### Fixed

- LLM relation extraction parsing — normalized typed responses; structured JSON fallback
- Pipeline circular import (Issues #192 #193) — lazy-loaded `PipelineValidator`
- JupyterLab progress (Issue #181) — `SEMANTICA_DISABLE_JUPYTER_PROGRESS` env var

---

## v0.2.2 — January 15, 2026

```bash
pip install semantica==0.2.2
```

### Added

- **Parallel Extraction Engine** — `ThreadPoolExecutor` across all extractors; ~1.89× speedup; `max_workers` parameter

### Changed

- Gemini SDK migrated to `google-genai` with `google.generativeai` fallback
- Global `optimization.max_workers` default raised to 8

### Security

- Hardcoded API keys removed from 8 notebooks; `ExtractionCache` excludes auth keys from cache keys; cache hashing upgraded MD5 → SHA-256

---

## v0.2.1 — January 12, 2026

```bash
pip install semantica==0.2.1
```

### Fixed

- LLM output stability (Bug #176) — correct `max_tokens` propagation; automatic chunk-halving on context limit errors
- Increased default `max_text_length` to 64,000 characters for all providers
- Standardized Groq defaults: `llama-3.3-70b-versatile`, 64k context

---

## v0.2.0 — January 10, 2026

```bash
pip install semantica==0.2.0
```

### Added

- **Amazon Neptune Support** — `AmazonNeptuneStore` via Bolt/OpenCypher; AWS IAM SigV4 signing. `pip install semantica[graph-amazon-neptune]`
- **Docling Integration** — `DoclingParser` for PDF/DOCX/PPTX/XLSX/HTML/image; OCR; Markdown/HTML/JSON export
- **Robust Extraction Fallbacks** — ML/LLM → Pattern → Last Resort chains across all extractors
- Semantic Extract: auto-chunking for long text; `silent_fail` parameter; JSON parsing with exponential backoff

---

## v0.1.1 — January 5, 2026

```bash
pip install semantica==0.1.1
```

### Fixed

- `DoclingParser` import/export across platforms (Windows, Linux, Google Colab)
- Error messaging when optional `docling` dependency is missing

---

## v0.1.0 — December 31, 2025

```bash
pip install semantica==0.1.0
```

### Added

- Command-line interface (`semantica` CLI) with knowledge base building and info commands
- FastAPI-based REST API server
- Background worker for scalable task processing
- Automated release workflow with Trusted Publishing

---

## v0.0.3 — November 25, 2025

### Added

- Comprehensive issue templates, PR template, `SUPPORT.md`, `FUNDING.yml`
- 10+ domain-specific cookbook examples (Finance, Healthcare, Cybersecurity, etc.)

---

## v0.0.1 — January 2024

Initial release: universal data ingestion, NER/relation extraction, knowledge graph construction, 6-stage ontology pipeline, GraphRAG engine, multi-agent infrastructure, vector/graph store backends, temporal KG support, conflict detection, deduplication, multi-format export, visualization, streaming support.
