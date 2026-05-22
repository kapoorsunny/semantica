---
title: "Normalize Module"
description: "Text cleaning, entity standardization, date normalization, and encoding repair."
icon: "broom"
---

> Clean, standardize, and prepare text and data for semantic processing.

---

## DataNormalizer

```python
from semantica.normalize import DataNormalizer

normalizer = DataNormalizer()

# Text cleaning
clean = normalizer.normalize_text("  Hello,   World!!  \n\n")
# → "Hello, World!!"

# Date standardization
date = normalizer.normalize_date("Jan 1st, 2020")
# → "2020-01-01"

# Entity normalization
entity = normalizer.normalize_entity("Apple Computer Inc.")
# → "Apple Inc."

# Number normalization
num = normalizer.normalize_number("$1,234.56")
# → 1234.56
```

---

## Text Normalization

```python
text = normalizer.normalize_text(
    raw_text,
    lowercase=False,           # convert to lowercase
    remove_punctuation=False,  # strip punctuation
    remove_extra_whitespace=True,
    fix_encoding=True,         # repair cp1252/latin-1 mojibake
    strip_html=True,           # remove HTML tags
    normalize_unicode=True     # NFC normalization
)
```

<Note>
  **v0.5.0 fix:** The encoding repair now handles cp1252/latin-1 characters that previously caused crashes on Windows when processing documents with non-ASCII content.
</Note>

---

## Entity Normalization

```python
# Company name normalization
companies = [
    "Apple Computer, Inc.",
    "Apple Inc",
    "APPLE INC.",
]
normalized = [normalizer.normalize_entity(c) for c in companies]
# All → "Apple Inc."

# Person name normalization
name = normalizer.normalize_person_name("JOBS, STEVE")
# → "Steve Jobs"
```

---

## Date & Time Normalization

```python
dates = [
    "January 1st, 2020",
    "01/01/2020",
    "2020-01-01T00:00:00Z",
    "yesterday",   # relative dates supported
]
normalized = [normalizer.normalize_date(d) for d in dates]
# All → "2020-01-01" (ISO 8601)
```

---

## Quantity Normalization

```python
# Currency
normalizer.normalize_number("$1,234.56M")   # → 1234560000.0
normalizer.normalize_number("€42K")          # → 42000.0

# Units
normalizer.normalize_unit("100 km/h")        # → {"value": 100, "unit": "km/h", "si": 27.78}
```

---

## Batch Processing

```python
texts = ["Text 1...", "Text 2...", "Text 3..."]
normalized = normalizer.normalize_batch(texts, batch_size=100)
```

---

## See Also

<CardGroup cols={2}>
  <Card title="Parse" icon="file-lines" href="parse">
    Parse documents before normalization.
  </Card>
  <Card title="Split" icon="scissors" href="split">
    Chunk normalized text.
  </Card>
  <Card title="Deduplication" icon="copy" href="deduplication">
    Resolve duplicate entities post-normalization.
  </Card>
  <Card title="Pipeline" icon="gear" href="pipeline">
    Include normalization in a pipeline.
  </Card>
</CardGroup>
