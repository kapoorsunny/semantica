---
title: "Examples"
description: "Code examples organized by complexity — beginner through production."
icon: "code"
---

> Code examples organized by complexity. For interactive notebooks, see the [Cookbook](cookbook).

---

## Beginner

### Basic Knowledge Graph

```python
from semantica.ingest import FileIngestor
from semantica.parse import DocumentParser
from semantica.semantic_extract import NERExtractor, RelationExtractor
from semantica.kg import GraphBuilder

ingestor = FileIngestor()
parser   = DocumentParser()
ner      = NERExtractor()
rel      = RelationExtractor()

sources  = ingestor.ingest("data/sample.pdf")
parsed   = parser.parse(sources[0])

entities      = ner.extract(parsed)
relationships = rel.extract(parsed, entities=entities)

kg = GraphBuilder(merge_entities=True).build(
    entities=entities, relationships=relationships
)
print(f"{len(kg.nodes)} nodes, {len(kg.edges)} edges")
```

### Entity Extraction from Text

```python
from semantica.semantic_extract import NERExtractor

ner      = NERExtractor()
entities = ner.extract("Apple Inc. was founded by Steve Jobs in 1976.")

for entity in entities:
    print(f"{entity['text']}: {entity['type']}")
# Apple Inc.: ORGANIZATION
# Steve Jobs: PERSON
# 1976: DATE
```

### Custom NER with LLM

```python
from semantica.semantic_extract import NERExtractor
from semantica.llms import OpenAI

llm = OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
ner = NERExtractor(method="llm", llm_provider=llm, confidence_threshold=0.8)
entities = ner.extract("Your document text here...")
```

---

## Intermediate

### Multi-Source Integration

```python
from semantica.ingest import FileIngestor
from semantica.parse import DocumentParser
from semantica.semantic_extract import NERExtractor, RelationExtractor
from semantica.kg import GraphBuilder

ingestor = FileIngestor()
parser   = DocumentParser()
ner      = NERExtractor()
rel      = RelationExtractor()
builder  = GraphBuilder(merge_entities=True)

all_entities, all_rels = [], []

for path in ["source1.pdf", "source2.pdf", "source3.pdf"]:
    sources = ingestor.ingest(path)
    parsed  = parser.parse(sources[0])
    all_entities.extend(ner.extract(parsed))
    all_rels.extend(rel.extract(parsed, entities=all_entities))

kg = builder.build(entities=all_entities, relationships=all_rels)
print(f"Unified graph: {len(kg.nodes)} nodes, {len(kg.edges)} edges")
```

### Conflict Detection and Resolution

```python
from semantica.conflicts import ConflictDetector, ConflictResolver

detector  = ConflictDetector()
conflicts = detector.detect_conflicts(all_entities)

resolver = ConflictResolver(default_strategy="voting")
resolved = resolver.resolve_conflicts(conflicts)

print(f"Detected {len(conflicts)} conflicts, resolved {len(resolved)}")
```

### Parquet and XML Ingestion (v0.5.0)

```python
from semantica.ingest import ParquetIngestor, XMLIngestor

parquet_data = ParquetIngestor().ingest("data/records.parquet")
xml_data     = XMLIngestor(safe_mode=True).ingest("data/feed.xml")
```

### Persistent Storage — Neo4j

```python
from semantica.graph_store import GraphStore

store = GraphStore(
    backend="neo4j",
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
)
store.connect()

apple = store.create_node(labels=["Company"], properties={"name": "Apple Inc."})
tim   = store.create_node(labels=["Person"],  properties={"name": "Tim Cook"})
store.create_relationship(
    start_node_id=tim["id"],
    end_node_id=apple["id"],
    rel_type="CEO_OF",
)
store.close()
```

---

## Advanced

### GraphRAG with Reasoning

```python
from semantica.context import AgentContext
from semantica.reasoning import Reasoner

context = AgentContext(
    vector_store=vs,
    knowledge_graph=kg,
    graph_expansion=True,
    hybrid_alpha=0.7,
)

reasoner = Reasoner()
reasoner.add_rule("IF Library(?x) AND Language(?y) THEN TechStackItem(?x)")
inferred = reasoner.infer_facts(kg.get_all_triplets())

for fact in inferred:
    kg.add_fact_from_string(fact)

results = context.retrieve("What technologies are used in this project?")
```

### Temporal Knowledge Graph (v0.4.0)

```python
from semantica.kg import TemporalKnowledgeGraph

tkg = TemporalKnowledgeGraph()
tkg.add_temporal_fact("Apple", "CEO", "Tim Cook", valid_from="2011-08-24")
tkg.add_temporal_fact("Apple", "CEO", "Steve Jobs", valid_from="1997-09-16", valid_to="2011-08-24")

ceo_2005 = tkg.query_at("Apple", "CEO", timestamp="2005-01-01")
```

### Distance Intelligence (v0.5.0)

```python
from semantica.kg import DistanceCalculator

calc = DistanceCalculator(kg)
dist = calc.calculate("Apple Inc.", "Microsoft")

print(f"Distance: {dist.score:.3f} — Band: {dist.band}")
similar = calc.find_similar("Apple Inc.", radius=0.3)
```

---

## Production

### Batch Processing (Large Datasets)

```python
from semantica.pipeline import Pipeline
from semantica.ingest import FileIngestor
from semantica.parse import DocumentParser
from semantica.semantic_extract import NERExtractor
from semantica.kg import GraphBuilder

pipeline = Pipeline(workers=4)
pipeline.add_step("ingest",  FileIngestor())
pipeline.add_step("parse",   DocumentParser())
pipeline.add_step("extract", NERExtractor(), parallel=True, batch_size=50)
pipeline.add_step("build",   GraphBuilder())

result = pipeline.run("data/")
print(f"Processed: {result.processed_count}, Failed: {result.failed_count}")
```

### Real-Time Streaming

```python
from semantica.ingest import StreamIngestor
from semantica.semantic_extract import NERExtractor, RelationExtractor
from semantica.kg import GraphBuilder

stream  = StreamIngestor(stream_uri="kafka://localhost:9092/topic")
ner     = NERExtractor()
rel     = RelationExtractor()
builder = GraphBuilder()

for batch in stream.stream(batch_size=100):
    all_entities, all_rels = [], []
    for item in batch:
        text = str(item)
        all_entities.extend(ner.extract(text))
        all_rels.extend(rel.extract(text, entities=all_entities))
    kg = builder.build(entities=all_entities, relationships=all_rels)
    print(f"Processed batch: {len(kg.nodes)} nodes")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Quickstart" icon="play" href="quickstart">
    Step-by-step first pipeline tutorial.
  </Card>
  <Card title="Cookbook" icon="book-open" href="cookbook">
    Interactive Jupyter notebook tutorials.
  </Card>
  <Card title="Use Cases" icon="briefcase" href="use-cases">
    Domain-specific examples.
  </Card>
  <Card title="API Reference" icon="code" href="reference/core">
    Complete API documentation.
  </Card>
</CardGroup>
