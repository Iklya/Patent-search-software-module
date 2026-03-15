from playwright.async_api import async_playwright

from app.services.patent_collection.patent_collection_service import PatentCollectionService
from app.services.patent_collection.patent_preparation_service import ParserPreparationService
from app.services.patent_storage.patent_storage_service import PatentStorageService
from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentParserService:
    """
    Используется для управления процессом сбора одного и более патентов
    (запуск браузера, получение ссылок на патенты и автоматизированный сбор каждого из них)
    """
    async def parse(
        self,
        session,
        query: str,
        limit: int = 5,
        date_from: str = "2004-10-02",
        date_to: str = "2025-10-02",
    ):
        logger.info(f"Начат сбор патентов. Query='{query}', limit={limit}, date_from={date_from}, date_to={date_to}")
        
        results = []
        storage_service = PatentStorageService(session)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)

            page = await browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )

            self.collection_service = PatentCollectionService(page)
            self.preparation_service = ParserPreparationService()

            links = await self.collection_service.collect_patent_links(
                query=query,
                limit=limit,
                date_from=date_from,
                date_to=date_to
            )

            for i, link in enumerate(links, start=1):
                ru_html = await self.fetch_page_html(page, link)

                patent_json = self.preparation_service.prepare_patent_json(
                    ru_html,
                    link
                )
                results.append(patent_json)

                if i % 50 == 0:
                    logger.info(f"Собрано 50 патентов.")

            await browser.close()

        logger.info("Браузер закрыт")

        await storage_service.store_patents(results)
        
        logger.info(f"Сохранено патентов: {len(results)}")

        return results
    

    async def fetch_page_html(self, page, url: str) -> str:
        logger.debug(f"Загрузка страницы патента: {url}")

        await page.goto(url, timeout=90000, wait_until="domcontentloaded")

        last_height = 0

        for _ in range(10):
            height = await page.evaluate("document.body.scrollHeight")

            if height == last_height:
                break

            last_height = height
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1200)

        logger.debug("Страница полностью прокручена")

        return await page.content()
