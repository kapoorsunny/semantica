---
title: "Core Module"
description: "Framework orchestration, lifecycle management, configuration, and plugin system."
icon: "gear"
---

> Framework infrastructure for complex workflows — lifecycle hooks, centralized config, and a plugin registry.

---

## Overview

The **Core Module** is the coordination layer for Semantica. For most tasks you should use individual modules directly; reach for Core when you need lifecycle management, centralized configuration, or multi-step orchestration.

<Tip>
**Use individual modules directly** (`semantica.ingest`, `semantica.kg`, etc.) for the vast majority of use cases. Use the `Semantica` orchestration class only when you need application-level lifecycle management or a plugin system.
</Tip>

<CardGroup cols={2}>
  <Card title="Semantica" icon="network-wired">
    Orchestration class for coordinating complex multi-module workflows.
  </Card>
  <Card title="ConfigManager" icon="sliders">
    Unified configuration loading, validation, and merging.
  </Card>
  <Card title="LifecycleManager" icon="rotate">
    Startup/shutdown hooks and system health monitoring.
  </Card>
  <Card title="PluginRegistry" icon="puzzle-piece">
    Dynamic plugin discovery, registration, and loading.
  </Card>
</CardGroup>

---

## Semantica (Orchestration)

```python
from semantica.core import Semantica, ConfigManager

config_manager = ConfigManager()
config = config_manager.load_from_file("config.yaml")

framework = Semantica(config=config)
framework.initialize()

try:
    result = framework.build_knowledge_base(
        sources=["doc1.pdf", "doc2.docx"],
        embeddings=True,
        graph=True,
    )
    status = framework.get_status()
    print(f"State: {status['state']}")
finally:
    framework.shutdown(graceful=True)
```

| Method | Description |
|--------|-------------|
| `initialize()` | Initialize all framework components |
| `build_knowledge_base(sources, **kwargs)` | Orchestrate KG construction |
| `run_pipeline(pipeline, data)` | Execute a processing pipeline |
| `get_status()` | System health and state |
| `shutdown(graceful=True)` | Graceful shutdown |

---

## ConfigManager

```python
from semantica.core import ConfigManager

manager = ConfigManager()
config = manager.load_from_file("config.yaml")

# Merge base + override configs
merged = manager.merge_configs(
    manager.load_from_file("base.yaml"),
    manager.load_from_file("prod.yaml"),
)

# Nested access
batch_size = config.get("processing.batch_size", default=16)
config.set("processing.batch_size", 64)
config.validate()
```

### YAML Configuration

```yaml
llm_provider:
  name: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}

processing:
  batch_size: 32
  max_workers: 4

quality:
  min_confidence: 0.7

logging:
  level: INFO
```

```bash
# Environment variable overrides (SEMANTICA_ prefix)
export SEMANTICA_PROCESSING_BATCH_SIZE=64
export SEMANTICA_LOG_LEVEL=DEBUG
```

---

## LifecycleManager

State machine: `UNINITIALIZED` → `INITIALIZING` → `READY` → `RUNNING` → `STOPPING` → `STOPPED`

```python
from semantica.core import LifecycleManager

manager = LifecycleManager()

def init_db():
    print("Initializing database...")

def cleanup_db():
    print("Closing database connections...")

manager.register_startup_hook(init_db,    priority=10)
manager.register_shutdown_hook(cleanup_db, priority=10)

manager.startup()

# Health monitoring
class DatabaseComponent:
    def health_check(self):
        return {"healthy": True, "message": "Connected"}

manager.register_component("database", DatabaseComponent())
summary = manager.get_health_summary()

manager.shutdown(graceful=True)
```

Lower `priority` values execute first during startup; higher values execute first during shutdown.

---

## PluginRegistry

```python
from semantica.core import PluginRegistry

class MyPlugin:
    def initialize(self):
        print("Plugin initialized")

    def execute(self, data):
        return {"processed": True}

registry = PluginRegistry(plugin_paths=["./plugins"])
registry.register_plugin("my_plugin", MyPlugin, version="1.0.0")

plugin = registry.load_plugin("my_plugin", api_key="xxx")
result = plugin.execute("sample data")

for info in registry.list_plugins():
    print(f"{info['name']}: {info['version']}")
```

---

## MethodRegistry

Register custom orchestration methods for extensibility.

```python
from semantica.core import method_registry

def fast_kb_builder(sources, **kwargs):
    # custom logic — skip embeddings for speed
    ...

method_registry.register("knowledge_base", "fast", fast_kb_builder)

from semantica.core.methods import build_knowledge_base
result = build_knowledge_base(sources=["doc.pdf"], method="fast")
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Pipeline" icon="arrows-turn-to-dots" href="pipeline">
    Pipeline execution and orchestration.
  </Card>
  <Card title="Utils" icon="wrench" href="utils">
    Shared utilities used by Core internally.
  </Card>
  <Card title="Getting Started" icon="play" href="../getting-started">
    Learn the basics before using Core.
  </Card>
  <Card title="LLMs" icon="microchip" href="llms">
    Configure LLM providers via ConfigManager.
  </Card>
</CardGroup>
