# Pinecone RAG API

A production-ready REST API for building RAG (Retrieval Augmented Generation) applications using Pinecone vector database and OpenAI.

## Features

- **Document Processing**: Upload and process PDF, DOCX, TXT, and Markdown files
- **Semantic Search**: Vector-based document retrieval using OpenAI embeddings
- **RAG Chat**: Ask questions and get answers grounded in your documents
- **Flexible Storage**: Local filesystem or Cloudflare R2 cloud storage
- **RESTful API**: Clean, versioned API with OpenAPI documentation

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (for local development)
- OpenAI API key
- Pinecone account and index

## Quick Start

### Using Docker (Recommended)

```bash
# Build the image
docker build -t pinecone-rag-api .

# Run the container
docker run -p 8000:8000 --env-file .env pinecone-rag-api
```

The API will be available at `http://localhost:8000/docs`

### Local Development

#### 1. Clone the repository

```bash
git clone https://github.com/your-username/pinecone-rag-api.git
cd pinecone-rag-api
```

#### 2. Install dependencies

```bash
uv sync
```

#### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=rag-docs

# Optional - Cloudflare R2 (for cloud storage)
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=your-bucket-name
```

#### 4. Create a Pinecone index

Create an index in [Pinecone Console](https://app.pinecone.io/) with:

- **Dimensions**: 1536 (for `text-embedding-3-small`)
- **Metric**: cosine

#### 5. Start the server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000/docs`

## API Reference

All endpoints are prefixed with `/api/v1`

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents` | Upload a document (PDF, DOCX, TXT, MD) |
| `GET` | `/documents` | List all uploaded documents |
| `GET` | `/documents/{filename}` | Download a specific document |
| `DELETE` | `/documents/{filename}` | Delete document and its vectors |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Ask a question about your documents |

### Examples

**Upload a document:**

```bash
curl -X POST "http://localhost:8000/api/v1/documents" \
  -F "file=@document.pdf"
```

**Ask a question:**

```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

**Response:**

```json
{
  "question": "What is the main topic of the document?",
  "answer": "Based on the documents, the main topic is...",
  "sources": [
    {
      "filename": "document.pdf",
      "chunk_index": 0,
      "score": 0.92,
      "text": "..."
    }
  ]
}
```

## Architecture

```
app/
├── main.py              # FastAPI application entrypoint
├── config.py            # Settings and environment variables
├── routers/
│   ├── chat.py          # Chat/RAG endpoints
│   ├── documents_local.py   # Document endpoints (local storage)
│   └── documents_r2.py      # Document endpoints (R2 storage)
├── schemas/
│   ├── chat.py          # Chat request/response models
│   └── document.py      # Document request/response models
└── services/
    ├── document_service.py   # Text extraction and chunking
    ├── embedding_service.py  # OpenAI embeddings
    ├── llm_service.py        # RAG answer generation
    ├── pinecone_service.py   # Vector database operations
    └── storage_service.py    # Cloudflare R2 operations
```

### How It Works

1. **Document Upload**: Files are processed to extract text, split into overlapping chunks (500 chars, 50 overlap), embedded using OpenAI, and stored in Pinecone with metadata.

2. **RAG Query**: Questions are embedded and used to search Pinecone for relevant chunks. The top results are sent as context to the LLM, which generates an answer grounded in the retrieved documents.

### Storage Modes

The API automatically selects storage mode based on configuration:

- **Local Storage** (default): Documents stored in `uploads/` directory
- **Cloudflare R2**: Enabled when `R2_ACCESS_KEY_ID` is set

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** - Web framework
- **[Pinecone](https://www.pinecone.io/)** - Vector database
- **[OpenAI](https://openai.com/)** - Embeddings and LLM
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation
- **[pypdf](https://pypdf.readthedocs.io/)** - PDF processing
- **[python-docx](https://python-docx.readthedocs.io/)** - DOCX processing
- **[boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)** - Cloudflare R2 (S3-compatible)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for embeddings and chat |
| `OPENAI_MODEL` | Yes | Model for chat completions |
| `PINECONE_API_KEY` | Yes | Pinecone API key |
| `PINECONE_INDEX_NAME` | Yes | Name of your Pinecone index |
| `R2_ACCOUNT_ID` | No | Cloudflare account ID (for R2 storage) |
| `R2_ACCESS_KEY_ID` | No | R2 access key ID |
| `R2_SECRET_ACCESS_KEY` | No | R2 secret access key |
| `R2_BUCKET_NAME` | No | R2 bucket name |

## License

MIT License - see [LICENSE](LICENSE) for details.
