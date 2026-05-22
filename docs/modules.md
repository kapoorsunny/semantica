---
title: "Modules"
description: "Every Semantica module works independently — use only what you need."
icon: "puzzle-piece"
---

<Tip>
  Just need a quick reference? Jump to the [Module Index](#module-index) at the bottom of this page.
</Tip>

---

## Architecture Overview

Semantica is organized into **six logical layers**, each with specific responsibilities:

<CardGroup cols={3}>
  <Card title="Input Layer" icon="database">
    Data ingestion and preparation. **Modules:** Ingest, Parse, Split, Normalize
  </Card>
  <Card title="Core Processing" icon="microchip">
    Intelligence and understanding. **Modules:** Semantic Extract, KG, Ontology, Reasoning
  </Card>
  <Card title="Storage" icon="hard-drive">
    Persistent data storage. **Modules:** Embeddings, Vector Store, Graph Store, Triplet Store
  </Card>
  <Card title="Quality Assurance" icon="check-circle">
    Data quality and consistency. **Modules:** Deduplication, Conflicts
  </Card>
  <Card title="Context & Memory" icon="brain">
    Agent memory and decision tracking. **Modules:** Context, Provenance, Change Management
  </Card>
  <Card title="Output & Orchestration" icon="share-nodes">
    Export, visualization, and workflows. **Modules:** Export, Visualization, Pipeline
  </Card>
</CardGroup>

---

## Input Layer

### Ingest

Data ingestion from files, web, databases, and streams.

```python
from semantica.ingest import FileIngestor, WebIngestor, ParquetIngestor, XMLIngestor

# Files (PDF, DOCX, CSV, Excel, PPTX, JSON, HTML, archives)
ingestor = FileIngestor()
documents = ingestor.ingest_directory("data/")

# Web
web_ingestor = WebIngestor()
pages = web_ingestor.ingest_urls(["https://example.com"])

# Parquet — single file, partitioned directory, Hive-style (v0.5.0)
parquet = ParquetIngestor()
sources = parquet.ingest("data/events.parquet")

# XML with XSD/DTD validation, namespace handling (v0.5.0)
xml = XMLIngestor(validate_xsd="schema.xsd")
sources = xml.ingest("data/records/")
```

### Parse

Document parsing and text extraction.

```python
from semantica.parse import DocumentParser, DoclingParser

# Standard parser
parser = DocumentParser()
parsed = parser.parse_document("document.pdf")

# Advanced parser: multi-column PDFs, merged-cell tables, OCR
parser = DoclingParser(extract_tables=True, extract_images=True, output_format="markdown")
parsed = parser.parse("data/annual_report.pdf")
```

### Split

Text chunking and segmentation for embedding and RAG pipelines.

```python
from semantica.split import TextSplitter

splitter = TextSplitter(method="semantic")
chunks = splitter.split(text, chunk_size=1000, overlap=200)
```

Methods: `recursive`, `semantic`, `entity-aware`, `relation-aware`.

### Normalize

Data cleaning and standardization.

```python
from semantica.normalize import DataNormalizer

normalizer = DataNormalizer()
clean_text = normalizer.normalize_text(text)
standardized_date = normalizer.normalize_date("Jan 1st, 2020")
```

---

## Core Processing

### Semantic Extract

Named entity recognition, relation extraction, and triplet generation.

```python
from semantica.semantic_extract import NERExtractor, RelationExtractor, TripletExtractor

ner = NERExtractor(method="llm", llm_provider=llm)
entities = ner.extract("Apple Inc. was founded by Steve Jobs.")

rel = RelationExtractor(method="llm", llm_provider=llm)
relationships = rel.extract(text, entities=entities)

trip = TripletExtractor(method="llm", llm_provider=llm)
triplets = trip.extract(text)
```

Methods: `"pattern"`, `"ml"`, `"llm"`. LLM method supports all 8 providers.

### Knowledge Graph

Graph construction, algorithms, temporal model, and distance intelligence.

```python
from semantica.kg import GraphBuilder, GraphAnalyzer, TemporalKnowledgeGraph, DistanceCalculator

# Build
builder = GraphBuilder(merge_entities=True)
kg = builder.build(entities=entities, relationships=relationships)

# Temporal graphs (v0.4.0)
tkg = TemporalKnowledgeGraph()
tkg.add_node("ceo_role", valid_from=datetime(2020, 1, 1), valid_until=datetime(2023, 6, 1))
snapshot = tkg.at(datetime(2021, 6, 15))

# Distance Intelligence (v0.5.0)
calc = DistanceCalculator(kg)
neighborhood = calc.semantic_neighborhood("Apple Inc.", radius=0.4)
matrix = calc.distance_matrix(["Apple Inc.", "Google", "Microsoft"])
```

### Ontology

SHACL, SKOS, alignments, diff/migration, auto-generation, and OWL/RDF — plus the visual Ontology Hub (v0.5.0).

```python
from semantica.ontology import OntologyManager, SHACLGenerator

ontology = OntologyManager()
ontology.add_class("Person", ["name", "birth_date"])
ontology.add_relationship("works_for", "Person", "Organization")
is_valid = ontology.validate_graph(kg)

shacl = SHACLGenerator()
shapes = shacl.generate(ontology)
```

### Reasoning

Forward chaining, Rete, deductive, abductive, SPARQL, and Datalog reasoning.

```python
from semantica.reasoning import ReasoningEngine, DatalogEngine

# Rule-based reasoning
engine = ReasoningEngine()
inferences = engine.infer(kg, rules=["transitivity", "symmetry"])

# Datalog — recursive Horn clause rules (v0.4.0)
datalog = DatalogEngine()
datalog.add_rule("ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).")
results = datalog.query("ancestor(alice, ?)")
```

---

## Storage

### Embeddings

Vector embeddings and similarity computation.

```python
from semantica.embeddings import EmbeddingGenerator

generator = EmbeddingGenerator(model="sentence-transformers")
embeddings = generator.generate(["text1", "text2"])
similarity = generator.similarity(embeddings[0], embeddings[1])
```

Supported: Sentence-Transformers, FastEmbed, OpenAI, BGE.

### Vector Store

Multi-backend vector database management.

```python
from semantica.vector_store import VectorStore

store = VectorStore(backend="faiss", dimension=768)
store.add_vectors(embeddings, ids)
results = store.search(query_vector, top_k=10)
```

Backends: FAISS, Pinecone, Weaviate, Qdrant, Milvus, PgVector, in-memory.
Search modes: semantic top-k, hybrid (vector + keyword), metadata-filtered.

### Graph Store

Graph database integration.

```python
from semantica.graph_store import GraphStore

store = GraphStore(backend="neo4j")
store.add_nodes(entities)
store.add_edges(relationships)
results = store.query("MATCH (n)-[r]->(m) RETURN n, r, m")
```

Backends: Neo4j, FalkorDB, Apache AGE, Amazon Neptune.

### Triplet Store

RDF triple-based storage with SPARQL.

```python
from semantica.triplet_store import TripletStore

store = TripletStore(backend="blazegraph")
store.add_triplets(subject, predicate, obj)
results = store.sparql("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
```

Backends: Blazegraph, Apache Jena, RDF4J.

---

## Quality Assurance

### Deduplication

Entity deduplication v1/v2, similarity scoring, and merging.

```python
from semantica.deduplication import EntityResolver

resolver = EntityResolver()
merged = resolver.resolve(entities, strategy="semantic_v2")
```

v2 strategies (`blocking_v2`, `hybrid_v2`, `semantic_v2`) are up to 7x faster than v1. `DuplicateDetector` supports `max_results`, `top_k_per_entity`, `min_similarity`, and `sort_by` for fine-grained control.

### Conflicts

Multi-source conflict detection and resolution.

```python
from semantica.conflicts import ConflictDetector

detector = ConflictDetector()
conflicts = detector.detect_conflicts(kg)
resolved = detector.resolve(conflicts, strategy="most_recent")
```

Detection types: value, type, temporal, and logical conflicts.

---

## Context & Memory

### Context

Agent context graphs, decision tracking, causal chains, and precedent search.

```python
from semantica.context import AgentContext, ContextGraph

context = AgentContext(
    vector_store=VectorStore(backend="faiss", dimension=768),
    knowledge_graph=ContextGraph(advanced_analytics=True),
    decision_tracking=True,
)

context.store("GPT-4 outperforms GPT-3.5 on reasoning benchmarks by 40%")
decision_id = context.record_decision(
    category="model_selection", scenario="...", reasoning="...", outcome="...", confidence=0.9
)
precedents = context.find_precedents("model selection", limit=5)
```

### Provenance

W3C PROV-O compliant lineage tracking across all 17 modules.

```python
from semantica.provenance import ProvenanceManager

manager = ProvenanceManager()
manager.track_entity("entity_1", "document.pdf", "person")
lineage = manager.get_lineage("entity_1")
```

### Change Management

Version storage, change tracking, SHA-256 checksums, and audit trails.

```python
from semantica.change_management import TemporalVersionManager

manager = TemporalVersionManager(storage_path="versions.db")
snapshot = manager.create_snapshot(kg, "v1.0", "user@example.com", "Initial version")
diff = manager.diff("v1.0", "v1.1")
```

---

## Output & Orchestration

### Export

RDF (Turtle, JSON-LD, N-Triples, XML), Parquet, ArangoDB AQL, CSV, OWL ontologies.

```python
from semantica.export import RDFExporter

exporter = RDFExporter()
rdf = exporter.export_to_rdf(graph, format="turtle")
```

### Visualization

Interactive and static KG, ontology, embedding, and temporal visualization.

```python
from semantica.visualization import GraphVisualizer

viz = GraphVisualizer()
viz.visualize(graph, output="graph.html")
```

### Pipeline

Pipeline DSL with parallel workers, retry policies, and failure handling.

```python
from semantica.pipeline import Pipeline

pipeline = Pipeline()
pipeline.add_step("ingest", FileIngestor())
pipeline.add_step("extract", NERExtractor())
pipeline.add_step("build", GraphBuilder())
result = pipeline.run("data/")
```

### Explorer (v0.4.0/v0.5.0)

FastAPI Knowledge Explorer + Ontology Hub with WebSocket progress, thread-safe sessions, bidirectional path finding, and indexed search.

```python
from semantica.explorer import start_explorer

start_explorer(graph=kg, port=8080)
# Opens at http://localhost:8080
```

---

## Common Module Chains

| Goal | Modules |
|------|---------|
| Document processing | Ingest → Parse → Split → Semantic Extract → KG |
| Web scraping | Ingest (Web) → Normalize → Semantic Extract → Graph Store |
| GraphRAG | KG + Vector Store → Context → Reasoning → Export |
| AI agents | Context → LLM Providers → Reasoning → Export |
| Temporal analysis | KG (Temporal) → Context → Change Management → Export |
| Compliance pipeline | Ingest → Semantic Extract → KG → Provenance → Export |

---

## Module Index

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| [ingest](reference/ingest) | Data ingestion | `FileIngestor`, `WebIngestor`, `ParquetIngestor`, `XMLIngestor` |
| [parse](reference/parse) | Document parsing | `DocumentParser`, `DoclingParser` |
| [split](reference/split) | Text chunking | `TextSplitter` |
| [normalize](reference/normalize) | Data cleaning | `DataNormalizer` |
| [semantic_extract](reference/semantic_extract) | NER & relation extraction | `NERExtractor`, `RelationExtractor`, `TripletExtractor` |
| [kg](reference/kg) | Graph construction | `GraphBuilder`, `TemporalKnowledgeGraph`, `DistanceCalculator` |
| [ontology](reference/ontology) | Schema management | `OntologyManager`, `SHACLGenerator` |
| [reasoning](reference/reasoning) | Logical inference | `ReasoningEngine`, `DatalogEngine` |
| [embeddings](reference/embeddings) | Vector embeddings | `EmbeddingGenerator` |
| [vector_store](reference/vector_store) | Vector database | `VectorStore` |
| [graph_store](reference/graph_store) | Graph database | `GraphStore` |
| [triplet_store](reference/triplet_store) | RDF triple store | `TripletStore` |
| [deduplication](reference/deduplication) | Entity resolution | `EntityResolver`, `DuplicateDetector` |
| [conflicts](reference/conflicts) | Conflict resolution | `ConflictDetector` |
| [context](reference/context) | Agent context & decisions | `AgentContext`, `ContextGraph` |
| [provenance](reference/provenance) | W3C PROV-O lineage | `ProvenanceManager` |
| [change_management](reference/change_management) | Version control | `TemporalVersionManager` |
| [export](reference/export) | Data export | `RDFExporter` |
| [visualization](reference/visualization) | Graph visualization | `GraphVisualizer` |
| [pipeline](reference/pipeline) | Workflow orchestration | `Pipeline` |
| [explorer](reference/evals) | Knowledge Explorer UI | `start_explorer` |
| [llms](reference/llms) | LLM providers | `Groq`, `OpenAI`, `Anthropic`, `create_provider` |
| [seed](reference/seed) | Foundation data | `SeedData` |

---

## More

<CardGroup cols={2}>
  <Card title="Getting Started" icon="rocket" href="getting-started">
    Your first knowledge graph in 5 minutes.
  </Card>
  <Card title="Cookbook" icon="flask" href="cookbook">
    40+ domain notebooks with real-world examples.
  </Card>
  <Card title="API Reference" icon="code" href="reference/context">
    Full technical documentation.
  </Card>
  <Card title="Use Cases" icon="briefcase" href="use-cases">
    Domain-specific examples.
  </Card>
</CardGroup>
