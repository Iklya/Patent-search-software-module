from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PatentClassification(Base):
    __tablename__ = "patent_classifications"

    patent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patents.id"),
        primary_key=True
    )
    classification_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("classifications.id"),
        primary_key=True
    )