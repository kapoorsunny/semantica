---
title: "Triplet Store Module"
description: "RDF triple storage with SPARQL queries and bulk loading — Blazegraph, Apache Jena, and RDF4J."
icon: "table"
---

> Store and query RDF triplets with SPARQL support.

---

## Overview

The **Triplet Store Module** provides W3C-standard RDF storage with full SPARQL query support. Use it when you need semantic web compatibility, OWL reasoning, or SPARQL-based queries.

Backends: **Blazegraph**, **Apache Jena (Fuseki)**, **RDF4J**.

---

## Basic Usage

```python
from semantica.triplet_store import TripletStore

store = TripletStore(
    backend="blazegraph",
    endpoint="http://localhost:9999/blazegraph/sparql"
)

# Add triplets
store.add_triplet(
    subject="http://example.org/apple_inc",
    predicate="http://example.org/founded_by",
    obj="http://example.org/steve_jobs"
)

# Bulk load
store.add_triplets_bulk(triplets)
```

---

## SPARQL Queries

```python
# SELECT query
results = store.sparql("""
    PREFIX ex: <http://example.org/>
    SELECT ?person ?company WHERE {
        ?person ex:founded ?company .
        ?company ex:located_in ex:SiliconValley .
    }
""")

# CONSTRUCT query (returns graph)
graph = store.sparql_construct("""
    PREFIX ex: <http://example.org/>
    CONSTRUCT {
        ?s ex:connected_to ?o
    } WHERE {
        ?s ex:founded ?company .
        ?company ex:has_investor ?o .
    }
""")
```

---

## Backends

```python
# Blazegraph
store = TripletStore(
    backend="blazegraph",
    endpoint="http://localhost:9999/blazegraph/sparql",
    namespace="semantica"
)

# Apache Jena Fuseki
store = TripletStore(
    backend="jena",
    endpoint="http://localhost:3030/dataset/sparql",
    update_endpoint="http://localhost:3030/dataset/update"
)

# RDF4J
store = TripletStore(
    backend="rdf4j",
    server_url="http://localhost:8080/rdf4j-server",
    repository_id="semantica"
)
```

---

## Import / Export

```python
# Import from file
store.import_file("ontology.ttl", format="turtle")
store.import_file("data.jsonld", format="json-ld")

# Export to file
store.export("output.ttl", format="turtle")
store.export("output.nt",  format="nt")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Export" icon="file-export" href="export">
    Export to RDF formats.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Load OWL ontologies into a triplet store.
  </Card>
  <Card title="Reasoning" icon="microchip" href="reasoning">
    SPARQL-based reasoning.
  </Card>
  <Card title="Graph Store" icon="server" href="graph_store">
    Property graph alternative for Cypher queries.
  </Card>
</CardGroup>
