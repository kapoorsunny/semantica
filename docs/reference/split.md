---
title: "Split Module"
description: "15+ text chunking methods including recursive, semantic, entity-aware, and relation-aware splitting."
icon: "scissors"
---

> Comprehensive document chunking for optimal RAG, embedding, and extraction pipelines.

---

## Overview

The **Split Module** breaks documents into chunks while preserving context and semantic meaning — critical for embedding quality in RAG systems.

---

## TextSplitter

```python
from semantica.split import TextSplitter

splitter = TextSplitter(
    method="semantic",   # see methods below
    chunk_size=1000,
    overlap=200
)

chunks = splitter.split(text)
for chunk in chunks:
    print(f"Chunk: {chunk.text[:80]}... ({chunk.token_count} tokens)")
```

---

## Splitting Methods

| Method | Description | Best for |
|--------|-------------|----------|
| `recursive` | Split by paragraph → sentence → word | General purpose |
| `semantic` | Split at semantic boundaries (topic shifts) | RAG systems |
| `entity-aware` | Keep entity mentions intact across boundaries | NER pipelines |
| `relation-aware` | Keep relation triplets intact | KG construction |
| `sentence` | Split by sentence | Short content |
| `token` | Split by token count (tiktoken) | LLM context windows |
| `fixed` | Fixed character count with overlap | Batch processing |
| `markdown` | Split by Markdown headers | Documentation |
| `code` | Split by function/class boundaries | Code analysis |

---

## Entity-Aware Chunking

```python
from semantica.split import TextSplitter
from semantica.semantic_extract import NERExtractor

ner = NERExtractor()
entities = ner.extract(text)

splitter = TextSplitter(method="entity-aware")
chunks = splitter.split(text, entities=entities)
```

Entity mentions are never split across chunk boundaries, preserving context for downstream NER.

---

## Relation-Aware Chunking

```python
splitter = TextSplitter(method="relation-aware")
chunks = splitter.split(text, relationships=relationships)
```

Keeps subject–predicate–object triplets within the same chunk.

---

## Semantic Chunking

```python
from semantica.split import TextSplitter
from semantica.embeddings import EmbeddingGenerator

embedder = EmbeddingGenerator(model="sentence-transformers")
splitter = TextSplitter(
    method="semantic",
    embedder=embedder,
    similarity_threshold=0.7   # split when topic similarity drops below this
)

chunks = splitter.split(text)
```

---

## Chunk Object

```python
@dataclass
class Chunk:
    text: str
    start_char: int
    end_char: int
    token_count: int
    metadata: Dict       # source_id, chunk_index, section_title, etc.
    entities: List[Dict] # if entity-aware splitting was used
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Parse" icon="file-lines" href="parse">
    Parse documents before chunking.
  </Card>
  <Card title="Embeddings" icon="vector-square" href="embeddings">
    Embed chunks for vector search.
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Extract entities from chunks.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Integrate splitting into a pipeline.
  </Card>
</CardGroup>
