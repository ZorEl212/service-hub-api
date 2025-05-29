from typing import List, Optional

from elasticsearch import AsyncElasticsearch, helpers

from models.elastic.es_schema import ServiceProviderSearchDoc


class ElasticSearchConfig:
    """Configuration for ElasticSearch."""

    # ElasticSearch host
    HOST = "http://localhost:9200"
    # Index names
    INDEX_PROVIDER = "service_providers_v2"

    def __init__(self):
        self.client = AsyncElasticsearch(self.HOST)
        self.indices = {
            "provider": self.INDEX_PROVIDER,
        }

    # elastic/search.py

    async def search_providers(
            self,
            query: Optional[str] = None,
            category: Optional[str] = None,
            size: int = 10
    ) -> List[str]:
        must_clauses = []

        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^4",
                        "description^3",
                        "category_text^3",
                        "service_titles^2",
                        "service_descriptions",
                        "category_titles^2",
                        "category_descriptions"
                    ],
                    "fuzziness": "AUTO"
                }
            })

        if category:
            must_clauses.append({
                "multi_match": {
                    "query": category,
                    "fields": [
                        "category_titles^3",
                        "category_text^2",
                        "category_descriptions"
                    ]
                }
            })

        if not must_clauses:
            return []

        res = await self.client.search(
            index=self.indices["provider"],
            query={
                "bool": {
                    "must": must_clauses
                }
            },
            size=size,
            _source=["id"]
        )

        return [hit["_source"]["id"] for hit in res["hits"]["hits"]]

    async def bulk_index(self, index:str, docs: List[ServiceProviderSearchDoc]):
        """Bulk index documents into ElasticSearch."""
        actions = [
            {
                "_index": index,
                "_id": doc.id,
                "_source": doc.model_dump()
            }
            for doc in docs
        ]
        await helpers.async_bulk(self.client, actions)