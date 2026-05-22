---
title: "Ontology Module"
description: "Automated ontology generation, SHACL validation, SKOS vocabularies, alignment, diff/migration, and the visual Ontology Hub."
icon: "sitemap"
---

> Automated ontology generation, validation, and management system.

---

## Overview

The **Ontology Module** provides the full lifecycle for knowledge graph schemas — from auto-generation and SHACL validation to visual editing in the Ontology Hub (v0.5.0).

<Tip>
  **When to use:** Schema design (defining KG structure), data modeling (formalizing domain concepts), interoperability (semantic web standards), and SHACL-based data quality validation.
</Tip>

---

## OntologyManager

```python
from semantica.ontology import OntologyManager

ontology = OntologyManager()
ontology.add_class("Person", properties=["name", "birth_date"])
ontology.add_class("Organization", properties=["name", "founded_date"])
ontology.add_relationship("works_for", domain="Person", range="Organization")
ontology.add_constraint("Person", "must_have_name")

is_valid = ontology.validate_graph(kg)
owl_ttl = ontology.export_owl(format="turtle")
```

---

## Auto-Generation (6-Stage Pipeline)

Generate an ontology automatically from your knowledge graph data.

```python
from semantica.ontology import OntologyGenerator

generator = OntologyGenerator()
ontology = generator.generate_from_graph(kg)
```

The pipeline runs through these stages:

1. **Semantic Network Parsing** — extract concepts and patterns from entity/relationship data
2. **YAML-to-Definition** — transform patterns into intermediate class definitions
3. **Definition-to-Types** — map definitions to OWL types (`owl:Class`, `owl:ObjectProperty`)
4. **Hierarchy Generation** — build taxonomy trees using transitive closure and cycle detection
5. **TTL Generation** — serialize to Turtle format using `rdflib`
6. **Quality Evaluation** — assess coverage, completeness, and granularity metrics

---

## SHACL Validation

```python
from semantica.ontology import SHACLGenerator, SHACLValidator

# Generate SHACL shapes from an ontology
generator = SHACLGenerator()
shapes = generator.generate(ontology)
shapes_ttl = shapes.serialize(format="turtle")

# Validate a graph against shapes
validator = SHACLValidator()
report = validator.validate(kg, shapes=shapes)

if not report.conforms:
    for violation in report.violations:
        print(f"Violation: {violation.message} on {violation.node}")
```

---

## SKOS Vocabularies

```python
from semantica.ontology import SKOSVocabulary

vocab = SKOSVocabulary()
vocab.add_concept("Machine Learning", broader="Artificial Intelligence")
vocab.add_concept("Deep Learning", broader="Machine Learning")
vocab.add_alt_label("ML", for_concept="Machine Learning")

skos_ttl = vocab.export(format="turtle")
```

---

## Ontology Alignment

```python
from semantica.ontology import OntologyAligner

aligner = OntologyAligner()
alignment = aligner.align(source_ontology, target_ontology)

for mapping in alignment.mappings:
    print(f"{mapping.source} → {mapping.target} (confidence: {mapping.confidence:.2f})")

merged = aligner.merge(source_ontology, target_ontology, alignment)
```

---

## Diff & Migration

```python
from semantica.ontology import OntologyDiff, OntologyMigrator

diff = OntologyDiff()
changes = diff.compare(ontology_v1, ontology_v2)

for change in changes:
    print(f"{change.type}: {change.element} — {change.description}")

migrator = OntologyMigrator()
migration_script = migrator.generate_migration(changes)
migrator.apply(kg, migration_script)
```

---

## OWL/RDF Export

```python
from semantica.ontology import OWLExporter

exporter = OWLExporter()
exporter.export(ontology, path="ontology.ttl", format="turtle")
exporter.export(ontology, path="ontology.xml",  format="xml")
exporter.export(ontology, path="ontology.json", format="json-ld")
```

---

## Ontology Hub (v0.5.0)

The Ontology Hub is a visual browser UI for the full ontology lifecycle, available via `semantica.explorer`.

```bash
pip install semantica[explorer]
```

```python
from semantica.explorer import start_explorer

start_explorer(graph=kg, port=8080)
# Opens at http://localhost:8080 — navigate to the Ontology Hub tab
```

Features:
- **Visual Editor** — create and edit classes, properties, and relationships in the browser
- **SHACL Studio** — author and validate SHACL shapes visually
- **Alignment Authoring** — map concepts across ontologies with drag-and-drop
- **Health Dashboard** — coverage, completeness, and granularity metrics
- **Version Control** — track ontology changes with diff visualization

---

## See Also

<CardGroup cols={2}>
  <Card title="Reasoning" icon="microchip" href="reasoning">
    Apply inference rules over ontology axioms.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The graph being modeled by the ontology.
  </Card>
  <Card title="Export" icon="file-export" href="export">
    Export ontologies as RDF, OWL, or JSON-LD.
  </Card>
  <Card title="Conflicts" icon="triangle-exclamation" href="conflicts">
    Detect ontology constraint violations.
  </Card>
</CardGroup>
