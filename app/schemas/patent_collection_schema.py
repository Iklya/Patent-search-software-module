from pydantic import BaseModel, Field
from datetime import date

class PatentsLoadCreate(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле запроса на сбор патентов
    """
    query: str = Field(
        default="",
        max_length=1000,
        description="Текст запроса для поиска патентов в Google Patents"
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=1000000,
        description="Максимальное число загружаемых патентов"
    )
    date_from: date = Field(default="2004-10-02", description="Начальная дата публикации")
    date_to: date = Field(default="2025-10-02", description="Конечная дата публикации")
