import asyncio

from app.services.patent_indexing.elasticsearch_service import ElasticsearchService


async def main():
    es = ElasticsearchService()

    await es.delete_index()
    await es.client.close()

    print("Индекс Elasticsearch был удален.")


if __name__ == "__main__":
    asyncio.run(main())
