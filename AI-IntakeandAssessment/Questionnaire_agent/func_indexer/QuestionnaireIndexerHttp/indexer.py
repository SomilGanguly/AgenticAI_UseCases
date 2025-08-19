import os
import io
import base64
import logging
from typing import List, Dict

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    CorsOptions,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
)
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

# -----------------------------
# Environment configuration
# -----------------------------
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX", "")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_ADMIN_KEY", "")
SEM_CONFIG_NAME = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIG")

# Storage: prefer connection string, then account URL (optionally with SAS), else MSI
AZ_STORAGE_CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZ_STORAGE_ACCOUNT_URL = os.getenv("AZURE_STORAGE_ACCOUNT_URL")


# -----------------------------
# Helpers matching existing repo
# -----------------------------

def _blob_client() -> BlobServiceClient:
    if AZ_STORAGE_CONN_STR:
        return BlobServiceClient.from_connection_string(AZ_STORAGE_CONN_STR)
    if AZ_STORAGE_ACCOUNT_URL:
        # If SAS provided inline, no credential needed
        if "?" in AZ_STORAGE_ACCOUNT_URL:
            return BlobServiceClient(account_url=AZ_STORAGE_ACCOUNT_URL)
        return BlobServiceClient(account_url=AZ_STORAGE_ACCOUNT_URL, credential=DefaultAzureCredential())
    raise RuntimeError("Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL")


def create_or_update_index():
    if not SEARCH_ENDPOINT or not SEARCH_INDEX:
        raise RuntimeError("AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_INDEX must be set")
    if not SEARCH_KEY:
        logging.warning("AZURE_SEARCH_ADMIN_KEY not set; index creation may fail without permissions")
    idx_client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="appId", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
        SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="path", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="chunkId", type=SearchFieldDataType.String, filterable=True),
    ]

    index = SearchIndex(
        name=SEARCH_INDEX,
        fields=fields,
        cors_options=CorsOptions(allowed_origins=["*"], max_age_in_seconds=60),
    )

    if SEM_CONFIG_NAME:
        index.semantic_search = SemanticSearch(configurations=[
            SemanticConfiguration(
                name=SEM_CONFIG_NAME,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")],
                ),
            )
        ])

    try:
        # If exists, delete then create fresh (matching repo behavior)
        idx_client.get_index(SEARCH_INDEX)
        idx_client.delete_index(SEARCH_INDEX)
    except Exception:
        pass

    idx_client.create_index(index)
    logging.info("Index %s created/updated", SEARCH_INDEX)


def _download_text(container: str, blob_name: str) -> str:
    bc = _blob_client().get_blob_client(container=container, blob=blob_name)
    data = bc.download_blob().readall()
    name = blob_name.lower()
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        from docx import Document  # lazy import
        f = io.BytesIO(data)
        doc = Document(f)
        return "\n".join([p.text for p in doc.paragraphs])
    if name.endswith(".pdf"):
        from pypdf import PdfReader  # lazy import
        f = io.BytesIO(data)
        reader = PdfReader(f)
        return "\n".join([(page.extract_text() or "") for page in reader.pages])
    # Fallback: treat as text
    return data.decode("utf-8", errors="ignore")


def _chunk(text: str, size: int = 1200, overlap: int = 200) -> List[str]:
    words = text.split()
    chunks: List[str] = []
    i = 0
    while i < len(words):
        chunk_words = words[i : i + size]
        chunks.append(" ".join(chunk_words))
        i += max(1, size - overlap)
    return chunks


def _safe_doc_id(app_id: str, path: str, ci: int) -> str:
    raw = f"{app_id}|{path}|{ci}".encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii")


# -----------------------------
# Public functions called by HTTP
# -----------------------------

def index_blob(app_id: str, container: str, blob_name: str) -> Dict:
    # Ensure index exists (idempotent)
    create_or_update_index()

    # Skip Excel questionnaires by default
    if blob_name.lower().endswith(".xlsx"):
        logging.info("Skipping Excel file: %s", blob_name)
        return {"blobName": blob_name, "chunks": 0, "uploaded": 0, "failed": 0}

    search = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, AzureKeyCredential(SEARCH_KEY))

    text = _download_text(container, blob_name)
    if not text or not text.strip():
        return {"blobName": blob_name, "chunks": 0, "uploaded": 0, "failed": 0}

    chunks = _chunk(text)

    batch: List[Dict] = []
    uploaded = 0
    failed = 0

    for ci, ch in enumerate(chunks):
        path = f"{container}/{blob_name}"
        doc = {
            "id": _safe_doc_id(app_id, path, ci),
            "appId": app_id,
            "title": os.path.basename(blob_name),
            "content": ch,
            "source": "blob",
            "path": path,
            "chunkId": f"{ci}",
        }
        batch.append(doc)
        if len(batch) >= 1000:
            resp = search.upload_documents(documents=batch)
            uploaded += sum(1 for r in resp if r.succeeded)
            failed += len(resp) - (sum(1 for r in resp if r.succeeded))
            batch = []

    if batch:
        resp = search.upload_documents(documents=batch)
        uploaded += sum(1 for r in resp if r.succeeded)
        failed += len(resp) - (sum(1 for r in resp if r.succeeded))

    return {"blobName": blob_name, "chunks": len(chunks), "uploaded": uploaded, "failed": failed}


def index_container(app_id: str, container: str) -> Dict:
    # Ensure index exists (idempotent)
    create_or_update_index()

    search = SearchClient(SEARCH_ENDPOINT, SEARCH_INDEX, AzureKeyCredential(SEARCH_KEY))
    bs = _blob_client().get_container_client(container)

    total_uploaded = 0
    total_failed = 0
    total_chunks = 0
    total_blobs = 0

    batch: List[Dict] = []

    for blob in bs.list_blobs():
        name = blob.name
        # Skip Excel questionnaires
        if name.lower().endswith(".xlsx"):
            continue
        try:
            text = _download_text(container, name)
            if not text or not text.strip():
                continue
            chunks = _chunk(text)
            total_chunks += len(chunks)
            total_blobs += 1
            for ci, ch in enumerate(chunks):
                path = f"{container}/{name}"
                doc = {
                    "id": _safe_doc_id(app_id, path, ci),
                    "appId": app_id,
                    "title": os.path.basename(name),
                    "content": ch,
                    "source": "blob",
                    "path": path,
                    "chunkId": f"{ci}",
                }
                batch.append(doc)
            if len(batch) >= 1000:
                resp = search.upload_documents(documents=batch)
                uploaded = sum(1 for r in resp if r.succeeded)
                total_uploaded += uploaded
                total_failed += len(resp) - uploaded
                batch = []
        except Exception as e:  # pragma: no cover
            logging.exception("Failed %s: %s", name, e)
            total_failed += 1

    if batch:
        resp = search.upload_documents(documents=batch)
        uploaded = sum(1 for r in resp if r.succeeded)
        total_uploaded += uploaded
        total_failed += len(resp) - uploaded

    return {"blobs": total_blobs, "chunks": total_chunks, "uploaded": total_uploaded, "failed": total_failed}
