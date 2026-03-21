from sqlalchemy import select
from sqlalchemy.orm import selectinload
import re

from app.models.patents import Patent
from app.services.patent_storage.hdfs_service import HDFSService
from app.core.logger import get_logger


logger = get_logger(__name__)


class PatentResultBuilder:
    """
    Используется для сборки результатов поиска: на основе полученных индексов патентов
    подгружает полную информацию о патентном документе из PostgreSQL и HDFS, подсвечивая
    вхождения найденных ключевых фраз в полнотекстовых данных
    """
    def __init__(self, session):
        self.session = session
        self.hdfs = HDFSService()


    async def build_results(self, search_results: list[dict]) -> list[dict]:
        if not search_results:
            return []

        patent_ids = [r["patent_id"] for r in search_results]

        patents = await self.find_patents_from_database(patent_ids)

        final_results = []

        for r in search_results:
            patent = patents.get(r["patent_id"])
            if not patent:
                continue

            highlight = r.get("highlight", {})

            title, abstract, claims, description = \
                                self.apply_highlight_for_text_fields(patent, highlight)

            final_results.append({
                "patent_id": patent.id,
                "score": r["score"],
                "publication_number": patent.publication_number,
                "application_number": patent.application_number,
                "title": title,
                "country_code": patent.country_code,
                "kind_code": patent.kind_code,
                "filing_date": str(patent.filing_date) if patent.filing_date else None,
                "publication_date": str(patent.publication_date) if patent.publication_date else None,
                "inventors": [i.full_name for i in patent.inventors],
                "classifications": [c.code for c in patent.classifications],
                "citations": [c.publication_number for c in patent.citations],
                "abstract": abstract,
                "claims": claims,
                "description": description,
                "concepts": [c.name for c in patent.concepts],
                "source_url": patent.source_url,
                "parsed_at": patent.parsed_at.isoformat() if patent.parsed_at else None
            })

        logger.debug("Результаты сборки для патентов: %s", patent_ids)

        return final_results
    

    async def find_patents_from_database(self, patent_ids):
        result = await self.session.execute(
            select(Patent)
            .where(Patent.id.in_(patent_ids))
            .options(
                selectinload(Patent.inventors),
                selectinload(Patent.classifications),
                selectinload(Patent.citations),
                selectinload(Patent.concepts)
            )
        )

        return {p.id: p for p in result.scalars().all()}

    
    def apply_highlight_for_text_fields(self, patent, highlight):
        title = self.apply_highlight(
                patent.title,
                highlight.get("title")
            )
            
        abstract = self.apply_highlight(
            self.hdfs.read_file(patent.abstract_hdfs_path),
            highlight.get("abstract")
        )

        claims = self.apply_highlight(
            self.hdfs.read_file(patent.claims_hdfs_path),
            highlight.get("claims")
        )

        description = self.apply_highlight(
            self.hdfs.read_file(patent.description_hdfs_path),
            highlight.get("description")
        )

        return title, abstract, claims, description
    

    def apply_highlight(self, original_text: str, highlight_fragments: list[str] | None):
        if not original_text:
            return ""

        if not highlight_fragments:
            return original_text

        words = set()

        for fragment in highlight_fragments:
            matches = re.findall(r"<mark>(.*?)</mark>", fragment)
            for m in matches:
                words.add(m)

        highlighted_text = original_text

        for word in sorted(words, key=len, reverse=True):
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            highlighted_text = pattern.sub(
                lambda m: f"<mark>{m.group(0)}</mark>",
                highlighted_text
            )

        return highlighted_text
