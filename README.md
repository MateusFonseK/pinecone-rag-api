# Ask Your Docs

API for semantic search and Q&A on documents using RAG (Retrieval Augmented Generation).

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- OpenAI account (API key)
- Pinecone account (API key + index created)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ask-your-docs

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your keys

# Install dependencies
uv sync
```

## Pinecone Setup

1. Create an account at [pinecone.io](https://www.pinecone.io/)
2. Create an index with:
   - **Dimensions**: 1536 (compatible with text-embedding-3-small)
   - **Metric**: cosine

## Running

```bash
./run.sh
```

Or manually:

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/documents/upload` | Upload document (PDF/DOCX) |
| GET | `/documents/list` | List documents |
| DELETE | `/documents/{filename}` | Delete document |
| POST | `/chat` | Ask a question about documents |

## Usage

### Upload document

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@document.pdf"
```

### Ask a question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the summary of the document?"}'
```

## Interactive Documentation

Access `http://localhost:8000/docs` for Swagger documentation.
