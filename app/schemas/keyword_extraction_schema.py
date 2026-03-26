from pydantic import BaseModel, Field, HttpUrl


class KeywordExtractionFromUrlRequest(BaseModel):
    url: HttpUrl = Field(..., description="Ссылка на патент Google Patents")


class KeywordExtraction(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле ответа в результате извлечения ключевых фраз
    """
    keywords: list[str]
