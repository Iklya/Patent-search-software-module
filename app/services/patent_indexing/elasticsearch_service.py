from elasticsearch import AsyncElasticsearch, NotFoundError

from app.services.patent_indexing.index_mapping import INDEX_MAPPING
from app.core.logger import get_logger
from app.core.settings import settings

logger = get_logger(__name__)


class ElasticsearchService:
    """
    Используется для управления индексами патентов в Elasticsearch, 
    хранения метаданных индексирования, bulk-индексации документов и
    выполнения низкоуровневых операций Elasticsearch.
    """
    def __init__(self):
        self.client = AsyncElasticsearch(hosts=[settings.elasticsearch_url])
        self.index_name = "patents"
        self.meta_index = "index_meta"
        self.meta_doc_id = "patent_index_state"
    

    async def create_index_if_not_exists(self):
        logger.debug(f"Проверка существования индекса {self.index_name}")

        exists = await self.client.indices.exists(index=self.index_name)

        if not exists:
            logger.info(f"Создание индекса Elasticsearch: {self.index_name}")

            await self.client.indices.create(
            index=self.index_name,
            body=INDEX_MAPPING
        )
        else:
            logger.info(f"Индекс {self.index_name} уже существует.")
    

    async def index_exists(self):
        logger.debug("Проверка существования полнотекстового индекса.")

        return await self.client.indices.exists(index=self.index_name)
    

    async def create_meta_index_if_not_exists(self):
        logger.debug("Проверка существования meta индекса.")

        exists = await self.client.indices.exists(index=self.meta_index)

        if not exists:
            logger.info(f"Создание meta индекса: {self.meta_index}")
            await self.client.indices.create(index=self.meta_index)


    async def get_last_indexed_id(self):
        logger.debug("Получение last_indexed_patent_id.")

        try:
            result = await self.client.get(
                index=self.meta_index,
                id=self.meta_doc_id
            )
            last_id = result["_source"]["last_indexed_patent_id"]
        
            logger.debug(f"Последний индексированный id={last_id}")

            return last_id

        except NotFoundError:
            logger.exception("Meta документ не найден. Индексирование начнется с начала.")
            return 0


    async def update_last_indexed_id(self, last_id):
        logger.debug(f"Обновление last_indexed_id={last_id}")

        await self.client.index(
            index=self.meta_index,
            id=self.meta_doc_id,
            document={"last_indexed_patent_id": last_id}
        )


    async def delete_index(self):
        logger.warning("Удаление индексов Elasticsearch")

        if await self.client.indices.exists(index=self.index_name):
            logger.debug(f"Удаление индекса {self.index_name}")
            await self.client.indices.delete(index=self.index_name)

        if await self.client.indices.exists(index=self.meta_index):
            logger.debug(f"Удаление meta индекса {self.meta_index}")
            await self.client.indices.delete(index=self.meta_index)


    async def bulk_index(self, documents: list[dict]):
        logger.debug(f"Bulk индексирование документов: {len(documents)}")

        operations = []

        for d in documents:
            operations.append({
                "index": {
                    "_index": self.index_name,
                    "_id": d["patent_id"]
                }
            })
            operations.append(d)
        
        try:
            await self.client.bulk(operations=operations)
        
        except Exception:
            logger.exception(f"Ошибка bulk index.")
            raise


    async def close(self):
        logger.info("Закрытие клиента Elasticsearch")

        await self.client.close()
