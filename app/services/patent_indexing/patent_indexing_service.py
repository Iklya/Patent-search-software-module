from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.patents import Patent
from app.services.patent_storage.hdfs_service import HDFSService
from app.services.patent_indexing.elasticsearch_service import ElasticsearchService
from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentIndexingService:
    """
    Используется для выполнения процесса индексирования патентов в Elasticsearch.
    """
    def __init__(self, session):
        self.session = session
        self.hdfs = HDFSService()
        self.es = ElasticsearchService()
        self.documents_limit = 500


    async def index_all_patents(self):
        try:
            logger.info("Начато индексирование патентов.")

            await self.es.create_index_if_not_exists()
            await self.es.create_meta_index_if_not_exists()

            last_indexed_id = await self.es.get_last_indexed_id()
            logger.info(f"Последний проиндексированный patent_id: {last_indexed_id}")

            patents = await self.find_not_indexed_patents(last_indexed_id)

            if not patents:
                logger.info("Новых патентов для индексирования нет.")
                return

            documents = []
            max_id = last_indexed_id

            for i, patent in enumerate(patents, start=1):
                document = self.build_document(patent)
                
                documents.append(document)
                max_id = patent.id

                if len(documents) == self.documents_limit:
                    await self.es.bulk_index(documents)
                    documents = []
                    logger.info(f"Проиндексировано новых патентов: {i}")

            if documents:
                await self.es.bulk_index(documents)

            await self.es.update_last_indexed_id(max_id)

            logger.info(f"Индексирование завершено. Новый last_indexed_id={max_id}")

        finally:
            await self.es.close()


    async def find_not_indexed_patents(self, last_indexed_id):
        result = await self.session.execute(
            select(Patent)
            .where(Patent.id > last_indexed_id)
            .order_by(Patent.id)
            .options(
                selectinload(Patent.inventors),
                selectinload(Patent.classifications)
            )
        )
        
        return result.scalars().all()


    def build_document(self, patent):
        abstract = self.hdfs.read_file(patent.abstract_hdfs_path)
        description = self.hdfs.read_file(patent.description_hdfs_path)
        claims = self.hdfs.read_file(patent.claims_hdfs_path)

        return {
            "patent_id": patent.id,
            "publication_number": patent.publication_number,
            "application_number": patent.application_number,
            "country_code": patent.country_code,
            "kind_code": patent.kind_code,
            "title": patent.title,
            "filing_date": patent.filing_date,
            "publication_date": patent.publication_date,
            "abstract": abstract,
            "description": description,
            "claims": claims,
            "inventors": [i.full_name for i in patent.inventors],
            "classifications": [c.code for c in patent.classifications]
        }
