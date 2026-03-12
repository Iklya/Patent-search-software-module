from app.services.patent_collection.patent_parser_service import PatentParserService
import json

parser = PatentParserService()
data = parser.parse(
    query="",
    limit=2,
    date_from="2014-10-30",
    date_to="2025-10-02"
    )

for patent in data:
    print(json.dumps(patent, ensure_ascii=False, indent=4))
    print("\n\n")