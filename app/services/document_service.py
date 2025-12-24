import hashlib
from pypdf import PdfReader
from docx import Document
from app.services.pinecone_service import upsert_document, list_ids_by_filename, delete_by_ids


# Directory where uploaded files are stored
UPLOAD_DIR = "uploads"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def _generate_doc_id(filename: str) -> str:

    return hashlib.md5(filename.encode()).hexdigest()


def _extract_text_from_pdf(file_path: str) -> str:

    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def _extract_text_from_docx(file_path: str) -> str:

    doc = Document(file_path)
    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text


def _extract_text_from_txt(file_path: str) -> str:

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _extract_text(file_path: str) -> str:

    lower_path = file_path.lower()

    if lower_path.endswith(".pdf"):
        return _extract_text_from_pdf(file_path)
    elif lower_path.endswith(".docx"):
        return _extract_text_from_docx(file_path)
    elif lower_path.endswith(".txt") or lower_path.endswith(".md"):
        return _extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format. Allowed: {ALLOWED_EXTENSIONS}")


def _split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:

    chunks = []
    start = 0

    while start < len(text):

        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - overlap

    return chunks


def process_document(filename: str, file_path: str) -> int:

    text = _extract_text(file_path)

    if not text.strip():
        raise ValueError("Could not extract text from document")

    chunks = _split_into_chunks(text)

    base_id = _generate_doc_id(filename)

    for i, chunk in enumerate(chunks):
        doc_id = f"{base_id}_{i}"
        metadata = {
            "filename": filename,
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        upsert_document(doc_id, chunk, metadata)

    return len(chunks)


def delete_document_by_filename(filename: str) -> int:

    base_id = _generate_doc_id(filename)
    ids = list_ids_by_filename(base_id)

    if not ids:
        return 0

    delete_by_ids(ids)

    return len(ids)
