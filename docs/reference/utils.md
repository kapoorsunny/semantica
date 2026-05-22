---
title: "Utils Module"
description: "Shared utilities for logging, validation, error handling, progress tracking, and common operations."
icon: "wrench"
---

> Internal utilities used across all Semantica modules — logging, validation, error handling, and helpers.

---

## Overview

The Utils module provides shared infrastructure used throughout Semantica. You typically won't call it directly, but its APIs are available when you need fine-grained control.

<CardGroup cols={3}>
  <Card title="Logging" icon="terminal">
    Structured logging with performance decorators and quality tracking.
  </Card>
  <Card title="Error Handling" icon="circle-exclamation">
    Custom exception hierarchy and standardized error formatting.
  </Card>
  <Card title="Validation" icon="circle-check">
    Data validation for entities, relationships, and configuration.
  </Card>
  <Card title="Progress Tracking" icon="clock">
    Track long-running operations in console, Jupyter, or file output.
  </Card>
  <Card title="Helpers" icon="toolbox">
    Text cleaning, hashing, and safe file operations.
  </Card>
  <Card title="Type Definitions" icon="code">
    Shared TypedDicts and Enums for type safety across modules.
  </Card>
</CardGroup>

---

## Logging

```python
from semantica.utils import setup_logging, get_logger, log_performance

setup_logging(level="INFO")   # "DEBUG" | "INFO" | "WARNING" | "ERROR"
logger = get_logger(__name__)

@log_performance
def process_data(data):
    logger.info(f"Processing {len(data)} items")
```

```bash
export SEMANTICA_LOG_LEVEL=DEBUG
export SEMANTICA_LOG_FORMAT=json     # "json" | "text"
export SEMANTICA_PROGRESS_BAR=true
```

---

## Validation

```python
from semantica.utils import validate_entity, validate_config, ValidationError

try:
    validate_entity({"id": "1", "type": "PERSON", "text": "Alice"})
except ValidationError as e:
    print(f"Invalid entity: {e}")
```

| Function | Description |
|----------|-------------|
| `validate_entity(data)` | Check entity structure |
| `validate_config(cfg)` | Check configuration dict |

---

## Progress Tracking

```python
from semantica.utils import track_progress

for item in track_progress(items, desc="Processing documents"):
    process(item)
```

Supports console (tqdm), Jupyter notebooks, and file logging automatically.

---

## Helper Functions

```python
from semantica.utils import clean_text, hash_data, safe_filename

clean  = clean_text("  Hello   World  ")   # "Hello World"
uid    = hash_data({"key": "value"})        # SHA-256 hex digest
fname  = safe_filename("My File?.txt")      # "My_File_.txt"
```

---

## Exception Hierarchy

```python
from semantica.utils import SemanticaError, ValidationError, ProcessingError

try:
    ...
except ValidationError as e:
    # Input data did not pass validation
    ...
except ProcessingError as e:
    # Failure during extraction or graph construction
    ...
except SemanticaError as e:
    # Catch-all for all framework errors
    ...
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Core" icon="gear" href="core">
    Framework orchestration that uses Utils internally.
  </Card>
  <Card title="Pipeline" icon="arrows-turn-to-dots" href="pipeline">
    Uses ProgressTracker for step-level tracking.
  </Card>
</CardGroup>
