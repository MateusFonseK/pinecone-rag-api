# Pinecone RAG API

A RESTful API for semantic search and Q&A on documents using RAG (Retrieval Augmented Generation) with Pinecone and OpenAI.

## Features

- Upload and manage PDF, DOCX, TXT and Markdown documents
- Automatic text extraction and chunking
- Semantic search using vector embeddings
- Natural language Q&A powered by OpenAI
- RESTful API design with versioning

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- OpenAI API key
- Pinecone API key and index

## Installation

```bash
git clone <repo-url>
cd pinecone-rag-api

cp .env.example .env
# Edit .env with your API keys

uv sync
```

## Configuration

Create a `.env` file with:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
PINECONE_API_KEY=...
PINECONE_INDEX_NAME=your-index
```

### Pinecone Index Setup

Create an index at [pinecone.io](https://www.pinecone.io/) with:
- **Dimensions**: 1536 (for text-embedding-3-small)
- **Metric**: cosine

## Running

```bash
./run.sh
```

Or manually:

```bash
uv run uvicorn app.main:app --reload
```

API available at `http://localhost:8000`

## API Reference

Base URL: `/api/v1`

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents` | Upload a document |
| `GET` | `/api/v1/documents` | List all documents |
| `GET` | `/api/v1/documents/{filename}` | Download a document |
| `DELETE` | `/api/v1/documents/{filename}` | Delete a document |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat` | Ask a question about documents |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |

## Usage Examples

### Upload a document

```bash
curl -X POST http://localhost:8000/api/v1/documents \
  -F "file=@document.pdf"
```

Response (201 Created):
```json
{
  "success": true,
  "filename": "document.pdf",
  "chunks_created": 15,
  "message": "Document processed successfully. Created 15 chunks."
}
```

### List documents

```bash
curl http://localhost:8000/api/v1/documents
```

Response:
```json
{
  "documents": [
    {"filename": "document.pdf", "size_bytes": 102400}
  ],
  "total": 1
}
```

### Download a document

```bash
curl http://localhost:8000/api/v1/documents/document.pdf -o document.pdf
```

### Delete a document

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/document.pdf
```

### Ask a question

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

Response:
```json
{
  "question": "What is the main topic of the document?",
  "answer": "The document discusses...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_index": 0,
      "score": 0.89,
      "text": "..."
    }
  ]
}
```

## Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
pinecone-rag-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings and configuration
│   ├── routers/
│   │   ├── documents.py     # Document endpoints
│   │   └── chat.py          # Chat endpoint
│   ├── schemas/
│   │   ├── document.py      # Document models
│   │   └── chat.py          # Chat models
│   └── services/
│       ├── document_service.py   # Document processing
│       ├── embedding_service.py  # Text embeddings
│       ├── pinecone_service.py   # Vector database
│       └── llm_service.py        # LLM integration
├── uploads/                 # Uploaded documents
├── .env.example
├── pyproject.toml
└── README.md
```

## License

MIT
