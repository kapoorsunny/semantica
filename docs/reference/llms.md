---
title: "LLMs Module"
description: "Unified interface for Groq, OpenAI, LiteLLM (Anthropic, Gemini, Ollama, DeepSeek, Azure, Bedrock, 100+ models), and HuggingFace."
icon: "microchip"
---

`semantica.llms` provides a single consistent API across every major LLM provider. Every provider is a drop-in replacement for the `llm_provider=` parameter in extractors, reasoning engines, and agents.

## Exported Classes

```python
from semantica.llms import Groq, OpenAI, LiteLLM, HuggingFaceLLM
```

| Class | Provider | API Key Required |
| ----- | -------- | ---------------- |
| `Groq` | Groq Cloud | `GROQ_API_KEY` |
| `OpenAI` | OpenAI / any OpenAI-compatible gateway | `OPENAI_API_KEY` |
| `LiteLLM` | 100+ providers via LiteLLM routing | Depends on model |
| `HuggingFaceLLM` | Local HuggingFace Transformers | None (local) |

<Tip>
  **Anthropic, Gemini, Ollama, DeepSeek, Azure, Bedrock, Cohere, and 90+ others** are all available via `LiteLLM` using their model-string prefix. See the [LiteLLM section](#litellm-100-providers) below.
</Tip>

## What You Get

- **Unified `LLMProvider` interface** — swap providers with a one-line change, no application code changes
- **`LiteLLM`** — single class for 100+ providers using model-string routing
- **Local models** — `HuggingFaceLLM` runs fully on-premise, no API key
- **Streaming** — token-by-token output for low-latency UX
- **Custom gateways** — point `OpenAI` at any OpenAI-compatible endpoint via `base_url`

## Choosing a Provider

Use this decision matrix to select the right LLM provider for your use case:

| Priority | Recommended Provider | Model | Why |
|----------|---------------------|-------|-----|
| **Getting Started** | Groq | `llama-3.1-8b-instant` | Free tier, fast inference, no complex setup |
| **Production Quality** | OpenAI | `gpt-3.5-turbo` | Reliable, battle-tested, extensive documentation |
| **Cost Optimization** | LiteLLM + DeepSeek | `deepseek/deepseek-chat` | Lowest cost per token for high-volume workloads |
| **Privacy/On-Premise** | Ollama (via LiteLLM) | `ollama/llama3.2:3b` | Fully local, no data leaves your infrastructure |
| **Advanced Reasoning** | Anthropic Claude (via LiteLLM) | `anthropic/claude-sonnet-4-20250514` | Highest quality for complex analysis |

### Quick Start Recommendation

For new users, start with Groq:

```python
from semantica.llms import Groq
import os

# Fastest path to working extraction
llm = Groq(
    model="llama-3.1-8b-instant",  # Default model
    api_key=os.getenv("GROQ_API_KEY")
)
```

Get your free API key at [console.groq.com](https://console.groq.com).

## API Key Setup

### Environment Variables (Recommended)

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export GROQ_API_KEY="your_groq_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here" 
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Reload your shell
source ~/.bashrc
```

### Configuration File Method

```yaml
# config.yaml
llm_provider:
  name: groq
  model: llama-3.1-8b-instant
  temperature: 0.0
# Set GROQ_API_KEY environment variable and pass to constructor
```

### Programmatic Setup

```python
import os
from semantica.llms import Groq, LiteLLM

# Method 1: Direct API key
llm = Groq(api_key="your-api-key-here", model="llama-3.1-8b-instant")

# Method 2: Environment variable (preferred)
llm = Groq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant")

# Method 3: Multiple providers via LiteLLM
providers = {
    "fast": LiteLLM(model="groq/llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY")),
    "smart": LiteLLM(model="anthropic/claude-sonnet-4-20250514", api_key=os.getenv("ANTHROPIC_API_KEY"))
}
```

### Security Best Practices

<Warning>
Never commit API keys to version control. Use environment variables or secure secret management.
</Warning>

```python
# ❌ Bad - API key in code
llm = Groq(api_key="gsk_abc123...", model="llama-3.1-8b-instant")

# ✅ Good - Environment variable
llm = Groq(api_key=os.getenv("GROQ_API_KEY"), model="llama-3.1-8b-instant")
```

## Providers

<CodeGroup>

```python Groq
import os
from semantica.llms import Groq

llm = Groq(
    model="llama-3.1-8b-instant",   # default
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=64000,
    temperature=0.0,
)
# Best for: high-throughput extraction, fast inference at low cost
```

```python OpenAI
import os
from semantica.llms import OpenAI

llm = OpenAI(
    model="gpt-3.5-turbo",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.0,
)
# Best for: general purpose, function calling, JSON mode
```

```python LiteLLM (100+ providers)
import os
from semantica.llms import LiteLLM

# pip install "semantica[llm-litellm]"

# Anthropic Claude
llm = LiteLLM(model="anthropic/claude-opus-4-5",         api_key=os.getenv("ANTHROPIC_API_KEY"))

# Google Gemini
llm = LiteLLM(model="gemini/gemini-1.5-pro",             api_key=os.getenv("GOOGLE_API_KEY"))

# Ollama (local — no API key)
llm = LiteLLM(model="ollama/llama3.2:3b",                api_base="http://localhost:11434")

# DeepSeek
llm = LiteLLM(model="deepseek/deepseek-chat",            api_key=os.getenv("DEEPSEEK_API_KEY"))

# Azure OpenAI
llm = LiteLLM(model="azure/gpt-4o",                      api_key=os.getenv("AZURE_API_KEY"))

# AWS Bedrock
llm = LiteLLM(model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0")

# Novita AI
llm = LiteLLM(model="novita/deepseek/deepseek-v3.2",     api_key=os.getenv("NOVITA_API_KEY"))
```

```python HuggingFaceLLM (Local)
from semantica.llms import HuggingFaceLLM

llm = HuggingFaceLLM(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    device="cuda",           # "cpu" | "cuda" | "mps"
    max_new_tokens=512,
    temperature=0.1,
)
# Bring your own model — full local control, no API key
```

</CodeGroup>

## LiteLLM — 100+ Providers

`LiteLLM` is the recommended way to access any provider not directly exported by `semantica.llms`. Use the `provider/model` string format:

```python
import os
from semantica.llms import LiteLLM

# Pattern: LiteLLM(model="<provider>/<model-name>")
providers = {
    "Anthropic":  LiteLLM(model="anthropic/claude-opus-4-5",       api_key=os.getenv("ANTHROPIC_API_KEY")),
    "Gemini":     LiteLLM(model="gemini/gemini-1.5-pro",            api_key=os.getenv("GOOGLE_API_KEY")),
    "Ollama":     LiteLLM(model="ollama/llama3.2:3b",               api_base="http://localhost:11434"),
    "DeepSeek":   LiteLLM(model="deepseek/deepseek-chat",           api_key=os.getenv("DEEPSEEK_API_KEY")),
    "Azure":      LiteLLM(model="azure/gpt-4o",                     api_key=os.getenv("AZURE_API_KEY")),
    "Bedrock":    LiteLLM(model="bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0"),
    "Cohere":     LiteLLM(model="cohere/command-r-plus",            api_key=os.getenv("COHERE_API_KEY")),
    "Novita AI":  LiteLLM(model="novita/deepseek/deepseek-v3.2",    api_key=os.getenv("NOVITA_API_KEY")),
}

# Every LiteLLM instance implements the same .generate() interface
response = providers["Anthropic"].generate("Explain GraphRAG in one paragraph.")
```

<Note>
  The full list of supported LiteLLM model strings is at [docs.litellm.ai/docs/providers](https://docs.litellm.ai/docs/providers). Use the `provider/model` format shown above.
</Note>

## Custom / Enterprise Gateways

Any OpenAI-compatible endpoint — internal routing layers, Qwen proxies, or private LLaMA deployments:

```python
import os
from semantica.llms import OpenAI

llm = OpenAI(
    model="qwen2.5-72b",
    api_key=os.getenv("GATEWAY_API_KEY"),
    base_url="https://my-internal-gateway.company.com/v1",
)
```

<Note>
  `base_url` is validated at construction time. Non-HTTP(S) schemes raise `ValueError` to prevent SSRF attacks (fixed in v0.5.0).
</Note>

## Using in Extractors

All extractors accept any provider as `llm_provider=`:

```python
import os
from semantica.semantic_extract import NERExtractor, RelationExtractor, TripletExtractor
from semantica.llms import Groq

llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))

ner  = NERExtractor(method="llm",      llm_provider=llm, max_retries=3)
rel  = RelationExtractor(method="llm", llm_provider=llm)
trip = TripletExtractor(method="llm",  llm_provider=llm)
```

## Provider Comparison

| Provider | Import | Speed | Cost | Local | Context | Best For |
| -------- | ------ | ----- | ---- | ----- | ------- | -------- |
| Groq | `Groq` | Very fast | Low | No | 128k | High-throughput extraction |
| OpenAI | `OpenAI` | Fast | Medium | No | 128k | General purpose, function calling |
| Anthropic | `LiteLLM(model="anthropic/...")` | Fast | Medium | No | 200k | Complex reasoning, safety |
| Gemini | `LiteLLM(model="gemini/...")` | Fast | Low | No | 1M | Long context, multimodal |
| Ollama | `LiteLLM(model="ollama/...")` | Medium | Free | Yes | Varies | Privacy, air-gapped |
| DeepSeek | `LiteLLM(model="deepseek/...")` | Fast | Very low | No | 64k | Coding, analysis |
| Azure OpenAI | `LiteLLM(model="azure/...")` | Fast | Medium | No | 128k | Enterprise, compliance |
| AWS Bedrock | `LiteLLM(model="bedrock/...")` | Fast | Varies | No | Varies | AWS-native workloads |
| HuggingFace | `HuggingFaceLLM` | Slow | Free | Yes | Varies | Custom models, BYOM |

<Tip>
  For production extraction pipelines, Groq delivers the best throughput-to-cost ratio. For complex multi-hop reasoning, Claude Opus or GPT-4o provide the highest accuracy.
</Tip>

## Performance and Reliability Tips

### Extraction with Retries

```python
import os
from semantica.semantic_extract import NERExtractor
from semantica.llms import Groq

llm = Groq(model="llama-3.1-8b-instant", api_key=os.getenv("GROQ_API_KEY"))
ner = NERExtractor(method="llm", llm_provider=llm, max_retries=3)

# Process multiple texts with automatic retries
texts = ["Document 1 text...", "Document 2 text...", "Document 3 text..."]
all_entities = []

for text in texts:
    entities = ner.extract(text)
    all_entities.extend(entities)
    
# Rate limiting handled automatically by provider
```

### Model Selection by Use Case

| Use Case | Recommended Provider/Model | Reasoning |
|----------|---------------------------|-----------|
| **Entity Extraction** | `Groq("llama-3.1-8b-instant")` | Fast, good accuracy for structured tasks |
| **Relation Extraction** | `OpenAI("gpt-3.5-turbo")` | Better at complex relationship reasoning |
| **Complex Analysis** | `LiteLLM("anthropic/claude-sonnet-4-20250514")` | Highest reasoning capability |
| **High Volume/Cost** | `LiteLLM("deepseek/deepseek-chat")` | Lowest cost per token |

### Error Handling

```python
import os
from semantica.llms import Groq
from semantica.semantic_extract import NERExtractor

llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

# Automatic retries for rate limits and transient errors
extractor = NERExtractor(
    method="llm", 
    llm_provider=llm,
    max_retries=3      # Retry failed requests automatically
)
```

<CardGroup cols={2}>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Use LLMs for NER and relation extraction.
  </Card>
  <Card title="Agno Integration" icon="robot" href="../integrations/agno">
    LLM providers in Agno multi-agent teams.
  </Card>
  <Card title="Reasoning" icon="brain" href="reasoning">
    LLM-backed deductive and abductive reasoning.
  </Card>
  <Card title="Context" icon="diagram-project" href="context">
    GraphRAG uses LLMs for reasoning over knowledge graphs.
  </Card>
</CardGroup>
