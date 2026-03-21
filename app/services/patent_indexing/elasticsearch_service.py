from elasticsearch import AsyncElasticsearch, NotFoundError

from app.services.patent_indexing.index_mapping import INDEX_MAPPING
from app.core.logger import get_logger


logger = get_logger(__name__)


class ElasticsearchService:
    """
    Используется для управления индексами патентов в Elasticsearch, 
    хранения метаданных индексирования, bulk-индексации документов и
    выполнения низкоуровневых операций Elasticsearch.
    """
    def __init__(self):
        self.client = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
        self.index_name = "patents"
        self.meta_index = "index_meta"
        self.meta_doc_id = "patent_index_state"
    
    
    async def create_index_if_not_exists(self):
        exists = await self.client.indices.exists(index=self.index_name)

        if not exists:
            logger.info("Создание индекса Elasticsearch: %s", self.index_name)

            await self.client.indices.create(
            index=self.index_name,
            body=INDEX_MAPPING
        )
        else:
            logger.info("Индекс %s уже существует", self.index_name)
    

    async def index_exists(self):
        return await self.client.indices.exists(index=self.index_name)
    

    async def create_meta_index_if_not_exists(self):
        exists = await self.client.indices.exists(index=self.meta_index)

        if not exists:
            logger.info("Создание meta индекса: %s", self.meta_index)
            await self.client.indices.create(index=self.meta_index)


    async def get_last_indexed_id(self):
        try:
            result = await self.client.get(
                index=self.meta_index,
                id=self.meta_doc_id
            )
            return result["_source"]["last_indexed_patent_id"]
        
        except NotFoundError:
            logger.info("Meta документ не найден. Индексирование начнется с начала.")
            return 0


    async def update_last_indexed_id(self, last_id):
        await self.client.index(
            index=self.meta_index,
            id=self.meta_doc_id,
            document={"last_indexed_patent_id": last_id}
        )


    async def delete_index(self):
        logger.warning("Удаление индексов Elasticsearch")

        if await self.client.indices.exists(index=self.index_name):
            await self.client.indices.delete(index=self.index_name)

        if await self.client.indices.exists(index=self.meta_index):
            await self.client.indices.delete(index=self.meta_index)


    async def bulk_index(self, documents: list[dict]):
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


    async def close(self):
        logger.info("Закрытие клиента Elasticsearch")
        await self.client.close()
