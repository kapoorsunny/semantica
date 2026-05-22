---
title: "Glossary"
description: "Reference of terms and concepts used throughout Semantica."
icon: "book"
---

<Tip>
  Use Ctrl+F to search this page.
</Tip>

---

## Core Concepts

**Agent** — An autonomous AI system that can perceive its environment, reason about information, and take actions to achieve specific goals. In Semantica, agents use knowledge graphs for memory and reasoning.

**Entity** — A distinct object or concept in the real world, such as a person, place, organization, or event. Entities are the fundamental building blocks of knowledge graphs.

**Knowledge Graph (KG)** — A structured representation of knowledge using entities (nodes) and relationships (edges). KGs enable reasoning, querying, and semantic analysis of data.

**Relationship** — A connection between two entities that describes how they relate to each other (e.g., `works_for`, `located_in`, `founded_by`).

**Semantic** — Relating to meaning in language or logic. Semantic understanding goes beyond keywords to comprehend context and intent.

---

## Data Processing

**Ingestion** — The process of loading data from various sources (files, databases, APIs, streams) into a system for processing.

**Normalization** — The process of standardizing data into a consistent format (e.g., converting dates to ISO format, standardizing entity names).

**Parsing** — Extracting structured information from unstructured or semi-structured documents like PDFs, Word documents, or web pages.

**Chunking** — Breaking down large documents into smaller, manageable pieces while preserving context and meaning.

---

## Artificial Intelligence

**LLM (Large Language Model)** — A type of artificial intelligence model trained on vast amounts of text data, capable of understanding and generating human-like text.

**RAG (Retrieval Augmented Generation)** — A technique that enhances LLM responses by retrieving relevant information from a knowledge base before generating an answer.

**GraphRAG (Graph-Augmented Retrieval Augmented Generation)** — An advanced RAG approach that combines vector search with knowledge graph traversal to provide more accurate and contextually relevant information to LLMs.

**Inference** — The process of deriving new facts or conclusions from existing knowledge using logical rules.

---

## Knowledge Graph Components

**Node** — A vertex in a graph representing an entity or concept.

**Edge** — A connection between two nodes representing a relationship.

**Property** — An attribute or characteristic of an entity or relationship (e.g., name, date, confidence score).

**Triplet** — A basic unit of knowledge in RDF, consisting of a subject, predicate, and object (e.g., `<Apple_Inc> <founded_by> <Steve_Jobs>`).

**Temporal Graph** — A knowledge graph that tracks changes over time, allowing queries about the state of the graph at specific time points. Semantica's temporal model uses `valid_from`/`valid_until` on nodes and edges.

**BiTemporalFact** — A fact with both a valid time (when it was true in the world) and a transaction time (when it was recorded in the system).

**Allen Interval Algebra** — A system of 13 relations for temporal ordering of intervals (before, after, meets, overlaps, during, starts, finishes, equals, and their inverses). Supported since v0.4.0.

---

## Entity Recognition & Extraction

**Named Entity Recognition (NER)** — The process of identifying and classifying named entities in text into predefined categories such as persons, organizations, locations, dates, and more.

**Relationship Extraction** — The task of identifying and extracting semantic relationships between entities in text.

**Entity Resolution** — The process of determining when two entity mentions refer to the same real-world entity, also known as entity linking or deduplication.

**Coreference Resolution** — The task of determining when two or more expressions in text refer to the same entity (e.g., "Apple" and "the company" referring to Apple Inc.).

**Event Detection** — The task of identifying and classifying events (e.g., acquisitions, partnerships, announcements) in text.

---

## Ontology & Schema

**Ontology** — A formal specification of concepts, relationships, and constraints in a domain, typically expressed in OWL (Web Ontology Language).

**Ontology Hub** — Semantica's v0.5.0 visual browser UI for the full ontology lifecycle: visual editor, SHACL Studio, alignment authoring, health dashboard, and version control.

**Class** — In ontologies, a category or type of entity (e.g., `Person`, `Organization`, `Location`).

**Axiom** — A statement or rule that is accepted as true without proof, used in ontologies to define logical constraints and relationships.

**OWL (Web Ontology Language)** — A W3C standard language for defining and instantiating ontologies on the web.

**SHACL (Shapes Constraint Language)** — A W3C standard for validating RDF graphs against a set of shapes (constraints). Semantica can auto-generate and validate SHACL shapes.

**SKOS (Simple Knowledge Organization System)** — A W3C standard for representing controlled vocabularies, taxonomies, and thesauri.

---

## Data Storage & Retrieval

**Embedding** — A dense vector representation of text, images, or other data that captures semantic meaning in a continuous vector space. Used for similarity search and semantic matching.

**Vector Store** — A database optimized for storing and searching high-dimensional vectors, used for semantic similarity search.

**Triplet Store** — A database designed specifically for storing and querying RDF triplets.

**Graph Database** — A database designed specifically for storing and querying graph-structured data.

**Hybrid Search** — A search strategy that combines multiple retrieval methods, typically vector search and keyword search, to improve accuracy.

---

## Graph Analytics

**Centrality** — A measure of the importance or influence of a node in a graph. Common metrics include PageRank, betweenness, and closeness centrality.

**PageRank** — An algorithm used to measure the importance of nodes in a graph based on the structure of incoming links.

**Community Detection** — The process of identifying groups or clusters of densely connected nodes in a graph.

**Distance Intelligence** — Semantica's v0.5.0 feature for semantic neighborhood exploration: N×N distance matrices, ego-mode visualization, and distance band classification.

**Distance Band** — A classification of a node's proximity to a target: `near`, `mid`, or `far`, based on semantic embedding distance thresholds.

---

## Query Languages

**Cypher** — A declarative query language for graph databases, particularly Neo4j.

**SPARQL** — A query language for RDF data, similar to SQL for relational databases.

**RDF (Resource Description Framework)** — A W3C standard for representing information about resources in the form of subject-predicate-object triplets.

**Datalog** — A declarative logic programming language used for knowledge base queries. Semantica's DatalogEngine supports recursive Horn clause rules with bottom-up semi-naive fixpoint semantics (v0.4.0).

---

## Data Quality

**Conflict Resolution** — The process of handling contradictory information from multiple sources in a knowledge graph.

**Deduplication** — The process of identifying and removing duplicate records or entities from a dataset.

**Data Provenance** — Information about the origin, history, and lineage of data, including sources, timestamps, and transformations.

**W3C PROV-O** — The W3C standard ontology for provenance. Semantica tracks lineage across all 17 modules in a PROV-O compliant format.

---

## Technical Terms

**API (Application Programming Interface)** — A set of functions and protocols that allow different software applications to communicate with each other.

**OCR (Optical Character Recognition)** — Technology that converts images of text (e.g., scanned documents, photos) into machine-readable text.

**Pipeline** — A sequence of data processing steps that transform raw data into a desired output format.

**Vector** — A mathematical representation of data as an array of numbers, used in embeddings to capture semantic meaning.

**XXE (XML External Entity)** — A security vulnerability in XML parsers. Semantica's `XMLIngestor` (v0.5.0) uses an XXE-safe lxml backend.

**SSRF (Server-Side Request Forgery)** — A security vulnerability where a server can be induced to make requests to unintended destinations. Semantica validates `base_url` at construction time to prevent SSRF.

---

## See Also

- [Core Concepts](concepts) — deeper explanation of key ideas
- [Getting Started](getting-started) — first steps
- [Modules Guide](modules) — every module explained
- [API Reference](reference/context) — technical reference
