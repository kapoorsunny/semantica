---
title: "Evals Module"
description: "Evaluation framework for measuring Knowledge Graph quality, extraction accuracy, and pipeline performance."
icon: "chart-line"
---

> Measure and benchmark Knowledge Graph quality, extraction accuracy, and pipeline performance.

<Warning>
  **Coming Soon** — This module is currently in active development. Documentation will be available in an upcoming release.
</Warning>

---

## Planned Capabilities

The Evals module will provide a comprehensive evaluation framework covering:

| Area | What It Measures |
|------|-----------------|
| **KG Quality** | Completeness, consistency, schema compliance |
| **Extraction Accuracy** | NER precision/recall/F1, relation extraction metrics |
| **Pipeline Performance** | Throughput, latency, error rates per step |
| **Deduplication** | Merge accuracy, false positive/negative rates |
| **Reasoning** | Inference correctness, rule coverage |

---

## See Also

<CardGroup cols={2}>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Extraction module to evaluate.
  </Card>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    Graph quality assessment.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Pipeline performance metrics.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Deduplication accuracy evaluation.
  </Card>
</CardGroup>
