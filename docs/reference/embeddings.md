---
title: "Embeddings Module"
description: "Text embedding generation with Sentence-Transformers, FastEmbed, OpenAI, and BGE model support."
icon: "vector-square"
---

> Unified interface for generating vector representations of text.

---

## Overview

The **Embeddings Module** converts text into dense vectors for semantic search, entity resolution, and GraphRAG retrieval. It abstracts multiple providers behind a single API.

---

## EmbeddingGenerator

```python
from semantica.embeddings import EmbeddingGenerator

# Sentence-Transformers (default, free, local)
generator = EmbeddingGenerator(model="sentence-transformers")
embeddings = generator.generate(["Text 1", "Text 2"])

# Specific model
generator = EmbeddingGenerator(model="BAAI/bge-large-en-v1.5")
embeddings = generator.generate(texts)

# OpenAI
generator = EmbeddingGenerator(
    model="openai",
    model_name="text-embedding-3-small",
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

## Supported Models

| Provider | Model | Dimension | Notes |
|----------|-------|-----------|-------|
| `sentence-transformers` | `all-MiniLM-L6-v2` | 384 | Default, fast, free |
| `sentence-transformers` | `all-mpnet-base-v2` | 768 | Higher quality |
| `bge` | `BAAI/bge-large-en-v1.5` | 1024 | State-of-the-art retrieval |
| `fastembed` | `BAAI/bge-small-en-v1.5` | 384 | Fast, CPU-optimized |
| `openai` | `text-embedding-3-small` | 1536 | OpenAI API |
| `openai` | `text-embedding-3-large` | 3072 | OpenAI API, highest quality |

---

## Similarity Computation

```python
# Cosine similarity between two embeddings
similarity = generator.similarity(embeddings[0], embeddings[1])
print(f"Similarity: {similarity:.3f}")   # 0.0 to 1.0

# Find top-k most similar texts
query_embedding = generator.generate(["machine learning"])[0]
scores = generator.rank(query_embedding, embeddings)
```

---

## Batch Generation

```python
# Efficient batched generation
texts = ["Text 1", "Text 2", ..., "Text 10000"]
embeddings = generator.generate_batch(texts, batch_size=128, show_progress=True)
```

---

## Caching

```python
generator = EmbeddingGenerator(
    model="sentence-transformers",
    cache_dir=".embeddings_cache",   # persist embeddings to disk
    cache_ttl=3600                    # cache TTL in seconds
)
```

The distance intelligence feature (v0.5.0) uses embedding cache optimization to avoid recomputing embeddings for large distance matrix calculations.

---

## GPU Acceleration

```python
generator = EmbeddingGenerator(
    model="sentence-transformers",
    device="cuda"   # "cpu" | "cuda" | "mps"
)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Vector Store" icon="database" href="vector_store">
    Store and search the generated embeddings.
  </Card>
  <Card title="Split" icon="scissors" href="split">
    Chunk text before embedding.
  </Card>
  <Card title="KG Module" icon="diagram-project" href="kg">
    Distance Intelligence uses embeddings for semantic neighborhoods.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Semantic deduplication uses embeddings for entity resolution.
  </Card>
</CardGroup>
