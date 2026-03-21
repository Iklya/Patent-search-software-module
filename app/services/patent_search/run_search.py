import asyncio
import json

from app.services.patent_search.patent_search_service import PatentSearchService


async def main():
    search_service = PatentSearchService()

    results = await search_service.search(
        keywords=["газон"],
        size=5,
        kind_code="A"
    )

    for r in results:
        print(json.dumps(r, ensure_ascii=False, indent=4))
        print("\n\n")


asyncio.run(main())