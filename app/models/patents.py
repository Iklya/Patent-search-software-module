from sqlalchemy import Integer, String, Text, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from app.core.database import Base


class Patent(Base):
    __tablename__ = "patents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    publication_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    application_number: Mapped[str | None] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    kind_code: Mapped[str] = mapped_column(String(2), nullable=False)
    filing_date: Mapped[datetime | None] = mapped_column(Date)
    publication_date: Mapped[datetime | None] = mapped_column(Date)
    abstract_hdfs_path: Mapped[str | None] = mapped_column(Text)
    description_hdfs_path: Mapped[str | None] = mapped_column(Text)
    claims_hdfs_path: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    concepts: Mapped[list["Concept"]] = relationship(
        back_populates="patent",
        cascade="all, delete-orphan"
    )

    inventors: Mapped[list["Inventor"]] = relationship(
        secondary="patent_inventors",
        back_populates="patents"
    )

    classifications: Mapped[list["Classification"]] = relationship(
        secondary="patent_classifications",
        back_populates="patents"
    )

    citations: Mapped[list["Citation"]] = relationship(
        secondary="patent_citations",
        back_populates="patents"
    )