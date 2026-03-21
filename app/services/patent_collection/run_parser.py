import json
import asyncio

from app.services.patent_collection.patent_parser_service import PatentParserService
from app.core.database import async_session_maker


async def main():
    parser = PatentParserService()

    async with async_session_maker() as session:
        await parser.parse(
            session=session,
            query="",
            limit=1,
            date_from="2015-01-22",
            date_to="2025-10-02"
        )


asyncio.run(main())