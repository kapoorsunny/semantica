---
title: "Pipeline Module"
description: "Pipeline DSL with parallel workers, retry policies, failure handling, and progress tracking."
icon: "gear"
---

> Robust orchestration engine for building and executing complex data processing workflows.

---

## Overview

The **Pipeline Module** lets you chain Semantica components into reproducible, fault-tolerant workflows with parallel execution and configurable error handling.

---

## Basic Pipeline

```python
from semantica.pipeline import Pipeline
from semantica.ingest import FileIngestor
from semantica.parse import DocumentParser
from semantica.semantic_extract import NERExtractor
from semantica.kg import GraphBuilder

pipeline = Pipeline()
pipeline.add_step("ingest",   FileIngestor())
pipeline.add_step("parse",    DocumentParser())
pipeline.add_step("extract",  NERExtractor(method="llm", llm_provider=llm))
pipeline.add_step("build_kg", GraphBuilder(merge_entities=True))

result = pipeline.run("data/")
kg = result.output
```

---

## Parallel Processing

```python
pipeline = Pipeline(workers=4)   # run steps in parallel across documents

pipeline.add_step("ingest",  FileIngestor())
pipeline.add_step("parse",   DocumentParser())
pipeline.add_step("extract", NERExtractor(), parallel=True, batch_size=10)
pipeline.add_step("build",   GraphBuilder())

result = pipeline.run("data/")
```

---

## Retry & Error Handling

```python
from semantica.pipeline import Pipeline, RetryPolicy, FailureHandler

retry = RetryPolicy(
    max_retries=3,
    backoff="exponential",   # "fixed" | "linear" | "exponential"
    initial_delay=1.0
)

handler = FailureHandler(
    strategy="skip",         # "skip" | "stop" | "retry"
    log_failures=True
)

pipeline = Pipeline(retry_policy=retry, failure_handler=handler)
```

---

## Progress Tracking

```python
# Print progress to console
result = pipeline.run("data/", show_progress=True)

# WebSocket progress (via Knowledge Explorer)
result = pipeline.run("data/", websocket_port=8080)

print(f"Processed: {result.processed_count}")
print(f"Failed: {result.failed_count}")
print(f"Duration: {result.duration_seconds:.1f}s")
```

---

## Pipeline DSL

```python
from semantica.pipeline import PipelineBuilder

pipeline = (
    PipelineBuilder()
    .ingest(FileIngestor())
    .parse(DocumentParser())
    .normalize()
    .extract(NERExtractor(method="llm", llm_provider=llm))
    .extract_relations(RelationExtractor(method="llm", llm_provider=llm))
    .build_kg(merge_entities=True)
    .deduplicate(strategy="semantic_v2")
    .export(format="turtle", path="output.ttl")
    .build()
)

result = pipeline.run("data/")
```

---

## Saving & Loading Pipelines

```python
# Save pipeline definition
pipeline.save("pipeline_config.yaml")

# Load and run
pipeline = Pipeline.load("pipeline_config.yaml")
result = pipeline.run("data/")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Ingest" icon="database" href="ingest">
    First step in most pipelines.
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Core extraction step.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    Graph construction step.
  </Card>
  <Card title="Export" icon="file-export" href="export">
    Final output step.
  </Card>
</CardGroup>
