---
title: "Semantic Extract Module"
description: "Named entity recognition, relation extraction, event detection, and triplet generation."
icon: "magnifying-glass-chart"
---

`semantica.semantic_extract` extracts structured information from unstructured text — the foundation of every knowledge graph in Semantica. All extractors support three modes: pattern-based (no API key), ML-based, and LLM-based.

## Getting Started

### Prerequisites & Setup

**Step 1: Install Dependencies**

```bash
# Basic extraction (pattern methods only)
pip install semantica

# HuggingFace models for advanced NER
pip install semantica[models-huggingface]

# LLM-based extraction (highest accuracy)
pip install semantica[llm-groq]    # or llm-openai
```

**Step 2: Set API Keys** (for LLM methods only)

```bash
export GROQ_API_KEY="your_groq_key_here"
export OPENAI_API_KEY="your_openai_key_here"
```

**Step 3: First Extraction**

```python
from semantica.semantic_extract import NERExtractor

# Start with pattern method (no setup required)
ner = NERExtractor(method="pattern")
entities = ner.extract("Apple Inc. was founded by Steve Jobs.")
print(f"Found {len(entities)} entities")
# Output: Found 2 entities

# Upgrade to LLM for better accuracy
from semantica.llms import Groq
import os

llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
ner = NERExtractor(method="llm", llm_provider=llm)
entities = ner.extract("Apple Inc. was founded by Steve Jobs.")
```

## Exported Classes

<Tip>
  `NamedEntityRecognizer` is the high-level coordinator with confidence thresholding and overlap merging. `NERExtractor` is the lower-level implementation. For most use cases, start with `NERExtractor` for simplicity or `NamedEntityRecognizer` for fine-grained control.
</Tip>

| Class | Role |
| --- | --- |
| `NamedEntityRecognizer` | High-level NER with confidence thresholding and overlap merging |
| `NERExtractor` | Core NER implementation — use directly for simplicity |
| `RelationExtractor` | Typed relationship extraction (`founded_by`, `located_in`, ...) |
| `TripletExtractor` | Direct `(subject, predicate, object)` triplet generation for RDF output |
| `EventDetector` | Event detection with participants, temporal context, and confidence scores |
| `CoreferenceResolver` | Resolve "Apple" and "the company" to the same canonical entity |
| `Entity` | `{id, text, type, confidence, start, end}` |
| `Relation` | `{subject, predicate, object, confidence}` |
| `Event` | `{type, participants, temporal, location, confidence}` |

## Method Selection Guide

Choose the right extraction method based on your requirements:

| Priority | Method | Setup Required | API Cost | Accuracy | Use Cases |
|----------|--------|----------------|----------|----------|-----------|
| **Speed** | `pattern` | None | Free | Good | Quick prototyping, known entity types |
| **Custom Models** | `huggingface` | Model download | Free | Varies | Domain-specific models, fine-tuned NER |
| **Best Accuracy** | `llm` | API key | $$ | Highest | Complex schemas, custom entity types |

### Quick Recommendations

```python
# No setup required
ner = NERExtractor(method="pattern")

# Best accuracy - requires API key
from semantica.llms import Groq
import os
llm = Groq(api_key=os.getenv("GROQ_API_KEY"))
ner = NERExtractor(method="llm", llm_provider=llm)

# Custom models - domain-specific
ner = NERExtractor(method="huggingface")
entities = ner.extract(text, model="dslim/bert-base-NER", device="cpu")
```

### Method Availability by Extractor

| Extractor | `pattern` | `huggingface` | `llm` | Notes |
|-----------|-----------|---------------|-------|-------|
| `NERExtractor` | ✅ | ✅ | ✅ | Full method support |
| `RelationExtractor` | ✅ | ✅ | ✅ | Also supports `dependency`, `cooccurrence` |
| `TripletExtractor` | ✅ | ✅ | ✅ | Also supports `rules` method |
| `EventDetector` | ✅ | ❌ | ✅ | Pattern and LLM only |

### Method Fallback Chains

For reliability, extractors support fallback chains that try methods in order until one succeeds:

```python
# Try LLM first, fall back to pattern if it fails
ner = NERExtractor(method=["llm", "pattern"])
rel = RelationExtractor(method=["llm", "pattern"]) 
trip = TripletExtractor(method=["llm", "pattern"])

# Always returns results - guarantees non-empty extraction
entities = ner.extract(text)
```

## Quick Start

```python
from semantica.semantic_extract import NERExtractor, RelationExtractor, TripletExtractor
from semantica.llms import Groq
import os

text = "Apple Inc. was founded by Steve Jobs in Cupertino in 1976."
llm  = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

entities      = NERExtractor(method="llm", llm_provider=llm).extract(text)
relationships = RelationExtractor(method="llm", llm_provider=llm).extract(text, entities=entities)
triplets      = TripletExtractor(method="llm", llm_provider=llm).extract(text)
```

<img src="/assets/img/diagrams/extraction-pipeline.svg" alt="Semantic extraction pipeline: raw text fans into NER, Relation, and Coreference extractors, then merges into a Triplet Generator" style={{ width: '100%', borderRadius: '12px', margin: '0 0 24px' }} />

## Extractor Methods

| Method | Returns | Description |
| ------ | ------- | ----------- |
| `extract(text)` | `List[Entity]` / `List[Relation]` / `List[Triplet]` / `List[Event]` | Extract from single text input |
| `extract(texts)` | `List[List[...]]` | Process multiple texts (batch detected automatically) |

## NERExtractor

```python
from semantica.semantic_extract import NERExtractor
from semantica.llms import Groq
import os

# Pattern-based — fast, no API key, good for standard entity types
ner = NERExtractor(method="pattern")
entities = ner.extract("Apple Inc. was founded by Steve Jobs in Cupertino.")

# HuggingFace-based — custom models, no API cost
ner = NERExtractor(method="huggingface")
entities = ner.extract(text, model="dslim/bert-base-NER", device="cpu")

# LLM-based — best accuracy, handles complex schemas and custom types
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

### Custom Entity Types

```python
ner = NERExtractor(
    method="pattern",
    custom_entities={
        "DRUG": ["aspirin", "ibuprofen", "metformin"],
        "GENE": ["BRCA1", "TP53", "EGFR"]
    }
)
```

<Note>
  **v0.5.0 fix:** `NERExtractor(method="llm")` no longer silently falls back to pattern extraction on custom gateways. The `response_format=json_object` parameter is now conditionally omitted for incompatible gateways, with a plain `generate()` + JSON parsing fallback applied automatically.
</Note>

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

Available methods: `"pattern"` (pattern-based), `"dependency"` (spaCy parsing), `"cooccurrence"` (proximity-based), `"huggingface"` (custom models), `"llm"`.

## TripletExtractor

Generate RDF-ready `(subject, predicate, object)` triplets directly from text:

```python
from semantica.semantic_extract import TripletExtractor

trip = TripletExtractor(method="llm", llm_provider=llm)
triplets = trip.extract(text)
# → [{"subject": "Steve Jobs", "predicate": "founded", "object": "Apple Inc.", ...}]
```

Triplets are suitable for loading directly into a triplet store or knowledge graph.

## EventDetector

Detect events with participants and temporal context:

```python
from typing import List
from semantica.semantic_extract import EventDetector, Event

extractor = EventDetector(method="llm", llm_provider=llm)
events: List[Event] = extractor.extract(text)

for event in events:
    print(f"Event type:   {event.type}")
    print(f"Participants: {event.participants}")
    print(f"Temporal:     {event.temporal}")
    print(f"Confidence:   {event.confidence:.2f}")
```

Output fields per event: `type`, `participants` (with roles), `temporal`, `location`, and `confidence`.

## CoreferenceResolver

Resolve pronoun and alias references to canonical entities before extraction:

```python
from semantica.semantic_extract import CoreferenceResolver

resolver = CoreferenceResolver()
resolved_text = resolver.resolve(
    "Apple Inc. was founded in 1976. The company is headquartered in Cupertino."
)
# "Apple Inc." replaces "The company" for consistent downstream extraction
```

## Batch Processing

All extractors automatically detect batch input and process multiple texts efficiently:

```python
# Batch processing with list input
texts = ["Apple Inc. was founded by Steve Jobs.", "Google was founded by Larry Page.", "Microsoft was founded by Bill Gates."]

ner = NERExtractor(method="llm", llm_provider=llm)
batch_results = ner.extract(texts)  # Returns List[List[Entity]]

# Process results
for i, doc_entities in enumerate(batch_results):
    print(f"Document {i}: {len(doc_entities)} entities")
    for entity in doc_entities:
        print(f"  - {entity.text} ({entity.label})")
```

**Batch Input Options:**

```python
# Option 1: List of strings
texts = ["Text 1...", "Text 2...", "Text 3..."]
results = ner.extract(texts)

# Option 2: List of documents with IDs (adds provenance metadata)
documents = [
    {"id": "doc_1", "content": "Apple Inc. was founded by Steve Jobs."},
    {"id": "doc_2", "content": "Google was founded by Larry Page."}
]
results = ner.extract(documents)  # Entities include document_id in metadata
```

## Using All Extractors Together

The standard extraction pipeline — entities → relationships → triplets:

```python
from semantica.semantic_extract import NERExtractor, RelationExtractor, TripletExtractor
from semantica.llms import Groq
import os

llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

ner  = NERExtractor(method="llm",      llm_provider=llm, max_retries=3)
rel  = RelationExtractor(method="llm", llm_provider=llm, max_retries=3)
trip = TripletExtractor(method="llm",  llm_provider=llm, max_retries=3)

entities      = ner.extract(text)
relationships = rel.extract(text, entities=entities)
triplets      = trip.extract(text)
```

## Extraction Method Comparison

| Method | Speed | Cost | Accuracy | Custom Types |
| ------ | ----- | ---- | -------- | ------------ |
| `pattern` | Very fast | Free | Medium | Yes (dictionary) |
| `ml` | Fast | Free | High | Limited |
| `llm` | Medium | API cost | Highest | Yes (schema) |

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
