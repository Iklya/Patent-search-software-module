class HighlightService:
    """
    Используется для обработки результатов Elasticsearch: выполняет подсветку
    совпавших ключевых фраз в тексте и их извлечение из ответа Elasticsearch.
    """
    def add_highlight(self, query: dict) -> None:
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
        hits = response["hits"]["hits"]
        results = []

        for hit in hits:
            result = {
                "patent_id": int(hit["_source"]["patent_id"]),
                "score": hit.get("_score", 0),
                "highlight": hit.get("highlight", {})
            }

            results.append(result)

        return results