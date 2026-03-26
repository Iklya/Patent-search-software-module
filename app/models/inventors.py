from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Inventor(Base):
    """
    Используется для задания SQLAlchemy-модели для таблицы Inventor
    """
    __tablename__ = "inventors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    patents: Mapped[list["Patent"]] = relationship(
        secondary="patent_inventors",
        back_populates="inventors"
    )