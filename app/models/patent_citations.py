from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PatentCitation(Base):
    __tablename__ = "patent_citations"

    patent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patents.id"),
        primary_key=True
    )
    citation_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("citations.id"),
        primary_key=True
    )