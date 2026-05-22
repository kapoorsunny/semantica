---
title: "Provenance Module"
description: "W3C PROV-O compliant lineage tracking, source attribution, and audit trails across all 17 modules."
icon: "link"
---

> W3C PROV-O compliant provenance tracking for high-stakes domains requiring complete traceability.

---

## Overview

The **Provenance Module** tracks the full lineage of every fact — from raw ingestion through extraction, reasoning, and export. Compliant with W3C PROV-O, suitable for HIPAA, SOX, GDPR, and FDA 21 CFR Part 11 environments.

---

## ProvenanceManager

```python
from semantica.provenance import ProvenanceManager

manager = ProvenanceManager()

# Track an entity
manager.track_entity(
    entity_id="apple_inc",
    source="annual_report_2023.pdf",
    entity_type="Organization",
    extraction_method="llm",
    confidence=0.98
)

# Track a relationship
manager.track_relationship(
    rel_id="steve_jobs_founded_apple",
    source="annual_report_2023.pdf",
    extraction_method="llm",
    confidence=0.92
)

# Get full lineage
lineage = manager.get_lineage("apple_inc")
print(f"Source: {lineage.source}")
print(f"Extracted: {lineage.extracted_at}")
print(f"Method: {lineage.extraction_method}")
```

---

## Activity Tracking

```python
# Track a pipeline activity
activity_id = manager.start_activity(
    activity_type="ner_extraction",
    used=["annual_report_2023.pdf"],
    generated=["apple_inc", "steve_jobs"]
)

manager.end_activity(activity_id)

# Query activities
activities = manager.get_activities(entity_id="apple_inc")
```

---

## Lineage Graph

```python
# Full lineage from source to current state
lineage_graph = manager.get_lineage_graph("apple_inc")

for node in lineage_graph.nodes:
    print(f"{node.id}: {node.type} — {node.timestamp}")
```

---

## W3C PROV-O Export

```python
# Export provenance as W3C PROV-O Turtle
prov_ttl = manager.export_prov_o("apple_inc", format="turtle")

# Export full provenance graph
manager.export_all(path="provenance.ttl", format="turtle")
```

---

## Integration with Other Modules

Provenance is automatically tracked when using `GraphBuilderWithProvenance`:

```python
from semantica.kg import GraphBuilderWithProvenance

builder = GraphBuilderWithProvenance(provenance=True)
result = builder.build_single_source(graph_data)

# The builder records what was used to produce each node/edge
lineage = result.provenance_manager.get_lineage("entity_id")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Change Management" icon="clock-rotate-left" href="change_management">
    Version control and audit trails.
  </Card>
  <Card title="Ingest" icon="database" href="ingest">
    Provenance begins at ingestion.
  </Card>
  <Card title="Export" icon="file-export" href="export">
    Include provenance in exports.
  </Card>
  <Card title="Context" icon="brain" href="context">
    Decision provenance via AgentContext.
  </Card>
</CardGroup>
