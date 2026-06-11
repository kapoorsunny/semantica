---
title: "Split Module"
description: "15+ text chunking methods including recursive, semantic, entity-aware, relation-aware, code, and structural splitting."
icon: "scissors"
---

`semantica.split` breaks documents into chunks that preserve semantic context. Chunking quality directly determines downstream accuracy — a poorly chunked document produces bad embeddings, missed entities, and broken relation triplets. Use the right strategy for your content type and pipeline goal.

## Why Chunking Matters

Most LLMs and embedding models have fixed context windows. Documents larger than that window must be split. But naive splitting (every 500 characters, regardless of structure) destroys semantic context:

- An entity mention like "Apple Inc." split across two chunks loses its context in both
- A relation triplet like "Steve Jobs founded Apple" split at "Steve Jobs" leaves a dangling subject
- Embedding a chunk that mixes two unrelated topics produces a centroid vector that matches neither

Semantica's chunking methods are designed to avoid these failure modes.

## Exported Classes

| Class | Role |
| --- | --- |
| `TextSplitter` | Unified entry point — swap `method=` without changing downstream code |
| `Chunk` | `{text, start_index, end_index, metadata, id}` |
| `SemanticChunker` | Embedding-based topic-shift detection — splits only when content actually changes |
| `StructuralChunker` | Heading/section-based splits using structural text analysis |
| `EntityAwareChunker` | Prevents named entity mentions from being split across chunk boundaries |
| `RelationAwareChunker` | Keeps subject-predicate-object triplets intact within a single chunk |
| `HierarchicalChunker` | Multi-level chunking producing parent/child chunk relationships |

**Available `method=` values for `TextSplitter`:**

| Method | Best for |
| --- | --- |
| `recursive` | General text — splits on paragraphs, sentences, words in order |
| `sentence` | Conversational text, QA |
| `token` | LLM context window enforcement |
| `semantic_transformer` | Long documents with topic shifts |
| `entity_aware` | KG extraction pipelines |
| `code` | Source code files |
| `structural` | PDFs and DOCX with heading hierarchy |

## What You Get

<CardGroup cols={2}>
  <Card title="TextSplitter" icon="scissors">
    Unified interface for 11 chunking strategies — swap methods without changing downstream code.
  </Card>
  <Card title="Semantic Chunking" icon="brain">
    Embedding-based topic shift detection — splits only when the topic actually changes.
  </Card>
  <Card title="Entity-Aware Chunking" icon="user">
    Entity spans never cross chunk boundaries — guaranteed by boundary adjustment.
  </Card>
  <Card title="Relation-Aware Chunking" icon="arrows-left-right">
    Subject–predicate–object triplets kept within a single chunk for KG pipelines.
  </Card>
  <Card title="Code Splitting" icon="code">
    AST-level boundaries (function, class, method) for source code search and analysis.
  </Card>
  <Card title="Chunk Object" icon="box">
    Output dataclass with text, character offsets, optional id, and full metadata.
  </Card>
</CardGroup>

## Quick Start

<Steps>
  <Step title="Choose a splitting method">
    ```python
    from semantica.split import TextSplitter

    splitter = TextSplitter(
        method="recursive",   # see Splitting Methods table
        chunk_size=1000,
        chunk_overlap=200,
    )
    ```
  </Step>
  <Step title="Split raw text">
    ```python
    chunks = splitter.split(text)

    for chunk in chunks:
        print(f"  Start: {chunk.start_index}, End: {chunk.end_index}")
        print(f"  Method: {chunk.metadata.get('method')}")
        print(f"  Preview: {chunk.text[:80]}...")
    ```
  </Step>
  <Step title="Or split a document object">
    ```python
    # split_documents() accepts any object with a .text attribute,
    # or a plain string — no specific document class required.
    class Doc:
        def __init__(self, text, metadata=None):
            self.text = text
            self.metadata = metadata or {}

    doc = Doc(text="Annual report content...", metadata={"source": "annual_report.pdf"})

    splitter = TextSplitter(method="structural")
    chunks   = splitter.split_documents([doc])

    for chunk in chunks:
        print(f"  {chunk.text[:80]}...")
    ```
  </Step>
  <Step title="Batch-split a list of documents">
    ```python
    # split_documents() returns a flat List[Chunk] across all inputs
    all_chunks = splitter.split_documents(docs)

    for chunk in all_chunks:
        print(chunk.text[:80])
    ```
  </Step>
</Steps>

## Splitting Methods

| Method | How It Splits | Best For |
| ------ | ------------- | -------- |
| `recursive` | Paragraph → sentence → word (cascading fallback) | General-purpose default |
| `semantic_transformer` | Embeds sentences, splits at cosine similarity drops | RAG — topic coherence matters |
| `entity_aware` | Adjusts boundaries so entity spans are never cut | NER pipelines |
| `relation_aware` | Keeps subject–predicate–object triplets within one chunk | KG construction |
| `sentence` | Language-aware sentence boundary detection (NLTK/spaCy) | Short documents, Q&A |
| `token` | Exact token count via tiktoken; hard cutoff | LLM context window prep |
| `fixed` | Fixed character count with overlap; fastest, no NLP | Simple batch jobs — use `character` method |
| `sliding_window` | Fixed-step window — heavy overlap for dense retrieval | Bi-encoder retrieval (ColBERT, DPR) |
| `markdown` | Splits at Markdown heading levels (configurable) | Documentation, wikis, MDX |
| `structural` | Structure-aware splits using heading/paragraph detection | Text with heading hierarchy |
| `code` | AST-level splits at function / class / method boundaries | Source code search and analysis |

## Choosing a Strategy

Use this decision tree before picking a method:

- **Source code?** → `code`
- **Markdown or structured doc with headings?** → `markdown` or `structural`
- **Building a KG?** → `relation_aware` (keeps triplets intact), then `entity_aware` for pure NER
- **RAG system where retrieval quality matters most?** → `semantic_transformer`
- **Dense overlap for bi-encoder retrieval (ColBERT, DPR)?** → `sliding_window`
- **Preparing prompts for a fixed-window LLM?** → `token`
- **Fast splitting with no NLP overhead?** → `recursive` or `character`

## TextSplitter Constructor

```python
from semantica.split import TextSplitter

splitter = TextSplitter(
    method="semantic_transformer",   # chunking strategy
    chunk_size=1000,                 # target size in tokens
    chunk_overlap=200,               # token overlap between adjacent chunks
    tokenizer="cl100k_base",         # tiktoken encoding (GPT-4 default)
    min_chunk_size=50,               # discard very short trailing chunks
    include_metadata=True,           # attach source_id, page_number, section_title
    language="en",                   # ISO 639-1 — used by sentence boundary detector
)
```

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `method` | `str` | `"recursive"` | Chunking strategy — see table above |
| `chunk_size` | `int` | `1000` | Target size in tokens (characters for `fixed`) |
| `chunk_overlap` | `int` | `200` | Token overlap between adjacent chunks |
| `tokenizer` | `str` | `"cl100k_base"` | tiktoken encoding: `"cl100k_base"` (GPT-4), `"p50k_base"` (GPT-3), `"r50k_base"` (Codex) |
| `min_chunk_size` | `int` | `0` | Discard chunks shorter than this many tokens |
| `similarity_threshold` | `float` | `0.7` | Cosine similarity cutoff for `semantic_transformer` |
| `embedder` | `EmbeddingGenerator` | `None` | Custom embedder for `semantic_transformer` |
| `include_metadata` | `bool` | `True` | Attach `source_id`, `page_number`, `section_title` to each chunk |
| `language` | `str` | `"en"` | ISO 639-1 language code for sentence boundary detection |
| `heading_levels` | `list[int]` | `[1, 2, 3]` | Heading levels to split on for `markdown` method |
| `code_units` | `list[str]` | `["function", "class"]` | AST node types to split on for `code` method |

## Splitting Method Details

<Tabs>
  <Tab title="Recursive (default)">
    Tries paragraph breaks first, then sentence boundaries, then word boundaries — falling back only when the chunk exceeds `chunk_size`:

    ```python
    splitter = TextSplitter(method="recursive", chunk_size=1000, chunk_overlap=200)
    chunks   = splitter.split(text)
    ```

    **Key behaviours:**
    - Preserves paragraph and sentence structure wherever possible
    - Falls back gracefully — never produces chunks larger than `chunk_size`
    - Overlap ensures context continuity across chunk boundaries
    - Good starting point when you're unsure which method to use
  </Tab>
  <Tab title="Semantic">
    Embeds each sentence, then splits whenever cosine similarity between consecutive sentences drops below `similarity_threshold`. Each chunk talks about one topic:

    ```python
    from semantica.split import TextSplitter
    from semantica.embeddings import EmbeddingGenerator

    embedder = EmbeddingGenerator(model="sentence-transformers")
    splitter = TextSplitter(
        method="semantic_transformer",
        embedder=embedder,
        similarity_threshold=0.7,   # 0.6 = more splits, 0.8 = fewer splits
        chunk_size=800,
        chunk_overlap=0,            # not needed — chunks are already coherent
    )
    chunks = splitter.split(text)
    ```

    **Key behaviours:**
    - Produces variable-length chunks — some topics are short, others long
    - Requires an embedder — defaults to `sentence-transformers/all-MiniLM-L6-v2` if not set
    - Slower than `recursive` due to embedding computation; cache embeddings for repeated splits
    - Best retrieval quality for semantic search — chunks map to single coherent topics
  </Tab>
  <Tab title="Entity-Aware">
    Runs NER internally, then adjusts chunk boundaries so no entity mention is split across two chunks:

    ```python
    from semantica.split import TextSplitter
    import os

    # ner_method is passed through to the internal NERExtractor.
    # Use "llm" for highest accuracy, "ml" (default) for speed.
    splitter = TextSplitter(
        method="entity_aware",
        chunk_size=512,
        chunk_overlap=50,
        ner_method="ml",   # "pattern" | "regex" | "ml" | "huggingface" | "llm"
    )
    chunks = splitter.split(text)

    for chunk in chunks:
        print(f"  entities in chunk: {chunk.metadata.get('entity_count', 0)}")
        print(f"  preview: {chunk.text[:80]}...")
    ```

    **Key behaviours:**
    - NER is run internally — entity extraction happens automatically inside the splitter
    - Entity objects are available in `chunk.metadata["entities"]` for each chunk
    - Chunk sizes vary slightly from `chunk_size` — boundary adjustments are ≤ one sentence
    - Works with all entity types: PERSON, ORGANIZATION, LOCATION, DATE, custom types
  </Tab>
  <Tab title="Relation-Aware">
    Keeps subject–predicate–object triplets within the same chunk — critical for KG pipelines:

    ```python
    from semantica.split import TextSplitter

    # relation_method is passed through to the internal RelationExtractor.
    # Use "llm" for highest accuracy, "ml" (default) for speed.
    splitter = TextSplitter(
        method="relation_aware",
        chunk_size=512,
        relation_method="ml",   # "ml" | "llm" | "huggingface"
    )
    chunks = splitter.split(text)

    for chunk in chunks:
        print(f"  relations in chunk: {chunk.metadata.get('relation_count', 0)}")
        for rel in chunk.metadata.get("relationships", []):
            print(f"  {rel}")
    ```

    **Key behaviours:**
    - Relation extraction is run internally — no pre-computed entities or triplets needed
    - Relation objects are available in `chunk.metadata["relationships"]` for each chunk
    - Implies entity-aware behaviour — both entities in a triplet are kept whole too
    - Best used as the split step in a `Parse → Split → Extract → Build KG` pipeline
  </Tab>
  <Tab title="Code">
    Parses source files with `CodeParser` and splits at AST-level boundaries:

    ```python
    from semantica.parse import CodeParser
    from semantica.split import TextSplitter

    parser = CodeParser(extract_comments=True, extract_dependencies=True)
    parsed = parser.parse("src/pipeline.py")

    splitter = TextSplitter(
        method="code",
        chunk_overlap=0,   # code units are self-contained
    )
    chunks = splitter.split_documents([parsed])

    for chunk in chunks:
        print(f"  start: {chunk.start_index}, end: {chunk.end_index}")
        print(f"  preview: {chunk.text[:80]}...")
    ```

    **Key behaviours:**
    - Use `split_documents([parsed])` to pass an object with a `.text` attribute
    - `chunk_overlap=0` recommended — functions and classes are logically self-contained
    - Supported languages: Python, JavaScript, TypeScript, Java, Go, Rust, C, C++, C#, Ruby, PHP, Swift
  </Tab>
  <Tab title="Structural & Markdown">
    ### Structural

    Splits text based on document structure — detected headings and paragraph breaks become natural chunk boundaries:

    ```python
    from semantica.split import TextSplitter

    splitter = TextSplitter(method="structural")
    chunks   = splitter.split(text)

    for chunk in chunks:
        print(f"  {chunk.text[:80]}...")
        print(f"  start: {chunk.start_index}, end: {chunk.end_index}")
    ```

    ### Markdown

    Splits at Markdown heading boundaries, configurable to specific heading levels:

    ```python
    splitter = TextSplitter(
        method="markdown",
        chunk_size=800,
    )
    chunks = splitter.split(markdown_text)
    ```

  </Tab>
</Tabs>

## Chunk Schema

<AccordionGroup>
  <Accordion title="Chunk dataclass">

```python
@dataclass
class Chunk:
    text:        str                    # the chunk's text content
    start_index: int                    # character offset of start in source text
    end_index:   int                    # character offset of end in source text
    metadata:    Dict[str, Any]         # method-specific fields — see table below
    id:          Optional[str] = None   # optional chunk identifier
```

  </Accordion>
  <Accordion title="Chunk metadata fields">

Metadata keys vary by method. Only keys that are actually set by the implementation are listed.

| Field | Type | Set by | Description |
| ----- | ---- | ------ | ----------- |
| `method` | `str` | all methods | Splitting method that produced this chunk |
| `chunk_size` | `int` | most methods | Character length of this chunk |
| `sentence_count` | `int` | `sentence`, `semantic_transformer`, spaCy path | Number of sentences in this chunk |
| `paragraph_count` | `int` | `paragraph` | Number of paragraphs in this chunk |
| `word_count` | `int` | `word` | Number of words in this chunk |
| `token_count` | `int` | `token`; `sentence`/`semantic_transformer` when spaCy is available | Token count — not always present |
| `entity_count` | `int` | `entity_aware` | Number of entities whose boundaries fall in this chunk |
| `entities` | `list` | `entity_aware` | Entity objects whose boundaries fall in this chunk |
| `relation_count` | `int` | `relation_aware` | Number of relation triplets in this chunk |
| `relationships` | `list` | `relation_aware` | Relation objects in this chunk |
| `element_count` | `int` | `structural` | Number of structural elements grouped into this chunk |
| `element_types` | `list[str]` | `structural` | Types of elements: `"heading"`, `"paragraph"`, `"list"`, etc. |

  </Accordion>
</AccordionGroup>

## Tokenizer Options

| Tokenizer | Models |
| --------- | ------ |
| `cl100k_base` | GPT-4, GPT-3.5-turbo, text-embedding-ada-002 |
| `p50k_base` | GPT-3 (`text-davinci-003`), Codex |
| `r50k_base` | GPT-3 (`davinci`) |

## Pipeline Integration

```python
from semantica.pipeline import Pipeline
from semantica.ingest import FileIngestor
from semantica.parse import DocumentParser
from semantica.split import TextSplitter
from semantica.semantic_extract import NERExtractor
from semantica.llms import Groq
import os

llm = Groq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

pipeline = Pipeline()
pipeline.add_step("ingest",   FileIngestor())
pipeline.add_step("parse",    DocumentParser())
pipeline.add_step("split",    TextSplitter(method="semantic_transformer", chunk_size=512))
pipeline.add_step("extract",  NERExtractor(method="llm", llm_provider=llm))

result = pipeline.run("data/reports/")
```

## Tips and Common Pitfalls

<Warning>
  **`chunk_overlap` too small.** Without overlap, a fact that spans a chunk boundary is invisible in both chunks. A 10–20% overlap relative to `chunk_size` is a safe minimum — for `chunk_size=1000`, set `chunk_overlap=100` to `200`.
</Warning>

<Warning>
  **Wrong tokenizer.** If you use `cl100k_base` (GPT-4) but send chunks to a model with a different vocabulary, your token counts will be wrong. Match the tokenizer to your target model.
</Warning>

<Tip>
  **Semantic splitting needs enough sentences.** `semantic_transformer` needs several sentences to detect topic shifts. On documents shorter than ~300 words it behaves like `sentence` splitting — use `recursive` instead.
</Tip>

<Tip>
  **Code units too coarse.** `code_units=["class"]` on a large codebase produces chunks too big to embed well. Use `["function", "method"]` for more granular, independently useful units.
</Tip>

<Tip>
  **Set `min_chunk_size` to avoid fragment chunks.** `min_chunk_size=0` (default) can produce many tiny trailing chunks. Set to ~30–50 tokens to discard fragments that carry no retrieval value.
</Tip>

<CardGroup cols={2}>
  <Card title="Parse" icon="file-lines" href="parse">
    Parse documents before chunking — produces sections and metadata.
  </Card>
  <Card title="Embeddings" icon="vector-square" href="embeddings">
    Embed chunks for vector search and semantic chunking.
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Extract entities and relations from individual chunks.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Integrate splitting as a named pipeline step.
  </Card>
</CardGroup>
