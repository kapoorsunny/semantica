---
title: "Vector Store: High-Performance Usage"
description: "Parallel ingestion, batch processing, and performance tuning for the Semantica Vector Store."
icon: "bolt"
---

> High-performance batch ingestion with parallel embedding generation — 3–10× faster than sequential processing.

---

## Key Features

- **Parallel ingestion** — multi-threaded embedding generation and storage
- **Batch processing** — minimizes overhead by grouping documents into chunks
- **Unified API** — `add_documents` handles embedding generation and storage in one call

---

## Quick Start: Parallel Ingestion

```python
from semantica.vector_store import VectorStore
import time

store = VectorStore(backend="faiss", dimension=768)

documents = [f"This is document number {i} with some content." for i in range(1000)]
metadata  = [{"source": "generated", "id": i} for i in range(1000)]

start = time.time()
ids   = store.add_documents(
    documents=documents,
    metadata=metadata,
    batch_size=64,
    parallel=True,       # default: True
)
print(f"Ingested {len(ids)} documents in {time.time() - start:.2f}s")
```

---

## Performance Comparison

**Old method (sequential loop)** — slower due to per-item overhead:

```python
for doc in documents:
    emb = embedder.generate(doc)
    store.store_vectors([emb], [{"text": doc}])
```

**New method (parallel batching)** — 3–10× faster:

```python
store.add_documents(documents, parallel=True)
```

---

## Configuration and Tuning

### `max_workers`

Number of concurrent threads for embedding generation.

- **Default**: 6 (optimized for most systems)
- Override only if you have very high core counts or specific throughput needs

```python
store = VectorStore(max_workers=16)
```

### `batch_size`

Number of documents processed in a single chunk.

- **Default**: 32
- **Local models**: 32–64 works well
- **API models (OpenAI, etc.)**: 100–200 reduces network latency overhead

```python
store.add_documents(documents, batch_size=100)
```

---

## Manual Batch Embedding

If you need embeddings without immediately storing them:

```python
vectors = store.embed_batch(texts=documents[:100])
print(f"Generated {len(vectors)} vectors")
```

---

## Best Practices

<Tip>
- **Metadata consistency** — ensure your `metadata` list is the same length as `documents`.
- **Error handling** — `add_documents` propagates exceptions if embedding fails; validate your data first.
- **Memory usage** — very large `batch_size` combined with high `max_workers` increases RAM usage. Monitor system resources for large corpora.
</Tip>

---

## See Also

<CardGroup cols={2}>
  <Card title="Vector Store Reference" icon="vector-square" href="reference/vector_store">
    Full VectorStore API with all backends.
  </Card>
  <Card title="Embeddings" icon="brain" href="reference/embeddings">
    Embedding providers and GPU acceleration.
  </Card>
</CardGroup>
