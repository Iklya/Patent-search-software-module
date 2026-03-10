import re
from urllib.parse import quote
from datetime import datetime, timedelta

from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentCollectionService:
    """
    Используется для сбора URL патентов из Google Patents
    на основе пользовательского запроса с учётом диапазона дат публикаций
    """
    def __init__(self, page):
        self.page = page
        self.base_url = "https://patents.google.com"
        self.max_pages = 10


    def collect_patent_links(
        self,
        query: str,
        limit: int,
        existing_publications: set,
        date_from: str,
        date_to: str
    ):
        collection_results = []
        seen_publications = set(existing_publications)

        start_date = datetime.fromisoformat(date_from)
        end_date = datetime.fromisoformat(date_to)
        current_date = start_date

        search_query = self.set_query(query)

        while current_date <= end_date and len(collection_results) < limit:
            strftime_date = current_date.strftime("%Y%m%d")
            logger.info(f"Поиск патентов, опубликованных {current_date.date()}.")

            self.search_patents_by_date(
                collection_results,
                seen_publications,
                search_query,
                strftime_date,
                limit
            )
            current_date += timedelta(days=1)

        logger.info(f"Собрано {len(collection_results)} новых патентов")

        return collection_results
    
    
    def set_query(self, query):
        return quote(query) if query else ""
    

    def search_patents_by_date(
        self,
        results,
        seen,
        query,
        strftime_date,
        limit
    ):
        page_index = 0
        while len(results) < limit:
            search_url = self.set_search_url(query, strftime_date, page_index)
            logger.debug(f"URL для поиска: {search_url}")

            try:
                self.load_patents_page(search_url)
                logger.info("Страница с патентами загружена")
            except:
                logger.warning("Страница с патентами не загрузилась")
                break

            links = self.find_patent_links()
            logger.info(f"Найдено ссылок на патенты: {len(links)}")

            if not links:
                break

            if self.add_patents_to_collection(links, seen, results, limit):
                break

            page_index += 1

            if page_index == self.max_pages:
                logger.warning("Достигнут лимит по просматриваемым страницам")
                break


    def set_search_url(
        self,
        query,
        strftime_date,
        page_index
    ):
        url = (
            f"{self.base_url}/"
            f"?after=publication:{strftime_date}"
            f"&before=publication:{strftime_date}"
            f"&language=RUSSIAN"
            f"&num=100"
            f"&page={page_index}"
        )

        if query:
            url += f"&q={query}"

        return url
    
    
    def load_patents_page(self, search_url):
        self.page.goto(search_url, timeout=10000)
        self.page.wait_for_selector("search-result-item", timeout=1000)
        self.page.wait_for_timeout(2000)


    def find_patent_links(self):
        paths = self.page.eval_on_selector_all(
            "search-result-item state-modifier.result-title",
            "els => els.map(e => e.getAttribute('data-result'))"
        )

        return [f"{self.base_url}/{p}" for p in paths if p]
    

    def add_patents_to_collection(
        self,
        links,
        seen,
        results,
        limit
    ):
        for link in links:
            pub_num = self.extract_publication_number(link)

            if not pub_num or pub_num in seen:
                continue

            logger.debug(f"Добавлен патент: {pub_num}")

            results.append(link)
            seen.add(pub_num)

            if len(results) >= limit:
                return True
        
        return False

    
    def extract_publication_number(self, link):
        m = re.search(r'/patent/([A-Z]*\d+[A-Z0-9]*)', link)

        return m.group(1) if m else None
