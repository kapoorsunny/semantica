---
title: "Export Module"
description: "Export knowledge graphs to RDF (Turtle, JSON-LD, N-Triples, XML), Parquet, ArangoDB AQL, OWL, and CSV."
icon: "file-export"
---

> Export knowledge graphs and data to multiple formats with W3C-compliant serialization.

---

## RDFExporter

```python
from semantica.export import RDFExporter

exporter = RDFExporter()

# Turtle
rdf = exporter.export_to_rdf(graph, format="turtle")
exporter.export_to_file(graph, "output.ttl", format="turtle")

# JSON-LD
rdf = exporter.export_to_rdf(graph, format="json-ld")

# N-Triples
rdf = exporter.export_to_rdf(graph, format="nt")

# RDF/XML
rdf = exporter.export_to_rdf(graph, format="xml")
```

---

## OWL Exporter

```python
from semantica.export import OWLExporter

exporter = OWLExporter()
exporter.export(ontology, path="ontology.ttl", format="turtle")
exporter.export(ontology, path="ontology.owl", format="xml")
```

---

## Parquet Exporter

For Spark, BigQuery, and Databricks pipelines.

```python
from semantica.export import ParquetExporter

exporter = ParquetExporter()

# Export nodes
exporter.export_nodes(graph, "nodes.parquet")

# Export edges
exporter.export_edges(graph, "edges.parquet")

# Export full graph (partitioned)
exporter.export(graph, output_dir="graph_parquet/", partition_by="node_type")
```

---

## ArangoDB AQL Exporter

```python
from semantica.export import ArangoExporter

exporter = ArangoExporter()
aql = exporter.export(graph)  # returns ready-to-run INSERT statements
exporter.export_to_file(graph, "arango_import.aql")
```

---

## CSV Exporter

```python
from semantica.export import CSVExporter

exporter = CSVExporter()
exporter.export_nodes(graph, "nodes.csv")
exporter.export_edges(graph, "edges.csv")
```

---

## GraphML Exporter

```python
from semantica.export import GraphMLExporter

exporter = GraphMLExporter()
exporter.export(graph, "graph.graphml")
```

---

## Selective Export

```python
# Export subgraph by node IDs
subgraph = graph.subgraph(node_ids=["apple_inc", "steve_jobs"])
exporter.export_to_file(subgraph, "subgraph.ttl", format="turtle")

# Export by node type
org_nodes = graph.filter(node_type="Organization")
exporter.export_nodes(org_nodes, "organizations.parquet")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Triplet Store" icon="table" href="triplet_store">
    Store RDF exports in a SPARQL-queryable backend.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Export OWL ontologies.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    Include provenance in RDF exports.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Add export as a pipeline step.
  </Card>
</CardGroup>
