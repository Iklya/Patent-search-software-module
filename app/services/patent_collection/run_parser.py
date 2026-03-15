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
            limit=100,
            date_from="2014-10-30",
            date_to="2025-10-02"
        )

        # for patent in data:
        #     print(json.dumps(patent, ensure_ascii=False, indent=4))
        #     print("\n\n")


asyncio.run(main())