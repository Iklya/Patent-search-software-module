from playwright.sync_api import sync_playwright

from app.services.patent_collection.patent_collection_service import PatentCollectionService
from app.services.patent_collection.patent_preparation_service import ParserPreparationService
from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentParserService:
    """
    Используется для управления процессом сбора одного и более патентов
    (запуск браузера, получение ссылок на патенты и автоматизированный сбор каждого из них)
    """
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
        )

        self.collection_service = PatentCollectionService(self.page)
        self.preparation_service = ParserPreparationService()


    def parse(
        self,
        query: str,
        limit: int = 5,
        date_from: str = "2004-10-02",
        date_to: str = "2025-10-02",
        existing_publications: set | None = None
    ):
        logger.info(f"Начат сбор патентов. Query='{query}', limit={limit}, date_from={date_from}, date_to={date_to}")
        results = []

        try:
            if existing_publications is None:
                existing_publications = set()

            links = self.collection_service.collect_patent_links(
                query=query,
                limit=limit,
                existing_publications=existing_publications,
                date_from=date_from,
                date_to=date_to
            )

            for link in links:
                ru_html = self.fetch_page_html(link)

                patent_json = self.preparation_service.prepare_patent_json(
                    ru_html,
                    link
                )
                results.append(patent_json)
                
        finally:
            self.browser.close()
            self.playwright.stop()
        logger.info("Браузер закрыт")

        return results
    

    def fetch_page_html(self, url: str) -> str:
        logger.debug(f"Загрузка страницы патента: {url}")

        self.page.goto(url, timeout=90000, wait_until="domcontentloaded")

        last_height = 0

        for _ in range(10):
            height = self.page.evaluate("document.body.scrollHeight")

            if height == last_height:
                break

            last_height = height
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1200)

        logger.debug("Страница полностью прокручена")

        return self.page.content()
