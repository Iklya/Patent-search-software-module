from pydantic import BaseModel, Field, field_validator


class KeywordExtraction(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле ответа в результате извлечения ключевых фраз
    """
    keywords: list[str]
