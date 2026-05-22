---
title: "Semantic Extract Module"
description: "Named entity recognition, relation extraction, event detection, and triplet generation."
icon: "magnifying-glass-chart"
---

> Advanced information extraction system for Entities, Relations, Events, and Triplets.

---

## Overview

The **Semantic Extract Module** extracts structured information from unstructured text — the foundation of every knowledge graph in Semantica.

<CardGroup cols={2}>
  <Card title="NER" icon="magnifying-glass">
    Extract named entities (Person, Org, Location) with confidence scores.
  </Card>
  <Card title="Relation Extraction" icon="arrows-left-right">
    Identify relationships between entities (e.g., `founded_by`, `located_in`).
  </Card>
  <Card title="Event Detection" icon="calendar">
    Detect events with temporal information and participants.
  </Card>
  <Card title="Triplet Generation" icon="diagram-project">
    Generate RDF triplets (Subject–Predicate–Object) for knowledge graphs.
  </Card>
</CardGroup>

---

## NERExtractor

```python
from semantica.semantic_extract import NERExtractor
from semantica.llms import Groq
import os

# Pattern-based (fast, no API key needed)
ner = NERExtractor(method="pattern")
entities = ner.extract("Apple Inc. was founded by Steve Jobs in Cupertino.")

# ML-based
ner = NERExtractor(method="ml", model="dslim/bert-large-NER")
entities = ner.extract(text)

# LLM-based (most accurate for complex schemas)
llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
ner = NERExtractor(method="llm", llm_provider=llm, max_retries=3)
entities = ner.extract(text)
```

Output format:

```python
[
    {"text": "Apple Inc.",  "type": "ORGANIZATION", "confidence": 0.98, "start": 0,  "end": 10},
    {"text": "Steve Jobs",  "type": "PERSON",       "confidence": 0.99, "start": 27, "end": 37},
    {"text": "Cupertino",   "type": "LOCATION",     "confidence": 0.97, "start": 41, "end": 50}
]
```

<Note>
  **v0.5.0 fix:** `NERExtractor(method="llm")` no longer silently falls back to pattern extraction on custom gateways. The `response_format=json_object` parameter is now conditionally omitted for incompatible gateways, and a plain `generate()` + JSON parsing fallback is used.
</Note>

---

## RelationExtractor

```python
from semantica.semantic_extract import RelationExtractor

rel = RelationExtractor(method="llm", llm_provider=llm, max_retries=3)
relationships = rel.extract(text, entities=entities)
```

Output format:

```python
[
    {"subject": "Steve Jobs", "predicate": "founded",    "object": "Apple Inc.", "confidence": 0.92},
    {"subject": "Apple Inc.", "predicate": "located_in", "object": "Cupertino",  "confidence": 0.89}
]
```

Methods: `"rule"`, `"ml"` (REBEL model), `"llm"`.

---

## TripletExtractor

```python
from semantica.semantic_extract import TripletExtractor

trip = TripletExtractor(method="llm", llm_provider=llm)
triplets = trip.extract(text)
```

Generates RDF-ready `(subject, predicate, object)` triplets directly from text, suitable for loading into a triplet store.

---

## EventExtractor

```python
from semantica.semantic_extract import EventExtractor

extractor = EventExtractor(method="llm", llm_provider=llm)
events = extractor.extract(text)
```

Output includes event type, participants, temporal information, and confidence score.

---

## Custom Entity Types

```python
ner = NERExtractor(
    method="pattern",
    custom_entities={
        "DRUG": ["aspirin", "ibuprofen", "metformin"],
        "GENE": ["BRCA1", "TP53", "EGFR"]
    }
)
```

---

## Batch Processing

```python
texts = ["Text 1...", "Text 2...", "Text 3..."]

ner = NERExtractor(method="llm", llm_provider=llm)
batch_results = ner.extract_batch(texts, batch_size=10)
```

---

## Using All Extractors Together

```python
from semantica.semantic_extract import NERExtractor, RelationExtractor, TripletExtractor

llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

ner  = NERExtractor(method="llm",  llm_provider=llm, max_retries=3)
rel  = RelationExtractor(method="llm", llm_provider=llm, max_retries=3)
trip = TripletExtractor(method="llm", llm_provider=llm, max_retries=3)

entities      = ner.extract(text)
relationships = rel.extract(text, entities=entities)
triplets      = trip.extract(text)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="LLM Providers" icon="microchip" href="llms">
    Configure which LLM is used for extraction.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    Build graphs from extracted entities and relationships.
  </Card>
  <Card title="Parse Module" icon="file-lines" href="parse">
    Parse documents before extraction.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Resolve duplicate entities after extraction.
  </Card>
</CardGroup>
