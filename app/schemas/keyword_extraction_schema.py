from pydantic import BaseModel, Field, field_validator


class KeywordExtractionCreate(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле запроса
    """
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Текст, из которого будут извлечены ключевые фразы"
    )

    @field_validator("text")
    @classmethod
    def validate_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("Входной текст не должен быть пустым.")
        
        return value
    
class KeywordExtraction(BaseModel):
    """
    Pydantic-модель с описанием содержимого в теле ответа
    """
    keywords: list[str]
