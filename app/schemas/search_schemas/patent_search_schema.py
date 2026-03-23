from pydantic import BaseModel, Field
from datetime import date

from app.schemas.search_schemas.search_enums import SearchMode, SortOrder


class PatentSearchCreate(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле запроса на извлечение ключевых фраз
    """
    keywords: list[str] = Field(None, description="Список ключевых фраз")
    mode: str = Field(default=SearchMode.AND, description="Логический режим поиска")
    publication_number: str = Field(None, description="Основной номер патента")
    application_number: str = Field(None, description="Номер заявки")
    country_code: str = Field(None, description="Код страны")
    kind_code: str = Field(None, description="Тип публикации")
    title: str = Field(None, description="Наименование патента")
    abstract: str = Field(None, description="Тест реферата патента")
    description: str = Field(None, description="Текст описания патента")
    claims: str = Field(None, description="Текст формулы изобретения патента")
    inventors: list[str] = Field(None, description="Список авторов изобретения")
    classifications: list[str] = Field(None, description="Список кодов патентных классификаций")
    filing_date_from: date = Field(None, description="Минимальная дата подачи заявки")
    filing_date_to: date = Field(None, description="Максимальная дата подачи заявки")
    publication_date_from: date = Field(None, description="Минимальная дата публикации")
    publication_date_to: date = Field(None, description="Максимальная дата публикации")
    sort_field: str = Field(None, description="Поле, по которому будет проведена сортировка")
    sort_order: str = Field(default=SortOrder.desc,description="Режим сортировки")
    size: int = Field(
        default=50,
        ge=1,
        le=10000,
        description="Максимальное количество найденных патентов"
    )


class PatentSearch(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле ответа в результате извлечения ключевых фраз
    """
    total: int
    search_result: list[dict]
