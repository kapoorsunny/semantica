---
title: "Seed Module"
description: "Seed data management for initializing Knowledge Graphs from trusted, verified sources."
icon: "database"
---

> Bootstrap Knowledge Graphs with verified taxonomies, reference data, and foundation graphs.

---

## Overview

The **Seed Module** provides a system for initializing Knowledge Graphs with verified, structured data from trusted sources — enabling you to start with a reliable foundation rather than an empty graph.

<CardGroup cols={3}>
  <Card title="Multi-Source Loading" icon="database">
    Load seed data from CSV, JSON, databases, and APIs.
  </Card>
  <Card title="Foundation Graph" icon="diagram-project">
    Build a reliable KG foundation to bootstrap extraction.
  </Card>
  <Card title="Data Integration" icon="code-merge">
    Merge seed data with extracted data using configurable strategies.
  </Card>
  <Card title="Validation" icon="circle-check">
    Validate seed data quality and schema compliance.
  </Card>
  <Card title="Versioning" icon="code-branch">
    Manage and track versions of seed data sources.
  </Card>
  <Card title="Export" icon="file-export">
    Export seed data to standard formats.
  </Card>
</CardGroup>

<Tip>
**When to use the Seed Module:**
- **Bootstrapping** — you have existing structured data (taxonomies, user lists, product catalogs) and want to build on them.
- **Reference data** — loading immutable reference information (countries, codes, constants).
- **Testing** — loading consistent datasets for development and CI.
</Tip>

---

## SeedDataManager

```python
from semantica.seed import SeedDataManager

manager = SeedDataManager()
manager.register_source("countries", "csv", "data/countries.csv")
foundation_kg = manager.create_foundation_graph()
```

| Method | Description |
|--------|-------------|
| `register_source(name, format, location)` | Add a data source |
| `create_foundation_graph()` | Build KG from registered sources |
| `validate_quality(seed_data)` | Check data quality |
| `integrate_with_extracted(seed, extracted)` | Merge seed and extracted graphs |
| `export_seed_data(path, format)` | Export seed data |

---

## SeedDataSource

```python
from semantica.seed import SeedDataSource

source = SeedDataSource(
    name="taxonomy",
    type="json",        # "csv" | "json" | "api" | "sql"
    path="taxonomy.json",
    config={"encoding": "utf-8"}
)
```

---

## Merge Strategies

```python
final_kg = manager.integrate_seed_extracted(
    seed_graph=foundation_kg,
    extracted_data=new_data,
    strategy="seed_first"   # "seed_first" | "extracted_first" | "smart_merge"
)
```

| Strategy | Behavior |
|----------|----------|
| `seed_first` | Seed data overrides extracted data |
| `extracted_first` | Extracted data overrides seed data |
| `smart_merge` | Property-level merging with conflict resolution |

---

## Bootstrapping a KG

```python
from semantica.seed import SeedDataManager
from semantica.ingest import FileIngestor

# Load foundation from verified data
manager = SeedDataManager()
manager.register_source("taxonomy", "json", "taxonomy.json")
foundation_kg = manager.create_foundation_graph()

# Ingest and merge new data
ingestor = FileIngestor()
new_data = ingestor.ingest("news_articles.pdf")

final_kg = manager.integrate_seed_extracted(
    seed_graph=foundation_kg,
    extracted_data=new_data,
    strategy="seed_first"
)
```

---

## Configuration

```yaml
seed:
  sources:
    - name: "employees"
      type: "csv"
      path: "./data/employees.csv"
  merge:
    strategy: "seed_first"
  validation:
    strict: true
```

```bash
export SEED_DATA_DIR=./data/seed
export SEED_MERGE_STRATEGY=seed_first
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Ingest" icon="file-import" href="ingest">
    Load unstructured data alongside seed data.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The target graph structure.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Handle duplicates during merge.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Incorporate seed loading in a pipeline.
  </Card>
</CardGroup>
