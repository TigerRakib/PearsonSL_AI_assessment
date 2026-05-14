# Pearson Specter Litt — Legal Document Intelligence Pipeline

## Overview

This system processes **messy legal documents** — scanned pages, low-resolution PDFs, handwritten notes, partially illegible records — and turns them into structured, grounded data for downstream retrieval and drafting.

```
                    ┌──────────────────────────┐
                    │     INPUT DOCUMENT       │
                    │  (any format, any mess)  │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │   1. MIME ROUTING    👈  │
                    │   python-magic detection  │
                    └───────┬──────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
    ┌─────────▼──────┐           ┌────────▼─────────┐
    │  Digital PDF   │           │  Image-based      │
    │  → PyMuPDF     │           │  → Pre-process    │
    │  → direct text │           │  → OCR (later)    │
    └────────────────┘           └───────────────────┘
```

## Quick Start

```bash
# 1. Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start FastAPI dev server
uvicorn app.main:app --reload

# 4. Check health
curl http://localhost:8000/health
```

## File Upload And MIME Routing API

The service stores uploaded files in `uploads/` by default and writes JSON metadata
beside them in `uploads/.metadata/`. Configure the location and size limit with
`UPLOAD_DIR` and `MAX_FILE_SIZE_MB` in `.env`.

Each upload is MIME-routed after it is saved using `python-magic` when available,
with filename/content-type fallback. The route is included in the upload response
as `mime_route` and is available later from `GET /files/{file_id}/route`.

Supported routes:

- `pdf` for `application/pdf`
- `image_ocr` for PNG, JPEG/JPG, and TIFF images
- `docx` for Word documents
- `text` for text-like files such as TXT, CSV, JSON, XML, Markdown, and RTF
- `unsupported` when no ingestion route exists yet

PDFs are classified before processing:

- `digital_pdf` uses `direct_extraction`
- `scanned_pdf` uses `ocr`
- `hybrid_pdf` uses `extraction_with_ocr_fallback`

Image uploads can be preprocessed for OCR with OpenCV:

- grayscale
- denoise
- resize
- adaptive threshold
- sharpen

```bash
# Upload a file
curl -F "file=@contract.pdf" http://localhost:8000/files

# List uploaded files
curl http://localhost:8000/files

# Inspect MIME routing for an upload
curl http://localhost:8000/files/{file_id}/route

# Extract embedded PDF text
curl -X POST http://localhost:8000/files/{file_id}/extract

# Preprocess an image upload for OCR
curl -X POST http://localhost:8000/files/{file_id}/preprocess

# Download a file by id
curl -OJ http://localhost:8000/files/{file_id}/download

# Delete a file by id
curl -X DELETE http://localhost:8000/files/{file_id}
```

## Project Structure

```
app/
├── api/
│   ├── routes/               # FastAPI route handlers
│   ├── schemas/              # API request/response schemas
│   └── dependencies/         # FastAPI dependency providers
├── ingestion/                # MIME routing, PDF classification, OCR prep
├── extraction/               # Cleaning, metadata, sections, chunk assembly
├── chunking/                 # Recursive/semantic chunking and overlap
├── embeddings/               # Embedding service, model loader, vectorizer
├── vectordb/                 # Qdrant client, collections, indexing
├── retrieval/                # Dense, BM25, hybrid retrieval, reranking
├── generation/               # Prompts, grounded generation, citations
├── feedback/                 # User edit/retrieval feedback learning
├── evaluation/               # Retrieval, grounding, OCR metrics
├── storage/                  # File store, metadata store, cache
├── models/                   # Domain models
├── utils/                    # Config, logging, helpers, exceptions
└── main.py

data/
├── raw/
├── processed/
├── chunks/
├── embeddings/
└── feedback/

tests/
├── ingestion/
├── retrieval/
├── generation/
└── feedback/
```
