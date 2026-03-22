from sqlalchemy import select

from app.models.inventors import Inventor
from app.models.classifications import Classification
from app.models.citations import Citation
from app.models.patents import Patent
from app.core.logger import get_logger


logger = get_logger(__name__)


class PostgreSQLService:
    """
    Используется для организации хранения метаданных патентов в PostgreSQL.
    """
    def __init__(self, session):
        self.session = session


    async def get_or_create_inventor(self, name: str):
        logger.debug(f"Поиск inventors: {name}")

        inventor_result = await self.session.execute(
            select(Inventor).where(Inventor.full_name == name)
        )
        obj = inventor_result.scalar_one_or_none()

        if obj:
            logger.debug(f"Inventor найден: %s", name)
            return obj

        logger.debug("Создание нового inventor: {name}")

        obj = Inventor(full_name=name)
        self.session.add(obj)

        return obj


    async def get_or_create_classification(self, code: str):
        logger.debug(f"Поиск classifications: {code}")

        classification_result = await self.session.execute(
            select(Classification).where(Classification.code == code)
        )
        obj = classification_result.scalar_one_or_none()

        if obj:
            logger.debug(f"Classification найдена: {code}")
            return obj

        logger.debug(f"Создание новой classification: {code}")

        obj = Classification(code=code)
        self.session.add(obj)

        return obj


    async def get_or_create_citation(self, publication_number: str):
        logger.debug(f"Поиск citations: {publication_number}")

        citation_result = await self.session.execute(
            select(Citation).where(Citation.publication_number == publication_number)
        )
        obj = citation_result.scalar_one_or_none()

        if obj:
            logger.debug(f"Сitation найдена: {publication_number}")
            return obj

        logger.debug(f"Создание новой citation: {publication_number}")

        obj = Citation(publication_number=publication_number)
        self.session.add(obj)

        return obj
