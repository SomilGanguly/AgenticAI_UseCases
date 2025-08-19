import os, tempfile
from typing import Optional
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

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

def list_blobs(container: str, prefix: Optional[str] = None):
    client = _blob_client().get_container_client(container)
    return [b.name for b in client.list_blobs(name_starts_with=prefix or "")]

def download_blob(container: str, blob_name: str) -> str:
    blob = _blob_client().get_blob_client(container=container, blob=blob_name)
    local = os.path.join(tempfile.gettempdir(), os.path.basename(blob_name))
    with open(local, "wb") as f:
        f.write(blob.download_blob().readall())
    return local

def upload_file(container: str, local_path: str, dest_blob_name: Optional[str] = None):
    dest = dest_blob_name or os.path.basename(local_path)
    blob = _blob_client().get_blob_client(container=container, blob=dest)
    with open(local_path, "rb") as f:
        blob.upload_blob(f, overwrite=True)
    return blob.url