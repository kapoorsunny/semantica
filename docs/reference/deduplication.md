---
title: "Deduplication Module"
description: "Entity deduplication v1/v2, similarity scoring, and merging — up to 7x faster with v2 strategies."
icon: "copy"
---

> Advanced entity deduplication and resolution for a clean, single-source-of-truth knowledge graph.

---

## Overview

The **Deduplication Module** identifies and merges duplicate entities across sources using similarity scoring and blocking strategies.

**v2 strategies** (`blocking_v2`, `hybrid_v2`, `semantic_v2`) are up to **7x faster** than v1 and support fine-grained result control via `max_results`, `top_k_per_entity`, `min_similarity`, and `sort_by`.

---

## EntityResolver

```python
from semantica.deduplication import EntityResolver

resolver = EntityResolver()
merged_entities = resolver.resolve(entities, strategy="semantic_v2")
```

Strategies:

| Strategy | Method | Speed | Accuracy |
|----------|--------|-------|----------|
| `jaro_winkler` | String similarity (v1) | Fast | Medium |
| `blocking_v2` | Blocking + Jaro-Winkler (v2) | Very fast | Medium |
| `hybrid_v2` | Blocking + semantic + string (v2) | Fast | High |
| `semantic_v2` | Embedding similarity (v2) | Medium | Highest |

---

## DuplicateDetector

Fine-grained control over duplicate detection results.

```python
from semantica.deduplication import DuplicateDetector

detector = DuplicateDetector()
duplicates = detector.find_duplicates(
    entities,
    strategy="semantic_v2",
    min_similarity=0.85,      # minimum score to consider a duplicate
    top_k_per_entity=3,       # max candidates per entity
    max_results=100,          # total result cap
    sort_by="similarity"      # "similarity" | "entity_id" | "cluster_size"
)

for dup in duplicates:
    print(f"{dup['entity_a']} ≈ {dup['entity_b']} ({dup['similarity']:.2f})")
```

<Note>
  **v0.5.0 fix:** `ConflictDetector` no longer produces duplicate definition errors when the same entity appears in multiple sources with identical definitions.
</Note>

---

## Merging Entities

```python
from semantica.deduplication import EntityMerger

merger = EntityMerger()
merged_kg = merger.merge(
    kg,
    duplicates,
    strategy="union",        # "union" | "intersection" | "most_recent" | "most_confident"
    preserve_provenance=True # keep source references after merge
)
```

---

## Blocking Strategies

Blocking reduces the comparison search space for large entity sets.

```python
resolver = EntityResolver(
    blocking_strategy="token",        # "token" | "phonetic" | "ngram"
    blocking_threshold=0.6,
    comparison_strategy="semantic_v2"
)
```

---

## Custom Similarity Functions

```python
def custom_similarity(entity_a, entity_b):
    # Domain-specific matching logic
    return score  # 0.0 to 1.0

resolver = EntityResolver(similarity_fn=custom_similarity)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Conflicts" icon="triangle-exclamation" href="conflicts">
    Detect value conflicts between non-duplicate entities.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    GraphBuilder uses deduplication during construction.
  </Card>
  <Card title="Normalize" icon="broom" href="normalize">
    Normalize entity names before deduplication.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    Track merged entity lineage.
  </Card>
</CardGroup>
