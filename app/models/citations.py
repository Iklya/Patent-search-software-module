from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Citation(Base):
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    publication_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    patents: Mapped[list["Patent"]] = relationship(
        secondary="patent_citations",
        back_populates="citations"
    )