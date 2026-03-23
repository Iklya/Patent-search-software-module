from functools import lru_cache

from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionService
from app.services.patent_collection.patent_parser_service import PatentParserService
from app.services.patent_search.patent_search_service import PatentSearchService


@lru_cache
def get_keyword_extraction_service() -> KeywordExtractionService:
    return KeywordExtractionService()


def get_patent_parser_service() -> PatentParserService:
    return PatentParserService()


def get_patent_search_service() -> PatentSearchService:
    return PatentSearchService()
