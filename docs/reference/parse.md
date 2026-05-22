---
title: "Parse Module"
description: "Document parsing and text extraction — DocumentParser for standard formats and DoclingParser for complex layouts."
icon: "file-lines"
---

> Universal data parser supporting documents, web content, structured data, emails, code, and media.

---

## DocumentParser

Standard parser for clean, machine-readable documents.

```python
from semantica.parse import DocumentParser

parser = DocumentParser()
parsed = parser.parse("data/report.pdf")

print(parsed.text)       # full clean text
print(parsed.metadata)   # title, author, date, page_count, etc.
print(parsed.sections)   # document structure
```

Supported formats: PDF, DOCX, HTML, TXT, JSON, CSV, PPTX, XLSX.

---

## DoclingParser

Advanced parser for complex layouts using the Docling backend.

```bash
pip install "semantica[docling]"
```

```python
from semantica.parse import DoclingParser

parser = DoclingParser(
    extract_tables=True,        # structured table extraction
    extract_images=True,        # image OCR
    output_format="markdown",   # "markdown" | "html" | "json"
)

parsed = parser.parse("data/annual_report.pdf")

print(parsed.text)     # full clean text
print(parsed.tables)   # structured table data
print(parsed.sections) # document structure
```

Use DoclingParser for: multi-column PDFs, tables with merged cells, PPTX slides, XLSX spreadsheets, images with OCR, and scanned documents.

---

## OCR Support

```python
parser = DoclingParser(
    ocr=True,
    ocr_language=["en"],
    extract_tables=True,
)

parsed = parser.parse("data/scanned_contract.pdf")
```

---

## Parsed Document Object

```python
@dataclass
class ParsedDocument:
    text: str
    sections: List[Section]
    tables: List[TableData]
    metadata: DocumentMetadata
    source_id: str

@dataclass
class DocumentMetadata:
    title: Optional[str]
    author: Optional[str]
    created_date: Optional[datetime]
    page_count: int
    language: Optional[str]
    has_tables: bool
    has_images: bool
    word_count: int
    format: str   # "pdf" | "docx" | "pptx" | ...
```

---

## Integration with FileIngestor

```python
from semantica.ingest import FileIngestor
from semantica.parse import DoclingParser

ingestor = FileIngestor()
parser = DoclingParser(extract_tables=True)

sources = ingestor.ingest("data/reports/")
for source in sources:
    parsed = parser.parse(source)
```

<Note>
  Docling is an optional dependency. If `docling` is not installed, `DoclingParser` raises an `ImportError` with installation instructions. Standard `DocumentParser` is used as the fallback.
</Note>

---

## See Also

<CardGroup cols={2}>
  <Card title="Ingest" icon="database" href="ingest">
    Load files before parsing.
  </Card>
  <Card title="Split" icon="scissors" href="split">
    Chunk parsed text for embedding.
  </Card>
  <Card title="Docling Integration" icon="file-pdf" href="../integrations/docling">
    Full Docling integration guide.
  </Card>
  <Card title="Semantic Extract" icon="magnifying-glass" href="semantic_extract">
    Extract entities from parsed text.
  </Card>
</CardGroup>
