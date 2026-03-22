from app.core.logger import get_logger


logger = get_logger(__name__)


class HighlightService:
    """
    Используется для обработки результатов Elasticsearch: выполняет подсветку
    совпавших ключевых фраз в тексте и их извлечение из ответа Elasticsearch.
    """
    def add_highlight(self, query: dict) -> None:
        logger.debug("Добавление highlight параметров в Elasticsearch query.")

        query["highlight"] = {
            "pre_tags": ["<mark>"],
            "post_tags": ["</mark>"],
            "fields": {
                "title": {},
                "abstract": {},
                "description": {},
                "claims": {}
            }
        }


    def extract_highlight_results(self, response) -> list[dict]:
        logger.debug("Извлечение highlight результатов из ответа Elasticsearch.")

        hits = response["hits"]["hits"]

        if not hits:
            logger.warning("Elasticsearch вернул пустой список результатов")
        
        results = []

        for hit in hits:
            result = {
                "patent_id": int(hit["_source"]["patent_id"]),
                "score": hit.get("_score", 0),
                "highlight": hit.get("highlight", {})
            }

            results.append(result)

        logger.debug(f"Извлечено результатов поиска: {len(results)}")

        return results