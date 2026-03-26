import re
from datetime import datetime, timedelta

from urllib.parse import quote

from app.core.logger import get_logger
from app.core.settings import settings


logger = get_logger(__name__)


class PatentCollectionService:
    """
    Используется для сбора URL патентов из Google Patents
    на основе пользовательского запроса с учётом диапазона дат публикаций
    """
    def __init__(self, page):
        self.page = page
        self.base_url = settings.google_patents_base_url
        self.max_pages = settings.google_patents_max_pages


    async def collect_patent_links(
        self,
        query: str,
        limit: int,
        date_from: str,
        date_to: str
    ):
        logger.info(f"Начат сбор патентов. Query='{query}', limit={limit}, date_from={date_from}, date_to={date_to}")
        
        collection_results = []

        start_date = datetime.fromisoformat(date_from)
        end_date = datetime.fromisoformat(date_to)
        current_date = start_date

        search_query = self.set_query(query)

        while current_date <= end_date and len(collection_results) < limit:
            strftime_date = current_date.strftime("%Y%m%d")
            logger.info(f"Поиск патентов, опубликованных {current_date.date()}.")

            await self.search_patents_by_date(
                collection_results,
                search_query,
                strftime_date,
                limit
            )

            current_date += timedelta(days=1)

        logger.info(f"Сбор ссылок завершен. Найдено {len(collection_results)} патентов")

        return collection_results
    
    
    def set_query(self, query):
        return quote(query) if query else ""
    

    async def search_patents_by_date(
        self,
        results,
        query,
        strftime_date,
        limit
    ):
        logger.debug(f"Начат поиск патентов на дату {datetime.strptime(strftime_date, '%Y%m%d')}")

        page_index = 0
        while len(results) < limit:
            search_url = self.set_search_url(query, strftime_date, page_index)
            logger.debug(f"URL для поиска: {search_url}")

            try:
                await self.load_patents_page(search_url)
                logger.info("Страница с патентами загружена")

            except Exception as e:
                logger.exception("Страница с патентами не загрузилась")
                break

            links = await self.find_patent_links()
            if not links:
                break

            logger.info(f"На текущей странице найдено {len(links)} ссылок на патенты.")

            if self.add_patents_to_collection(links, results, limit):
                break

            page_index += 1

            if page_index >= self.max_pages:
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
            f"&num={settings.google_patents_results_per_page}"
            f"&page={page_index}"
        )

        if query:
            url += f"&q={query}"

        return url
    
    
    async def load_patents_page(self, search_url):
        logger.debug(f"Загрузка страницы поиска: {search_url}")
        
        await self.page.goto(
            search_url,
            timeout=settings.playwright_page_load_timeout
        )
        await self.page.wait_for_selector(
            "search-result-item",
            timeout=settings.playwright_selector_timeout
        )
        await self.page.wait_for_timeout(settings.playwright_scroll_wait)


    async def find_patent_links(self):
        paths = await self.page.eval_on_selector_all(
            "search-result-item state-modifier.result-title",
            "els => els.map(e => e.getAttribute('data-result'))"
        )

        logger.debug(f"Извлечено ссылок со страницы: {len(paths)}")

        return [f"{self.base_url}/{p}" for p in paths if p]
    

    def add_patents_to_collection(
        self,
        links,
        results,
        limit
    ):
        for link in links:
            pub_num = self.extract_publication_number(link)

            if not pub_num:
                continue

            logger.debug(f"Добавлен патент: {pub_num}")

            results.append(link)

            if len(results) >= limit:
                return True
        
        return False

    
    def extract_publication_number(self, link):
        m = re.search(r'/patent/([A-Z]*\d+[A-Z0-9]*)', link)

        return m.group(1) if m else None
