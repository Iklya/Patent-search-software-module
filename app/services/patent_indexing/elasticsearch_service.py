from elasticsearch import AsyncElasticsearch, NotFoundError


class ElasticsearchService:
    def __init__(self):
        self.client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
        self.index_name = "patents"
        self.meta_index = "index_meta"
        self.meta_doc_id = "patent_index_state"
    
    
    async def create_index_if_not_exists(self):
        exists = await self.client.indices.exists(index=self.index_name)

        if not exists:
            await self.client.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "patent_id": {"type": "integer"},
                            "publication_number": {"type": "keyword"},
                            "application_number": {"type": "keyword"},
                            "title": {"type": "text"},
                            "abstract": {"type": "text"},
                            "description": {"type": "text"},
                            "claims": {"type": "text"},
                            "inventors": {"type": "keyword"},
                            "classifications": {"type": "keyword"},
                            "filing_date": {"type": "date"},
                            "publication_date": {"type": "date"}
                        }
                    }
                }
            )
    

    async def create_meta_index_if_not_exists(self):
        exists = await self.client.indices.exists(index=self.meta_index)

        if not exists:
            await self.client.indices.create(index=self.meta_index)


    async def get_last_indexed_id(self):
        try:
            result = await self.client.get(
                index=self.meta_index,
                id=self.meta_doc_id
            )
            return result["_source"]["last_indexed_patent_id"]
        
        except NotFoundError:
            return 0


    async def update_last_indexed_id(self, last_id):
        await self.client.index(
            index=self.meta_index,
            id=self.meta_doc_id,
            document={"last_indexed_patent_id": last_id}
        )


    async def bulk_index(self, documents):
        operations = []

        for d in documents:
            operations.append({
                "index": {
                    "_index": self.index_name,
                    "_id": d["patent_id"]
                }
            })
            operations.append(d)

        await self.client.bulk(operations=operations)