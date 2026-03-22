from elasticsearch import NotFoundError

from app.services.patent_indexing.elasticsearch_service import ElasticsearchService
from app.services.patent_search.highlight_service import HighlightService
from app.services.patent_search.patent_result_builder import PatentResultBuilder
from app.core.database import async_session_maker
from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentSearchService:
    """
    Используется для выполнения полнотекстового поиска с помощью Elasticsearch:
    выполняет запрос, обрабатывает результаты и строит финальный JSON-ответ.
    """
    def __init__(self):
        self.es = ElasticsearchService()
        self.highlight = HighlightService()


    async def search(
        self,
        keywords: list[str] | None = None,
        mode: str = "AND",
        publication_number: str | None = None,
        application_number: str | None = None,
        country_code: str | None = None,
        kind_code: str | None = None,
        title: str | None = None,
        abstract: str | None = None,
        description: str | None = None,
        claims: str | None = None,
        inventors: list[str] | None = None,
        classifications: list[str] | None = None,
        filing_date_from: str | None = None,
        filing_date_to: str | None = None,
        publication_date_from: str | None = None,
        publication_date_to: str | None = None,
        sort_field: str | None = None,
        sort_order: str = "desc",
        size: int = 50
    ):
        try:
            logger.info("Начат процесс поиска патентов на основе поискового запроса.")

            if not await self.es.index_exists():
                logger.error("Индекс Elasticsearch не существует.")
                raise RuntimeError(
                    "Индекс Elasticsearch не существует. Сначала выполните индексирование."
                )

            must = []
            filter_query = []

            self.add_keywords_for_search(must, keywords, mode)

            self.add_text_fields_for_search(must, title, abstract, description, claims)

            self.add_fields_for_exact_match_search(filter_query, publication_number,
                                                    application_number, country_code, kind_code)

            if inventors:
                must.append({"match": {"inventors": " ".join(inventors)}})

            if classifications:
                filter_query.append(
                    {"terms": {"classifications": classifications}}
                )

            self.add_date_fields_for_search(filter_query, filing_date_from,
                                            filing_date_to, publication_date_from, publication_date_to)

            query = {
                "size": size,
                "query": {
                    "bool": {
                        "must": must,
                        "filter": filter_query
                    }
                }
            }

            self.add_sort_field_for_search(query, sort_field, sort_order)

            self.highlight.add_highlight(query)

            logger.debug("Отправка поискового запроса в Elasticsearch.")

            response = await self.es.client.search(
                index=self.es.index_name,
                body=query
            )

            search_results = self.highlight.extract_highlight_results(response)

            final_results = await self.build_final_json(search_results)

            logger.info(f"Поиск завершен. Найдено результатов: {len(final_results)}")

            return final_results

        finally:
            logger.info("Закрытие соединения Elasticsearch.")

            await self.es.close()

    
    def add_keywords_for_search(self, must, keywords, mode):
        logger.debug("Добавление keywords в запрос поиска.")

        if not keywords:
            logger.warning("Ключевые слова поиска отсутствуют.")
            return

        operator = "and" if mode == "AND" else "or"

        must.append({
            "combined_fields": {
                "query": " ".join(keywords),
                "fields": [
                    "title",
                    "abstract",
                    "description",
                    "claims"
                ],
                "operator": operator
            }
        })

    
    def add_text_fields_for_search(self, must, title, abstract, description, claims):
        logger.debug("Добавление текстовых полей в запрос.")

        if title:
            must.append({"match": {"title": title}})

        if abstract:
            must.append({"match": {"abstract": abstract}})

        if description:
            must.append({"match": {"description": description}})

        if claims:
            must.append({"match": {"claims": claims}})


    def add_fields_for_exact_match_search(self, filter_query, publication_number,
                                            application_number, country_code, kind_code):
        logger.debug("Добавление фильтров точного совпадения.")

        if publication_number:
            filter_query.append(
                {"term": {"publication_number": publication_number}}
            )

        if application_number:
            filter_query.append(
                {"term": {"application_number": application_number}}
            )

        if country_code:
            filter_query.append(
                {"term": {"country_code": country_code}}
            )

        if kind_code:
            filter_query.append(
                {"term": {"kind_code": kind_code}}
            )

    
    def add_date_fields_for_search(self, filter_query, filing_date_from,
                                   filing_date_to, publication_date_from, publication_date_to):
        logger.debug("Добавление фильтров по датам.")

        if filing_date_from or filing_date_to:
            range_query = {}

            if filing_date_from:
                range_query["gte"] = filing_date_from

            if filing_date_to:
                range_query["lte"] = filing_date_to

            filter_query.append({"range": {"filing_date": range_query}})

        if publication_date_from or publication_date_to:
            range_query = {}

            if publication_date_from:
                range_query["gte"] = publication_date_from

            if publication_date_to:
                range_query["lte"] = publication_date_to

            filter_query.append(
                {"range": {"publication_date": range_query}}
            )


    def add_sort_field_for_search(self, query, sort_field, sort_order):
        logger.debug("Добавление сортировки в запрос.")

        if not sort_field:
            logger.warning("Поле сортировки не указано.")
            return

        query["sort"] = [
            {
                sort_field: {
                    "order": sort_order
                }
            }
        ]
    

    async def build_final_json(self, search_results):
        logger.debug("Формирование финального JSON ответа.")

        async with async_session_maker() as session:
            builder = PatentResultBuilder(session)

            return await builder.build_results(search_results)
