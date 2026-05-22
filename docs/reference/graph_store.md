---
title: "Graph Store Module"
description: "Unified interface for Neo4j, FalkorDB, Apache AGE, and Amazon Neptune graph databases."
icon: "server"
---

> Unified interface for property graph databases.

---

## Overview

The **Graph Store Module** provides a single API for persisting and querying knowledge graphs in production graph databases.

Backends: **Neo4j**, **FalkorDB**, **Apache AGE** (PostgreSQL), **Amazon Neptune**, and in-memory **NetworkX** for development.

---

## Basic Usage

```python
from semantica.graph_store import GraphStore

store = GraphStore(backend="neo4j", uri="bolt://localhost:7687", user="neo4j", password="password")

store.add_nodes(entities)
store.add_edges(relationships)

results = store.query("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10")
```

---

## Backends

<Tabs>
  <Tab title="Neo4j">
    ```python
    store = GraphStore(
        backend="neo4j",
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password",
        database="neo4j"     # optional, default database
    )
    ```
  </Tab>
  <Tab title="FalkorDB">
    ```python
    store = GraphStore(
        backend="falkordb",
        host="localhost",
        port=6379,
        graph_name="semantica"
    )
    ```
  </Tab>
  <Tab title="Apache AGE">
    ```python
    store = GraphStore(
        backend="apache_age",
        connection_string="postgresql://user:pass@localhost/graphdb",
        graph_name="semantica"
    )
    ```
    See the [Apache AGE Guide](../graph_stores/apache_age) for setup.
  </Tab>
  <Tab title="In-Memory">
    ```python
    store = GraphStore(backend="networkx")
    ```
    For development and testing only — data is not persisted.
  </Tab>
</Tabs>

---

## Querying

```python
# Cypher (Neo4j, FalkorDB)
results = store.query(
    "MATCH (p:Person)-[:WORKS_FOR]->(o:Organization) WHERE o.name = $org RETURN p",
    parameters={"org": "Apple Inc."}
)

# Path traversal
paths = store.find_paths(
    start_node="steve_jobs",
    end_node="apple_inc",
    max_hops=3,
    relationship_types=["FOUNDED", "WORKED_AT"]
)
```

---

## Graph Operations

```python
# Add a single node
store.add_node("apple_inc", node_type="Organization", properties={"founded": 1976})

# Add a relationship
store.add_edge("steve_jobs", "apple_inc", "FOUNDED", properties={"year": 1976})

# Bulk operations
store.add_nodes_bulk(entities, batch_size=1000)
store.add_edges_bulk(relationships, batch_size=1000)

# Delete
store.delete_node("node_id")
store.delete_edge("edge_id")

# Get neighbors
neighbors = store.get_neighbors("apple_inc", relationship_type="HAS_EMPLOYEE", direction="in")
```

---

## Schema Management

```python
# Create indexes for performance
store.create_index(label="Person", property="name")
store.create_constraint(label="Organization", property="id", constraint_type="unique")

# Get schema
schema = store.get_schema()
```

---

## See Also

<CardGroup cols={2}>
  <Card title="KG Module" icon="diagram-project" href="kg">
    Build the graph before persisting it.
  </Card>
  <Card title="Apache AGE Guide" icon="database" href="../graph_stores/apache_age">
    PostgreSQL-based graph storage setup.
  </Card>
  <Card title="Triplet Store" icon="table" href="triplet_store">
    RDF triple store for semantic web.
  </Card>
  <Card title="Visualization" icon="chart-bar" href="visualization">
    Visualize stored graphs.
  </Card>
</CardGroup>
