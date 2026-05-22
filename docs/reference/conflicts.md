---
title: "Conflicts Module"
description: "Multi-source conflict detection and resolution — value, type, temporal, and logical conflicts."
icon: "triangle-exclamation"
---

> Comprehensive conflict detection and resolution for data discrepancies across multiple sources.

---

## Overview

When multiple sources disagree on the same fact, the **Conflicts Module** detects and resolves the conflict rather than silently picking one value.

Detection types: **value**, **type**, **temporal**, and **logical** conflicts.

---

## ConflictDetector

```python
from semantica.conflicts import ConflictDetector

detector = ConflictDetector()
conflicts = detector.detect_conflicts(kg)

for conflict in conflicts:
    print(f"Conflict on '{conflict.entity}' — {conflict.attribute}")
    print(f"  Source A: {conflict.value_a} (from {conflict.source_a})")
    print(f"  Source B: {conflict.value_b} (from {conflict.source_b})")
    print(f"  Type: {conflict.conflict_type}")
```

---

## Detection Types

```python
# Detect specific types only
conflicts = detector.detect_conflicts(
    kg,
    types=["value", "temporal"]   # value | type | temporal | logical
)
```

**Value conflicts** — same entity, same attribute, different values across sources.
**Type conflicts** — same entity classified as different types in different sources.
**Temporal conflicts** — overlapping validity windows with contradictory facts.
**Logical conflicts** — facts that violate ontology axioms or constraints.

---

## Conflict Resolution

```python
from semantica.conflicts import ConflictResolver

resolver = ConflictResolver()
resolved_kg = resolver.resolve(
    kg,
    conflicts,
    strategy="most_recent"   # see strategies below
)
```

Resolution strategies:

| Strategy | Description |
|----------|-------------|
| `most_recent` | Prefer the most recently updated fact |
| `most_reliable` | Prefer the source with the highest reliability score |
| `majority_vote` | Use the value agreed upon by most sources |
| `highest_confidence` | Prefer the fact with the highest confidence score |
| `flag_for_review` | Mark conflicting facts for manual resolution |

---

## Source Reliability Scoring

```python
resolver = ConflictResolver(
    source_reliability={
        "pubmed": 0.95,
        "wikipedia": 0.80,
        "user_input": 0.60
    }
)
resolved_kg = resolver.resolve(kg, conflicts, strategy="most_reliable")
```

---

## Conflict Report

```python
report = detector.generate_report(conflicts)
print(f"Total conflicts: {report.total}")
print(f"By type: {report.by_type}")
print(f"Most conflicted entities: {report.top_entities[:5]}")

report.export("conflicts.json")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Resolve duplicate entities before conflict detection.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Logical conflicts use ontology axioms.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    Track which source each conflicting fact came from.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The graph being checked for conflicts.
  </Card>
</CardGroup>
