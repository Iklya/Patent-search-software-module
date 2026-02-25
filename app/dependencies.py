from functools import lru_cache
from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionService


@lru_cache
def get_keyword_extraction_service() -> KeywordExtractionService:
    return KeywordExtractionService()
