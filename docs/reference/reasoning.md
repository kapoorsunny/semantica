---
title: "Reasoning Module"
description: "Forward chaining, Rete, deductive, abductive, SPARQL, and Datalog reasoning with explainable inference paths."
icon: "microchip"
---

> Logical inference engine supporting rule-based inference, SPARQL, Rete, and Datalog reasoning.

---

## Overview

The **Reasoning Module** derives new knowledge from existing facts using logical rules. All engines produce **explainable inference paths** — not black-box conclusions.

<CardGroup cols={2}>
  <Card title="Rule-Based Inference" icon="brain">
    Forward-chaining inference with variable substitution.
  </Card>
  <Card title="SPARQL Reasoning" icon="database">
    Query expansion and property chain inference over RDF graphs.
  </Card>
  <Card title="Rete Algorithm" icon="bolt">
    High-performance pattern matching for large rule sets.
  </Card>
  <Card title="Datalog Engine" icon="code">
    Recursive Horn clause rules with bottom-up fixpoint semantics (v0.4.0).
  </Card>
</CardGroup>

---

## ReasoningEngine (Forward Chaining)

```python
from semantica.reasoning import ReasoningEngine

engine = ReasoningEngine()
engine.add_rule({
    "if": [
        {"subject": "?person", "predicate": "parent_of", "object": "?child"},
        {"subject": "?child",  "predicate": "parent_of", "object": "?grandchild"}
    ],
    "then": {"subject": "?person", "predicate": "grandparent_of", "object": "?grandchild"}
})

inferences = engine.infer(kg)
for inf in inferences:
    print(f"{inf['subject']} {inf['predicate']} {inf['object']}")
    print(f"  Derived via: {inf['explanation']}")
```

---

## ReteEngine (High Performance)

```python
from semantica.reasoning import ReteEngine

engine = ReteEngine()
engine.load_rules("rules/domain_rules.json")
results = engine.run(kg)
```

The Rete algorithm efficiently evaluates large rule sets by caching partial matches — far faster than naive forward chaining for hundreds of rules.

---

## DeductiveEngine

```python
from semantica.reasoning import DeductiveEngine

engine = DeductiveEngine()
engine.add_axiom("Person", "is_a", "Agent")
engine.add_axiom("Employee", "is_a", "Person")

# Infer: Employee is_a Agent (transitivity)
inferences = engine.close_under_transitivity(kg)
```

---

## AbductiveEngine

```python
from semantica.reasoning import AbductiveEngine

engine = AbductiveEngine()
hypotheses = engine.explain(
    observation=("apple_inc", "high_revenue", True),
    knowledge_graph=kg
)

for h in hypotheses:
    print(f"Hypothesis: {h['explanation']} (probability: {h['probability']:.2f})")
```

Abductive reasoning infers the most likely explanation for an observation given the current knowledge graph.

---

## DatalogEngine (v0.4.0)

Pure-Python bottom-up semi-naive fixpoint evaluation for recursive Horn clause rules.

```python
from semantica.reasoning import DatalogEngine

datalog = DatalogEngine()

# Add facts
datalog.add_fact("parent(alice, bob).")
datalog.add_fact("parent(bob, charlie).")

# Add recursive rule
datalog.add_rule("ancestor(X, Z) :- parent(X, Y), ancestor(Y, Z).")
datalog.add_rule("ancestor(X, Y) :- parent(X, Y).")

# Query
results = datalog.query("ancestor(alice, ?)")
# Returns: [("charlie",), ("bob",)]
```

<Note>
  Datalog termination is guaranteed — the engine detects fixpoint convergence and stops. No infinite loops.
</Note>

---

## SPARQLReasoner

```python
from semantica.reasoning import SPARQLReasoner

reasoner = SPARQLReasoner(graph=rdf_graph)

query = """
SELECT ?person ?company WHERE {
    ?person :founded ?company .
    ?company :located_in :SiliconValley .
}
"""

results = reasoner.query(query)
```

Also supports property chain inference:

```python
reasoner.add_property_chain("knows", ["friend_of", "colleague_of"])
inferences = reasoner.infer_property_chains()
```

---

## Built-In Rule Templates

```python
from semantica.reasoning import ReasoningEngine, RuleTemplates

engine = ReasoningEngine()

# Apply common logical patterns
engine.apply_template(RuleTemplates.TRANSITIVITY, predicate="located_in")
engine.apply_template(RuleTemplates.SYMMETRY, predicate="knows")
engine.apply_template(RuleTemplates.INVERSE, predicate1="parent_of", predicate2="child_of")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Knowledge Graph" icon="diagram-project" href="kg">
    The knowledge graph being reasoned over.
  </Card>
  <Card title="Ontology" icon="sitemap" href="ontology">
    Ontology rules that constrain reasoning.
  </Card>
  <Card title="SPARQL / Triplet Store" icon="database" href="triplet_store">
    RDF backend for SPARQL reasoning.
  </Card>
  <Card title="Context" icon="brain" href="context">
    Uses reasoning for agent intelligence.
  </Card>
</CardGroup>
