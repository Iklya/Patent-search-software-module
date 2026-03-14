from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PatentInventor(Base):
    __tablename__ = "patent_inventors"

    patent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patents.id"),
        primary_key=True
    )
    inventor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("inventors.id"),
        primary_key=True
    )