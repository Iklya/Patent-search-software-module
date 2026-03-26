from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Classification(Base):
    """
    Используется для задания SQLAlchemy-модели для таблицы Classification
    """
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    patents: Mapped[list["Patent"]] = relationship(
        secondary="patent_classifications",
        back_populates="classifications"
    )