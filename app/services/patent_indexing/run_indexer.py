import asyncio

from app.services.patent_indexing.patent_indexing_service import PatentIndexingService
from app.core.database import async_session_maker


async def main():
    async with async_session_maker() as session:
        indexer = PatentIndexingService(session)

        await indexer.index_all_patents()


if __name__ == "__main__":
    asyncio.run(main())
