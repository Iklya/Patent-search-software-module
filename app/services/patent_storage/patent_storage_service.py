from datetime import datetime

from app.models.patents import Patent
from app.models.concepts import Concept
from app.services.patent_storage.hdfs_service import HDFSService
from app.services.patent_storage.postgresql_service import PostgreSQLService
from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentStorageService:
    def __init__(self, session):
        self.session = session
        self.hdfs = HDFSService()
        self.pg = PostgreSQLService(session)


    async def store_patents(self, patents: list[dict]):
        stored_patents_counter = 0
        for p in patents:
            pub_number = p.get("publication_number")

            if not pub_number:
                continue

            abstract_path, description_path, claims_path = self.hdfs.store_fulltext(p)

            inventors = []

            for name in p.get("inventors", []):
                inventor = await self.pg.get_or_create_inventor(name)
                inventors.append(inventor)

            classifications = []

            for code in p.get("classifications", []):
                classification = await self.pg.get_or_create_classification(code)
                classifications.append(classification)

            citations = []

            for number in p.get("citations", []):
                citation = await self.pg.get_or_create_citation(number)
                citations.append(citation)

            concepts = []

            for concept_name in p.get("concepts", []):
                concept = Concept(name=concept_name)
                concepts.append(concept)

            patent = Patent(
                publication_number = pub_number,
                application_number = p.get("application_number"),
                title = p.get("title"),
                country_code = p.get("country_code"),
                kind_code = p.get("kind_code"),
                filing_date = self.parse_date(p.get("filing_date")),
                publication_date = self.parse_date(p.get("publication_date")),
                abstract_hdfs_path = abstract_path,
                description_hdfs_path = description_path,
                claims_hdfs_path = claims_path,
                source_url = p.get("source_url"),
                inventors = inventors,
                classifications = classifications,
                citations = citations,
                concepts = concepts
            )

            self.session.add(patent)
            stored_patents_counter += 1

        await self.session.commit()

        logger.info(f"Сохранено патентов: {stored_patents_counter}")


    def parse_date(self, value):
        if not value:
            return None
        
        return datetime.strptime(value, "%Y-%m-%d").date()