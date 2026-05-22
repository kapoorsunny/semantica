---
title: "Ingest Module"
description: "Universal data ingestion from files, Parquet, XML, web, feeds, streams, repositories, email, and databases."
icon: "database"
---

> Universal data ingestion — the entry point for loading data into Semantica.

---

## Overview

The **Ingest Module** handles loading data from every common source into Semantica. All ingestors return a list of `DataSource` objects with content and metadata.

---

## FileIngestor

```python
from semantica.ingest import FileIngestor

ingestor = FileIngestor()

# Single file
sources = ingestor.ingest("data/report.pdf")

# Directory (recursive)
sources = ingestor.ingest_directory("data/", recursive=True)

# Glob pattern
sources = ingestor.ingest("data/**/*.docx")
```

Supported formats: PDF, DOCX, TXT, HTML, JSON, CSV, Excel (XLSX/XLS), PPTX, ZIP/TAR archives. File type is auto-detected.

---

## ParquetIngestor (v0.5.0)

PyArrow-based ingestion for Apache Parquet files.

```python
from semantica.ingest import ParquetIngestor

ingestor = ParquetIngestor()

# Single file
sources = ingestor.ingest("data/events.parquet")

# Partitioned directory (Hive-style: year=2024/month=01/...)
sources = ingestor.ingest("data/partitioned/")

# Selective columns
sources = ingestor.ingest("data/events.parquet", columns=["id", "text", "timestamp"])
```

---

## XMLIngestor (v0.5.0)

XXE-safe lxml-based ingestion with optional XSD/DTD validation.

```python
from semantica.ingest import XMLIngestor

# Basic ingestion
ingestor = XMLIngestor()
sources = ingestor.ingest("data/records.xml")

# With XSD validation
ingestor = XMLIngestor(validate_xsd="schema.xsd")
sources = ingestor.ingest("data/records/")

# With DTD validation
ingestor = XMLIngestor(validate_dtd=True)
sources = ingestor.ingest("data/feed.xml")
```

<Note>
  The `XMLIngestor` uses lxml with XXE disabled (`resolve_entities=False`) to prevent XML External Entity injection attacks.
</Note>

---

## WebIngestor

```python
from semantica.ingest import WebIngestor

ingestor = WebIngestor(
    rate_limit=1.0,        # seconds between requests
    respect_robots=True,   # honor robots.txt
    max_depth=2            # crawl depth
)

# Single URL
sources = ingestor.ingest("https://example.com/about")

# Multiple URLs
sources = ingestor.ingest_urls([
    "https://example.com/page1",
    "https://example.com/page2",
])
```

---

## FeedIngestor (RSS/Atom)

```python
from semantica.ingest import FeedIngestor

ingestor = FeedIngestor()
sources = ingestor.ingest("https://feeds.example.com/rss")

# Monitor for updates
ingestor.monitor("https://feeds.example.com/rss", interval=300, callback=process_new_items)
```

---

## DBIngestor (SQL / NoSQL)

```python
from semantica.ingest import DBIngestor

# PostgreSQL
ingestor = DBIngestor(
    connection_string="postgresql://user:pass@localhost/db",
    query="SELECT id, content, created_at FROM documents WHERE status='active'"
)
sources = ingestor.ingest()
```

---

## SnowflakeIngestor

```python
from semantica.ingest import SnowflakeIngestor

ingestor = SnowflakeIngestor(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse="COMPUTE_WH",
    database="ANALYTICS",
    schema="PUBLIC"
)
sources = ingestor.ingest(query="SELECT * FROM documents")
```

---

## Other Ingestors

| Class | Source |
|-------|--------|
| `StreamIngestor` | Kafka, RabbitMQ, Kinesis, Pulsar |
| `RepoIngestor` | Git repositories (GitHub, GitLab) |
| `EmailIngestor` | IMAP/POP3 servers |
| `MCPIngestor` | Model Context Protocol servers |
| `S3Ingestor` | AWS S3 buckets |
| `GCSIngestor` | Google Cloud Storage |

---

## DataSource Object

All ingestors return a list of `DataSource` objects:

```python
@dataclass
class DataSource:
    content: str            # raw text content
    source_id: str          # unique identifier
    source_type: str        # "file", "web", "database", etc.
    metadata: Dict          # title, author, url, date, etc.
    raw_bytes: Optional[bytes]
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Parse" icon="file-lines" href="parse">
    Parse raw sources into structured text.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Orchestrate ingest as part of a pipeline.
  </Card>
  <Card title="Snowflake Integration" icon="snowflake" href="../integrations/snowflake">
    Snowflake-specific setup guide.
  </Card>
  <Card title="Provenance" icon="link" href="provenance">
    Track lineage from ingest to inference.
  </Card>
</CardGroup>
