---
title: "Deep Dive"
description: "Internals, advanced concepts, and extension points for contributors and power users."
icon: "microscope"
---

> Internals, advanced concepts, and extension points for contributors and power users.

<Tip>
New to Semantica? Read the [Architecture](architecture) overview first for a higher-level picture.
</Tip>

---

## Pipeline Internals

Full data flow through a Semantica pipeline:

```text
Data Sources
    └─ Ingestion Layer      (FileIngestor, WebIngestor, SnowflakeIngestor, StreamIngestor)
        └─ Parsing Layer    (DocumentParser, DoclingParser, OCR)
            └─ Extraction   (NER → Entity Linking → Validation)
                └─ Normalization
                    └─ Conflict Resolution
                        └─ Knowledge Graph Builder
                            └─ Embedding Generator
                                └─ Export Layer
```

---

## System Components

### Ingestion Layer

- **FileIngestor** — PDF, DOCX, HTML, JSON, CSV, TXT, Parquet (v0.5.0), XML (v0.5.0), archives
- **WebIngestor** — URL crawling and scraping
- **SnowflakeIngestor** — SQL databases and cloud warehouses
- **StreamIngestor** — Kafka and real-time feeds

### Parsing Layer

- Text and metadata extraction from documents
- OCR for scanned content
- Layout analysis via Docling (tables, columns, headers)

### Extraction Layer

```text
text → Tokenization → NER → Entity Linking → Entity Validation
```

Components: Named Entity Recognition, Relationship Extraction, Triplet Extraction, Coreference Resolution.

### Normalization Layer

Standardizes entity names, date formats, numbers, encodings, and language. Includes the v0.5.0 cp1252 encoding fix for Windows environments.

### Conflict Resolution

Multiple source facts that contradict each other are resolved using one of four strategies:

| Strategy | Behavior |
|----------|----------|
| `voting` | Most common value wins |
| `credibility_weighted` | Higher-credibility source wins |
| `most_recent` | Latest timestamp wins |
| `highest_confidence` | Highest extraction confidence wins |

### Knowledge Graph Builder

- Entity resolution across sources
- Edge creation with typed relationships
- Property assignment with confidence scores
- Graph validation and quality checks

### Embedding Generator

- Text embeddings: Sentence-Transformers, FastEmbed, OpenAI, BGE
- Graph embeddings: Node2Vec, GraphSAGE
- Distance caching for Distance Intelligence (v0.5.0)

---

## Advanced Concepts

### Entity Resolution

```python
def resolve_entities(entities, threshold=0.85):
    clusters = []
    for entity in entities:
        matched = False
        for cluster in clusters:
            if similarity(entity, cluster.representative) > threshold:
                cluster.add(entity)
                matched = True
                break
        if not matched:
            clusters.append(EntityCluster(entity))
    return clusters
```

### Relationship Inference

Semantica's reasoning engines derive implicit relationships:

- **Transitive** — if A→B and B→C, infer A→C
- **Temporal** — before/after/during from timestamped facts (Allen Interval Algebra)
- **Causal** — IF/THEN rules via `Reasoner`
- **Hierarchical** — subclass/instance inference via `OntologyReasoner`
- **Datalog** — recursive rules with termination guarantee (v0.4.0)

### Batch Processing for Large Datasets

```python
def process_large_dataset(sources, batch_size=100):
    for i in range(0, len(sources), batch_size):
        batch = sources[i : i + batch_size]
        result = semantica.build_knowledge_base(batch)
        save_result(result)
        del result
        gc.collect()
```

---

## Extension Points

### Custom Plugin

```python
from semantica.core import Plugin

class CustomPlugin(Plugin):
    def initialize(self):
        ...

    def process(self, data):
        return processed_data
```

### Custom Extractor

```python
from semantica.semantic_extract import BaseExtractor

class DomainSpecificExtractor(BaseExtractor):
    def extract(self, text):
        # Domain-specific entity extraction logic
        return entities
```

### Custom Ingestor

```python
from semantica.ingest import BaseIngestor

class CustomIngestor(BaseIngestor):
    def ingest(self, source):
        # Load and return document dicts
        return documents
```

---

## Internal APIs

| API | Purpose |
|-----|---------|
| `Semantica.build_knowledge_base()` | Main orchestration entry point |
| `GraphBuilder.build()` | Graph construction |
| `ConflictResolver.resolve()` | Conflict resolution |
| `EmbeddingGenerator.generate()` | Embedding generation |

Extension hooks: plugin registration, custom extractor registration, custom exporter registration, event hooks.

---

## Design Decisions

**Why modular architecture?** Each component is independently testable and swappable. You can use `NERExtractor` alone without pulling in graph storage or pipelines.

**Why built-in conflict resolution?** Multi-source data always has contradictions. Ignoring them produces low-quality graphs. Explicit strategies give you control over data quality.

**Why W3C PROV-O for provenance?** It's an industry standard with broad tooling support. A custom format would make lineage data non-portable.

**Why multiple reasoning engines?** Different problems need different reasoning: forward chaining for rule application, SPARQL for graph queries, abductive for hypothesis generation, Datalog for recursive rules.

---

## See Also

<CardGroup cols={2}>
  <Card title="Modules" icon="cubes" href="modules">
    Every module with code examples.
  </Card>
  <Card title="Core Module" icon="gear" href="reference/core">
    Framework orchestration internals.
  </Card>
  <Card title="Pipeline" icon="arrows-turn-to-dots" href="reference/pipeline">
    Pipeline DSL and execution model.
  </Card>
  <Card title="Contributing" icon="code-pull-request" href="contributing">
    How to extend the framework.
  </Card>
</CardGroup>
