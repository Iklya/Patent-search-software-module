from sqlalchemy import select

from app.models.inventors import Inventor
from app.models.classifications import Classification
from app.models.citations import Citation
from app.models.patents import Patent


class PostgreSQLService:
    def __init__(self, session):
        self.session = session


    async def get_or_create_inventor(self, name: str):
        inventor_result = await self.session.execute(
            select(Inventor).where(Inventor.full_name == name)
        )
        obj = inventor_result.scalar_one_or_none()

        if obj:
            return obj

        obj = Inventor(full_name=name)
        self.session.add(obj)

        return obj


    async def get_or_create_classification(self, code: str):
        classification_result = await self.session.execute(
            select(Classification).where(Classification.code == code)
        )
        obj = classification_result.scalar_one_or_none()

        if obj:
            return obj

        obj = Classification(code=code)
        self.session.add(obj)

        return obj


    async def get_or_create_citation(self, publication_number: str):
        citation_result = await self.session.execute(
            select(Citation).where(Citation.publication_number == publication_number)
        )
        obj = citation_result.scalar_one_or_none()

        if obj:
            return obj

        obj = Citation(publication_number=publication_number)
        self.session.add(obj)

        return obj

