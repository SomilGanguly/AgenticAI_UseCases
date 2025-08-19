import os
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchFieldDataType, SearchableField, CorsOptions,
    SemanticConfiguration, SemanticPrioritizedFields, SemanticField, SemanticSearch
)
from azure.core.credentials import AzureKeyCredential

SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT")
SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX")
SEARCH_KEY = os.environ.get("AZURE_SEARCH_ADMIN_KEY")

def create_or_update_index():
    client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))

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

    sem_name = os.environ.get("AZURE_SEARCH_SEMANTIC_CONFIG")
    if sem_name:
        index.semantic_search = SemanticSearch(configurations=[
            SemanticConfiguration(
                name=sem_name,
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")],
                )
            )
        ])

    try:
        client.get_index(SEARCH_INDEX)
        client.delete_index(SEARCH_INDEX)
    except Exception:
        pass

    client.create_index(index)
    print(f"Index {SEARCH_INDEX} created.")