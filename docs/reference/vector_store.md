---
title: "Vector Store Module"
description: "Unified interface for FAISS, Pinecone, Weaviate, Qdrant, Milvus, and PgVector with hybrid search."
icon: "database"
---

> Unified vector database interface supporting multiple backends and hybrid search.

---

## Overview

The **Vector Store Module** provides a unified API for storing and searching vector embeddings across all major backends.

<CardGroup cols={2}>
  <Card title="Multi-Backend" icon="server">
    FAISS (local), Pinecone, Weaviate, Qdrant, Milvus, PgVector, in-memory.
  </Card>
  <Card title="Hybrid Search" icon="magnifying-glass-plus">
    Combine dense vector similarity with sparse keyword/metadata filtering.
  </Card>
  <Card title="Metadata Filtering" icon="filter">
    Rich filtering (eq, ne, gt, lt, in, contains) on any field.
  </Card>
  <Card title="Namespace Isolation" icon="layer-group">
    Multi-tenant support via isolated namespaces.
  </Card>
</CardGroup>

---

## Basic Usage

```python
from semantica.vector_store import VectorStore

# In-memory (development)
store = VectorStore(backend="inmemory", dimension=768)

# FAISS (local, production)
store = VectorStore(backend="faiss", dimension=768, index_path="store.faiss")

# Add vectors
store.add_vectors(embeddings=embeddings, ids=["doc1", "doc2"], metadata=[{}, {}])

# Semantic search
results = store.search(query_vector, top_k=10)
for r in results:
    print(f"{r['id']} — score: {r['score']:.3f}")
```

---

## Backends

<Tabs>
  <Tab title="FAISS">
    ```python
    store = VectorStore(
        backend="faiss",
        dimension=768,
        index_type="IVF",      # Flat, IVF, HNSW
        index_path="store.faiss"
    )
    ```
    Best for: local development, on-premise production with no external services.
  </Tab>
  <Tab title="Pinecone">
    ```bash
    pip install "semantica[pinecone]"
    ```
    ```python
    store = VectorStore(
        backend="pinecone",
        dimension=768,
        api_key=os.getenv("PINECONE_API_KEY"),
        index_name="semantica-index",
        environment="us-east-1-aws"
    )
    ```
  </Tab>
  <Tab title="Weaviate">
    ```bash
    pip install "semantica[weaviate]"
    ```
    ```python
    store = VectorStore(
        backend="weaviate",
        dimension=768,
        url="http://localhost:8080",
        class_name="Document"
    )
    ```
  </Tab>
  <Tab title="Qdrant">
    ```bash
    pip install "semantica[qdrant]"
    ```
    ```python
    store = VectorStore(
        backend="qdrant",
        dimension=768,
        url="http://localhost:6333",
        collection_name="semantica"
    )
    ```
  </Tab>
</Tabs>

---

## Hybrid Search

Combines vector similarity with keyword/metadata filters.

```python
results = store.hybrid_search(
    query_vector=query_embedding,
    query_text="machine learning",   # keyword component
    top_k=10,
    alpha=0.7,                       # 0=keyword only, 1=vector only
    filters={"category": "research", "year": {"$gte": 2022}}
)
```

---

## Metadata Filtering

```python
# Equality
results = store.search(query_vector, filters={"author": "John Smith"})

# Range
results = store.search(query_vector, filters={"date": {"$gte": "2023-01-01"}})

# Set membership
results = store.search(query_vector, filters={"tag": {"$in": ["ai", "ml"]}})

# Compound
results = store.search(query_vector, filters={
    "$and": [{"category": "research"}, {"year": {"$gte": 2022}}]
})
```

---

## Namespaces (Multi-Tenant)

```python
store = VectorStore(backend="faiss", dimension=768)

store.add_vectors(embeddings, ids, namespace="tenant_a")
store.add_vectors(embeddings, ids, namespace="tenant_b")

results = store.search(query_vector, namespace="tenant_a")
```

---

## Batch Operations

```python
# Batch add
store.add_vectors_batch(embeddings_list, ids_list, batch_size=1000)

# Batch delete
store.delete_vectors(ids=["doc1", "doc2", "doc3"])

# Update metadata
store.update_metadata("doc1", {"status": "archived"})
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Embeddings" icon="vector-square" href="embeddings">
    Generate the vectors stored here.
  </Card>
  <Card title="Context" icon="brain" href="context">
    AgentContext uses VectorStore for memory.
  </Card>
  <Card title="PgVector Guide" icon="database" href="../vector_stores/pgvector">
    PostgreSQL vector storage with pgvector.
  </Card>
  <Card title="Ingest" icon="download" href="ingest">
    Ingest documents before embedding and storing.
  </Card>
</CardGroup>
