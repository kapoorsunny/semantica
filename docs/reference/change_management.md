---
title: "Change Management Module"
description: "Enterprise-grade version control, SHA-256 checksums, and audit trails for knowledge graphs."
icon: "clock-rotate-left"
---

> Version control and audit trails for knowledge graphs with data integrity verification.

---

## Overview

The **Change Management Module** provides version control for knowledge graphs — SHA-256 checksums, full snapshot history, diff analysis, and rollback protection.

---

## TemporalVersionManager

```python
from semantica.change_management import TemporalVersionManager

manager = TemporalVersionManager(storage_path="versions.db")

# Create a snapshot
snapshot_id = manager.create_snapshot(
    graph=kg,
    version="v1.0",
    author="user@example.com",
    message="Initial knowledge graph"
)

print(f"Snapshot {snapshot_id} — checksum: {manager.get_checksum(snapshot_id)}")
```

---

## Versioning

```python
# List all versions
versions = manager.list_versions()
for v in versions:
    print(f"{v.version} — {v.author} — {v.created_at} — {v.checksum[:8]}...")

# Get a specific version
kg_v1 = manager.get_version("v1.0")

# Rollback to a previous version
manager.rollback(target_version="v1.0", allow_data_loss=False)
```

---

## Diff Analysis

```python
diff = manager.diff("v1.0", "v2.0")

print(f"Added nodes: {len(diff.added_nodes)}")
print(f"Removed nodes: {len(diff.removed_nodes)}")
print(f"Modified edges: {len(diff.modified_edges)}")

for change in diff.changes:
    print(f"  [{change.type}] {change.element}: {change.description}")
```

---

## Integrity Verification

```python
# Verify current graph against stored checksum
is_valid = manager.verify_integrity(kg, version="v2.0")

if not is_valid:
    print("Warning: Graph has been modified since v2.0 was created")
```

SHA-256 checksums are computed over the serialized graph to detect unauthorized modifications.

---

## Audit Trail

```python
# Full audit trail for an entity
trail = manager.get_audit_trail(entity_id="apple_inc")
for entry in trail:
    print(f"{entry.timestamp} — {entry.author}: {entry.action} — {entry.description}")

# Export audit trail
manager.export_audit_trail("audit.csv", format="csv")
manager.export_audit_trail("audit.json", format="json")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Provenance" icon="link" href="provenance">
    W3C PROV-O lineage tracking.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The graph being versioned.
  </Card>
  <Card title="Export" icon="file-export" href="export">
    Export versioned snapshots.
  </Card>
  <Card title="Conflicts" icon="triangle-exclamation" href="conflicts">
    Detect conflicts introduced between versions.
  </Card>
</CardGroup>
