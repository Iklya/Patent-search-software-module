from functools import lru_cache

from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionService
from app.services.keyword_extraction.patent_text_builder import PatentTextBuilder
from app.services.keyword_extraction.text_file_reader import TextFileReader
from app.services.patent_collection.patent_parser_service import PatentParserService
from app.services.patent_search.patent_search_service import PatentSearchService


@lru_cache
def get_keyword_extraction_service() -> KeywordExtractionService:
    return KeywordExtractionService()


@lru_cache
def get_text_builder_service() -> PatentTextBuilder:
    return PatentTextBuilder()


@lru_cache
def get_file_reader_service() -> TextFileReader:
    return TextFileReader()


def get_patent_parser_service() -> PatentParserService:
    return PatentParserService()


def get_patent_search_service() -> PatentSearchService:
    return PatentSearchService()
