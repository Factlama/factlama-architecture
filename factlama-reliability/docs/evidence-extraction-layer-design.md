# FactLama — Evidence Extraction Layer

> Future-scope design input. Its separate `factlama-extract` package/repository proposal is not an accepted repository boundary under ADR-001; supplied evidence remains the MVP path.

**Version:** 0.1
**Scope:** `factlama-extract/` package
**Status:** Architecture design

## 1. Purpose

The extraction layer bridges the gap between enterprise data sources and FactLama's core verification engine. It fetches, parses, normalizes, and chunks raw evidence from diverse sources into the standard `Evidence` schema that core expects.

**Key principle**: Core always receives plain text evidence. All complexity of PDF parsing, API authentication, document conversion lives in the extraction layer.

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ENTERPRISE DATA SOURCES                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │Confluence│ │  Drive   │ │SharePoint│ │   APIs   │ │   DBs    │  │
│  │  Pages   │ │  Docs    │ │   Files  │ │  JSON    │ │  Rows    │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
└───────┼────────────┼────────────┼────────────┼────────────┼────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTRACTION LAYER (factlama-extract)              │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Extractor Registry                        │   │
│  │         (auto-detects source type by URI/pattern)           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│       ┌──────────────────────┼──────────────────────┐              │
│       │                      │                      │              │
│       ▼                      ▼                      ▼              │
│  ┌─────────┐           ┌─────────┐           ┌─────────┐          │
│  │ Docling │           │ HTTP    │           │ Custom  │          │
│  │ Extractor│          │ JSON    │           │Connectors│          │
│  │(PDF/Office)│        │Extractor│           │(Confluence,│        │
│  └────┬────┘           └────┬────┘           │Drive,SharePoint)│   │
│       │                     │                └────┬────┘          │
│       └──────────────────────┼──────────────────────┘              │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Normalization Pipeline                       │   │
│  │  • Text extraction                                          │   │
│  │  • Chunking (if needed)                                     │   │
│  │  • Metadata enrichment                                      │   │
│  │  • Locator generation (page, json_path, row, etc.)         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│                    Evidence[] (plain text)                         │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CORE ENGINE (factlama-core)                    │
│                                                                     │
│  • Input: Evidence(extracted_text="...", source, locator)          │
│  • Claim extraction → Evidence mapping → Verification              │
│  • SLM sees only plain text                                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. Design Principles

1. **Separation of concerns**: Extraction logic never enters core
2. **Plain text contract**: Core always receives `extracted_text` (string)
3. **Extensibility**: New extractors can be added without touching core
4. **Auto-detection**: Registry detects source type from URI patterns
5. **Fail gracefully**: Extraction errors return empty evidence list with error metadata
6. **Preserve provenance**: Every extracted Evidence includes source and locator

## 4. Package Structure

```
factlama-extract/
├── factlama_extract/
│   ├── __init__.py
│   ├── base.py              # Extractor ABC
│   ├── registry.py          # Auto-detection by URI/content-type
│   ├── pipeline.py          # Compose multiple extractors
│   ├── config.py            # Auth, rate limits, timeouts
│   │
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── docling.py       # PDF, DOCX, PPTX, HTML via Docling
│   │   ├── http_json.py     # REST/GraphQL APIs
│   │   ├── confluence.py    # Atlassian Confluence
│   │   ├── gdrive.py        # Google Drive (Docs, Sheets, Slides)
│   │   ├── sharepoint.py    # Microsoft SharePoint
│   │   ├── database.py      # SQL databases
│   │   ├── web.py           # Generic web pages
│   │   └── file.py          # Local files
│   │
│   ├── chunkers/
│   │   ├── __init__.py
│   │   ├── semantic.py      # Semantic chunking (future)
│   │   ├── fixed.py         # Fixed-size chunking
│   │   └── sentence.py      # Sentence-based chunking
│   │
│   └── utils/
│       ├── __init__.py
│       ├── auth.py          # Auth helpers (OAuth, API keys)
│       └── retry.py         # Retry logic
│
├── pyproject.toml
├── README.md
└── tests/
    ├── test_docling.py
    ├── test_http_json.py
    └── test_registry.py
```

## 5. Core Interface

### 5.1 Base Extractor

```python
from abc import ABC, abstractmethod
from typing import Any
from factlama.schemas import Evidence

class Extractor(ABC):
    """Base class for all evidence extractors."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Extractor identifier."""
        pass
    
    @property
    def supported_schemes(self) -> list[str]:
        """URI schemes this extractor handles (e.g., ['https', 'http'])."""
        return []
    
    @property
    def supported_content_types(self) -> list[str]:
        """Content types this extractor handles (e.g., ['application/pdf'])."""
        return []
    
    @abstractmethod
    def can_extract(self, source: str, content_type: str | None = None) -> bool:
        """Return True if this extractor can handle the source."""
        pass
    
    @abstractmethod
    def extract(self, source: str, **kwargs) -> list[Evidence]:
        """
        Extract evidence from source.
        
        Args:
            source: URI, path, or identifier for the content
            **kwargs: Extractor-specific options (auth, headers, etc.)
        
        Returns:
            List of Evidence objects with extracted_text populated
        
        Raises:
            ExtractionError: If extraction fails
        """
        pass
```

### 5.2 Extraction Result

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class ExtractionResult:
    """Result of extraction operation."""
    
    evidence: list[Evidence]
    source: str
    extractor: str
    success: bool
    error: str | None = None
    metadata: dict[str, Any] = None
```

### 5.3 Convenience Function

```python
def extract_evidence(
    sources: list[str],
    extractors: list[Extractor] | None = None,
    chunk: bool = False,
    chunk_size: int = 1000,
    **kwargs
) -> list[Evidence]:
    """
    Extract evidence from multiple sources.
    
    Args:
        sources: List of URIs, paths, or identifiers
        extractors: Custom extractor list (uses registry if None)
        chunk: Whether to chunk large documents
        chunk_size: Max characters per chunk
    
    Returns:
        Flattened list of all extracted Evidence
    
    Example:
        >>> evidence = extract_evidence([
        ...     "https://company.atlassian.net/wiki/spaces/HR/pages/12345",
        ...     "s3://bucket/policy.pdf",
        ...     "postgresql://db.company.com/hr?query=SELECT * FROM policies",
        ... ])
        >>> result = verify(question=q, answer=a, context=evidence)
    """
    pass
```

## 6. Supported Source Types

| Source Type | URI Pattern | Extractor | Content Extracted |
|-------------|-------------|-----------|-------------------|
| PDF | `*.pdf`, `s3://*.pdf` | Docling | Text, tables, structure |
| Word | `*.docx`, `*.doc` | Docling | Text, tables |
| Excel | `*.xlsx`, `*.xls` | Docling | Sheets as text tables |
| PowerPoint | `*.pptx`, `*.ppt` | Docling | Slide text |
| Confluence | `*.atlassian.net/wiki/*` | ConfluenceExtractor | Page content |
| Google Drive | `drive.google.com/*`, `docs.google.com/*` | GDriveExtractor | Doc/sheet content |
| SharePoint | `*.sharepoint.com/*` | SharePointExtractor | Document content |
| REST API | `https://api.*`, custom | HTTPJSONExtractor | JSON → text |
| GraphQL | `https://*/graphql` | HTTPJSONExtractor | Response → text |
| Database | `postgresql://`, `mysql://` | DatabaseExtractor | Query results → text |
| Web page | `https://*` (generic) | WebExtractor | Article text |
| Local file | `file://`, `/path/*` | FileExtractor | Based on extension |

## 7. Extractor Implementations

### 7.1 Docling Extractor (PDF, Office)

Uses IBM's Docling library for high-quality document parsing.

```python
from docling.document_converter import DocumentConverter
from factlama.schemas import Evidence, Source

class DoclingExtractor(Extractor):
    """Extract from PDF, DOCX, XLSX, PPTX, HTML using Docling."""
    
    name = "docling"
    supported_content_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]
    
    def extract(self, source: str, **kwargs) -> list[Evidence]:
        converter = DocumentConverter()
        result = converter.convert(source)
        
        # Export as markdown (preserves structure)
        text = result.document.export_to_markdown()
        
        # Create evidence with page-level locators
        evidence_list = []
        for i, page in enumerate(result.document.pages):
            page_text = page.export_to_markdown()
            if page_text.strip():
                evidence_list.append(Evidence(
                    id=f"{self._generate_id(source)}_page_{i+1}",
                    extracted_text=page_text,
                    source=Source(uri=source),
                    locator=Locator(page=i+1),
                    metadata={"extractor": self.name}
                ))
        
        return evidence_list
```

### 7.2 HTTP JSON Extractor

```python
import httpx
import jsonpath_ng

class HTTPJSONExtractor(Extractor):
    """Extract from REST/GraphQL APIs returning JSON."""
    
    name = "http_json"
    supported_schemes = ["http", "https"]
    
    def extract(
        self, 
        source: str,
        method: str = "GET",
        headers: dict | None = None,
        body: dict | None = None,
        json_path: str | None = None,  # JSONPath to extract specific fields
        text_template: str | None = None,  # Jinja template for text output
        **kwargs
    ) -> list[Evidence]:
        
        response = httpx.request(method, source, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        
        # Apply JSONPath if specified
        if json_path:
            data = self._apply_jsonpath(data, json_path)
        
        # Convert to text
        if text_template:
            text = self._render_template(text_template, data)
        else:
            text = self._default_text_format(data)
        
        return [Evidence(
            id=self._generate_id(source),
            extracted_text=text,
            structured_data=data,  # Preserve for programmatic checkers
            source=Source(uri=source),
            metadata={"extractor": self.name, "content_type": "json"}
        )]
```

### 7.3 Confluence Extractor

```python
from atlassian import Confluence

class ConfluenceExtractor(Extractor):
    """Extract from Atlassian Confluence pages."""
    
    name = "confluence"
    
    def can_extract(self, source: str, content_type: str | None = None) -> bool:
        return "atlassian.net/wiki" in source or "confluence" in source
    
    def extract(
        self,
        source: str,
        confluence_url: str | None = None,
        username: str | None = None,
        api_token: str | None = None,
        page_id: str | None = None,
        **kwargs
    ) -> list[Evidence]:
        
        confluence = Confluence(
            url=confluence_url or self._extract_base_url(source),
            username=username,
            password=api_token,
        )
        
        page_id = page_id or self._extract_page_id(source)
        page = confluence.get_page_by_id(page_id, expand="body.storage")
        
        # Extract plain text from HTML storage format
        text = self._html_to_text(page['body']['storage']['value'])
        
        return [Evidence(
            id=f"confluence_{page_id}",
            extracted_text=text,
            source=Source(
                uri=source,
                title=page.get('title'),
            ),
            metadata={
                "extractor": self.name,
                "page_id": page_id,
                "space_key": page.get('space', {}).get('key'),
            }
        )]
```

### 7.4 Database Extractor

```python
import sqlalchemy as sa

class DatabaseExtractor(Extractor):
    """Extract from SQL databases via query."""
    
    name = "database"
    supported_schemes = ["postgresql", "mysql", "sqlite", "mssql", "oracle"]
    
    def extract(
        self,
        source: str,  # Connection string with embedded query
        query: str | None = None,
        **kwargs
    ) -> list[Evidence]:
        
        # Parse connection string and query
        conn_str, query = self._parse_source(source, query)
        
        engine = sa.create_engine(conn_str)
        with engine.connect() as conn:
            result = conn.execute(sa.text(query))
            rows = result.fetchall()
            columns = result.keys()
        
        # Convert rows to text
        evidence_list = []
        for i, row in enumerate(rows):
            row_text = self._row_to_text(columns, row)
            evidence_list.append(Evidence(
                id=f"{self._generate_id(source)}_row_{i}",
                extracted_text=row_text,
                source=Source(uri=source),
                locator=Locator(row=i),
                metadata={"extractor": self.name}
            ))
        
        return evidence_list
```

## 8. Chunking Strategies

For large documents, the extraction layer can chunk before passing to core.

### 8.1 Fixed-Size Chunking

```python
def chunk_fixed(text: str, max_chars: int = 1000, overlap: int = 100) -> list[str]:
    """Split text into fixed-size chunks with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks
```

### 8.2 Sentence-Based Chunking

```python
import nltk

def chunk_sentences(text: str, max_sentences: int = 5) -> list[str]:
    """Split text by sentences, respecting boundaries."""
    sentences = nltk.sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = " ".join(sentences[i:i + max_sentences])
        chunks.append(chunk)
    return chunks
```

## 9. Registry and Auto-Detection

```python
class ExtractorRegistry:
    """Auto-detect and route to appropriate extractor."""
    
    def __init__(self):
        self._extractors: list[Extractor] = []
        self._register_defaults()
    
    def _register_defaults(self):
        """Register built-in extractors."""
        self.register(DoclingExtractor())
        self.register(HTTPJSONExtractor())
        self.register(ConfluenceExtractor())
        self.register(GDriveExtractor())
        self.register(SharePointExtractor())
        self.register(DatabaseExtractor())
        self.register(WebExtractor())
    
    def register(self, extractor: Extractor):
        self._extractors.append(extractor)
    
    def detect(self, source: str, content_type: str | None = None) -> Extractor | None:
        """Find extractor that can handle this source."""
        for extractor in self._extractors:
            if extractor.can_extract(source, content_type):
                return extractor
        return None
    
    def extract(self, source: str, **kwargs) -> list[Evidence]:
        """Auto-detect extractor and run."""
        extractor = self.detect(source)
        if not extractor:
            raise ExtractionError(f"No extractor found for: {source}")
        return extractor.extract(source, **kwargs)
```

## 10. Error Handling

```python
class ExtractionError(Exception):
    """Base error for extraction failures."""
    pass

class UnsupportedSourceError(ExtractionError):
    """No extractor available for source type."""
    pass

class AuthenticationError(ExtractionError):
    """Authentication failed for protected source."""
    pass

class SourceUnavailableError(ExtractionError):
    """Source could not be reached."""
    pass

class ParsingError(ExtractionError):
    """Content could not be parsed."""
    pass
```

## 11. Configuration

```python
from pydantic import BaseModel

class ExtractionConfig(BaseModel):
    """Configuration for extraction layer."""
    
    # Authentication
    confluence_url: str | None = None
    confluence_username: str | None = None
    confluence_api_token: str | None = None
    
    gdrive_credentials_path: str | None = None
    
    sharepoint_client_id: str | None = None
    sharepoint_client_secret: str | None = None
    
    # HTTP defaults
    http_timeout: int = 30
    http_retry_count: int = 3
    
    # Chunking
    default_chunk_size: int = 1000
    chunk_overlap: int = 100
    enable_chunking: bool = False
    
    # Output
    include_structured_data: bool = True  # Include in Evidence.structured_data
```

## 12. Integration with Core

### 12.1 SDK Usage

```python
from factlama import verify
from factlama_extract import extract_evidence

# Extract from multiple sources
evidence = extract_evidence([
    "https://company.atlassian.net/wiki/spaces/HR/pages/12345",
    "s3://company-policies/employee-handbook.pdf",
    "https://api.internal.com/v1/policies/remote-work",
])

# Pass to core verification
result = verify(
    question="What is the remote work policy?",
    answer="Employees can work remotely 3 days per week.",
    context=evidence,  # Already normalized to plain text
)
```

### 12.2 Direct Evidence Construction

For cases where extraction is done upstream (e.g., in RAG pipeline):

```python
from factlama import verify, Evidence

# Customer's RAG system already extracted text
evidence = [
    Evidence(
        id="chunk_001",
        extracted_text="Remote work is permitted up to 3 days per week with manager approval.",
        source={"uri": "confluence://HR/remote-work-policy"},
    )
]

result = verify(question=q, answer=a, context=evidence)
```

## 13. Deployment Options

### 13.1 SDK-Side Extraction (Recommended for Phase 1)

```
Customer Application
        |
        v
factlama-extract (runs in customer process)
        |
        v
Evidence[] (plain text)
        |
        v
factlama-core (verification)
```

**Pros**: No infrastructure, works locally, customer controls auth
**Cons**: Customer must install extraction dependencies

### 13.2 Collector/API-Side Extraction (Future)

```
Customer Application
        |
        v
FactLama API
        |
        +---> Extraction Service
        |
        v
factlama-core
```

**Pros**: Centralized extraction, consistent, no customer dependencies
**Cons**: More infrastructure, data egress concerns

## 14. Open Source Dependencies

| Library | Purpose | License | Notes |
|---------|---------|---------|-------|
| Docling | PDF/Office parsing | MIT | Best table/structure extraction |
| atlassian-python-api | Confluence/Jira | Apache 2.0 | Official API client |
| google-api-python-client | Google Drive | Apache 2.0 | Official Google client |
| trafilatura | Web scraping | Apache 2.0 | Clean article extraction |
| httpx | HTTP client | BSD | Modern async support |
| sqlalchemy | Database | MIT | Universal DB interface |
| python-docx | Word docs | MIT | Alternative to Docling |
| openpyxl | Excel | MIT | Alternative to Docling |

## 15. Phase Plan

### Phase 1.5 — Basic Extraction

**Goal**: Prove the separation works

- [ ] `factlama-extract` package skeleton
- [ ] `Extractor` ABC and registry
- [ ] Docling extractor (PDF, DOCX)
- [ ] HTTP JSON extractor
- [ ] `extract_evidence()` convenience function
- [ ] Tests for each extractor
- [ ] Integration test with core

### Phase 4 — SDK Integration

- [ ] Confluence extractor
- [ ] Google Drive extractor
- [ ] Database extractor
- [ ] Chunking strategies
- [ ] Configuration management

### Phase 6 — Enterprise Connectors

- [ ] SharePoint extractor
- [ ] S3/GCS blob extraction
- [ ] Streaming for large files
- [ ] Caching layer

## 16. Success Criteria

The extraction layer is successful when:

1. **Core never knows about PDFs, APIs, or databases** — it only sees `extracted_text`
2. **New sources can be added without touching core** — just register a new extractor
3. **Extraction failures don't crash verification** — empty evidence + error metadata
4. **Evidence is traceable** — every `Evidence` has `source` and `locator`
5. **SDK can extract from common enterprise sources** — Confluence, Drive, APIs

## 17. Relationship to SLM

The FactLama SLM is **not** an extractor. The separation is clear:

| FactLama SLM | Extraction Layer |
|--------------|------------------|
| Understands text semantically | Fetches and parses raw sources |
| Maps claims to evidence | Normalizes to `Evidence` schema |
| Scores groundedness | Handles auth, rate limits, schemas |
| Explains verdicts | Produces clean text for SLM |

**The SLM never sees raw PDF bytes or API JSON** — it works on the normalized `extracted_text` with `locator` for explainability. This keeps the SLM small, fast, and focused on verification reasoning.

## 18. Final Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     ENTERPRISE SOURCES                          │
│   Confluence | Drive | SharePoint | APIs | DBs | PDFs | Web    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  EXTRACTION LAYER                               │
│                    (factlama-extract)                           │
│                                                                 │
│  • Auto-detect source type                                      │
│  • Fetch and authenticate                                       │
│  • Parse and extract text                                       │
│  • Preserve locators (page, json_path, row)                    │
│  • Output: Evidence(extracted_text="...")                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CORE ENGINE                                │
│                    (factlama-core)                              │
│                                                                 │
│  • Input: Evidence with plain text only                        │
│  • Claim extraction                                             │
│  • Evidence mapping                                             │
│  • Verification (via ModelProvider)                            │
│  • Scoring and policy                                           │
│  • Output: VerificationResult                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SLM (Phase 3)                             │
│                                                                 │
│  • Trained on Evidence + claims                                 │
│  • Sees only extracted_text                                     │
│  • Uses locators for explainability                            │
└─────────────────────────────────────────────────────────────────┘
```

This separation ensures FactLama can scale to any enterprise data source while keeping the core verification engine focused, testable, and independent of extraction complexity.
