import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

# Optional Cosmos DB logging with graceful no-op if not configured
COSMOS_URL = os.environ.get("COSMOS_DB_URL")
COSMOS_KEY = os.environ.get("COSMOS_DB_KEY")
COSMOS_DB = os.environ.get("COSMOS_DB_DATABASE", "assessment")
COSMOS_CONTAINER = os.environ.get("COSMOS_DB_CONTAINER", "question_runs")

class TelemetryLogger:
    def __init__(self):
        self._client = None
        self._container = None
        if COSMOS_URL and COSMOS_KEY:
            try:
                from azure.cosmos import CosmosClient
                from azure.cosmos.partition_key import PartitionKey
                self._client = CosmosClient(COSMOS_URL, credential=COSMOS_KEY)
                # Ensure database and container exist
                db = self._client.create_database_if_not_exists(id=COSMOS_DB)
                self._container = db.create_container_if_not_exists(
                    id=COSMOS_CONTAINER,
                    partition_key=PartitionKey(path="/appId"),
                    offer_throughput=400
                )
            except Exception:
                self._client = None
                self._container = None

    def log_question_result(
        self,
        app_id: str,
        run_id: str,
        question_id: str,
        question_text: str,
        answer: str,
        confidence: str,
        provenance: str,
        retrieval_hits: Optional[List[str]] = None,
    ) -> None:
        if not self._container:
            return
        doc = {
            "id": str(uuid.uuid4()),
            "appId": app_id,
            "runId": run_id,
            "questionId": str(question_id),
            "question": question_text,
            "answer": answer,
            "confidence": confidence,
            "provenance": provenance,
            "retrievalHits": retrieval_hits or [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            self._container.create_item(doc)
        except Exception:
            pass
