import os, io
import base64
from typing import List
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
from index import create_or_update_index

# Remove global ACCOUNT_URL/CONN_STR reads; fetch env at call time
def _blob_client() -> BlobServiceClient:
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")
    if conn_str:
        return BlobServiceClient.from_connection_string(conn_str)
    if account_url:
        if "?" in account_url:  # SAS baked in
            return BlobServiceClient(account_url=account_url)
        return BlobServiceClient(account_url=account_url, credential=DefaultAzureCredential())
    raise RuntimeError("Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL")

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX"]
SEARCH_KEY = os.environ["AZURE_SEARCH_ADMIN_KEY"]

def _download_text(container: str, blob_name: str) -> str:
    bc = _blob_client().get_blob_client(container=container, blob=blob_name)
    data = bc.download_blob().readall()
    name = blob_name.lower()
    if name.endswith(".txt") or name.endswith(".md"):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        from docx import Document
        f = io.BytesIO(data)
        doc = Document(f)
        return "\n".join([p.text for p in doc.paragraphs])
    if name.endswith(".pdf"):
        # Light-weight extraction
        from pypdf import PdfReader
        f = io.BytesIO(data)
        reader = PdfReader(f)
        return "\n".join([(page.extract_text() or "") for page in reader.pages])
    # Fallback: treat as text
    return data.decode("utf-8", errors="ignore")

def _chunk(text: str, size: int = 1200, overlap: int = 200) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+size]
        chunks.append(" ".join(chunk_words))
        i += max(1, size - overlap)
    return chunks

def _safe_doc_id(app_id: str, path: str, ci: int) -> str:
    # URL-safe Base64 of a composite key => only letters, digits, _ and - (and = padding)
    raw = f"{app_id}|{path}|{ci}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")

def index_container(app_id: str, container: str, skip_patterns: List[str] = None):
    create_or_update_index()

    search = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, AzureKeyCredential(SEARCH_KEY))
    bs = _blob_client().get_container_client(container)
    skip_patterns = skip_patterns or [".xlsx"]  # do not index Excel questionnaires

    batch = []
    for blob in bs.list_blobs():
        name = blob.name
        if any(name.lower().endswith(p) for p in skip_patterns):
            continue
        try:
            text = _download_text(container, name)
            if not text or not text.strip():
                continue
            chunks = _chunk(text)
            for ci, ch in enumerate(chunks):
                doc = {
                    "id": _safe_doc_id(app_id, f"{container}/{name}", ci),
                    "appId": app_id,
                    "title": os.path.basename(name),
                    "content": ch,
                    "source": "blob",
                    "path": f"{container}/{name}",
                    "chunkId": f"{ci}",
                }
                batch.append(doc)
            if len(batch) >= 1000:
                search.upload_documents(documents=batch)
                batch = []
        except Exception as e:
            print(f"Failed {name}: {e}")

    if batch:
        search.upload_documents(documents=batch)
    print("Indexing complete.")