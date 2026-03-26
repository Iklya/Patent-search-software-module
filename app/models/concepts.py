from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Concept(Base):
    """
    Используется для задания SQLAlchemy-модели для таблицы Concept
    """
    __tablename__ = "concepts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    patent_id: Mapped[int] = mapped_column(Integer, ForeignKey("patents.id"))

    patent: Mapped["Patent"] = relationship(
        back_populates="concepts"
    )