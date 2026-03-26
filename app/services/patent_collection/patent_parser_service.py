from playwright.async_api import async_playwright
from sqlalchemy import select

from app.services.patent_collection.patent_collection_service import PatentCollectionService
from app.services.patent_collection.patent_preparation_service import ParserPreparationService
from app.services.patent_storage.patent_storage_service import PatentStorageService
from app.services.patent_indexing.patent_indexing_service import PatentIndexingService
from app.models.patents import Patent
from app.core.logger import get_logger
from app.core.settings import settings


logger = get_logger(__name__)


class PatentParserService:
    """
    Используется для управления процессом сбора одного и более патентов
    (запуск браузера, получение ссылок на патенты и автоматизированный сбор каждого из них)
    """
    def __init__(self):
        self.preparation_service = ParserPreparationService()


    async def parse_patents(
        self,
        session,
        query: str,
        limit: int = 5,
        date_from: str = "2004-10-02",
        date_to: str = "2025-10-02",
    ):        
        results = []

        p, browser, page = await self.create_browser_page()
        
        try:
            self.collection_service = PatentCollectionService(page)

            links = await self.collection_service.collect_patent_links(
                query=query,
                limit=limit,
                date_from=date_from,
                date_to=date_to
            )

            logger.info(f"Получено ссылок на патенты: {len(links)}")

            links = await self.filter_existing_links(session, links)

            for i, link in enumerate(links, start=1):
                logger.debug(f"Парсинг патента {i}: {link}")

                html = await self.fetch_page_html(page, link)

                patent_json = self.preparation_service.prepare_patent_json(
                    html,
                    link
                )
                results.append(patent_json)

                if i % 50 == 0:
                    logger.info(f"Собрано {i} патентов.")

        finally:
            await self.close_browser(p, browser)

            logger.info(f"Парсинг завершен. Обработано патентов: {len(results)}")

        return results
    

    async def parse_single_patent(self, url: str):
        p, browser, page = await self.create_browser_page()

        try:
            html = await self.fetch_page_html(page, url)

            patent_json = self.preparation_service.prepare_patent_json(
                html,
                url
            )

            return patent_json 
        
        finally: 
            await self.close_browser(p, browser)


    async def create_browser_page(self):
        p = await async_playwright().start()

        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        return p, browser, page


    async def close_browser(self, p, browser):
        await browser.close()
        await p.stop()


    async def filter_existing_links(self, session, links: list[str]) -> list[str]:
        if not links:
            return []
        
        result = await session.execute(
            select(Patent.source_url).where(Patent.source_url.in_(links))
        )

        existing = {row[0] for row in result.fetchall()}

        filtered_links = [link for link in links if link not in existing]

        logger.info(
            f"Найдено {len(existing)} уже существующих патентов из {len(links)}. "
            f"На обработку передано {len(filtered_links)} документов."
        )

        return filtered_links


    async def fetch_page_html(self, page, url: str) -> str:
        logger.debug(f"Загрузка страницы патента: {url}")

        await page.goto(url, timeout=90000, wait_until="domcontentloaded")

        last_height = 0

        for _ in range(settings.playwright_scroll_iterations):
            height = await page.evaluate("document.body.scrollHeight")

            if height == last_height:
                break

            last_height = height
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(settings.playwright_scroll_wait_after)

        logger.debug("Страница полностью прокручена.")

        return await page.content()
