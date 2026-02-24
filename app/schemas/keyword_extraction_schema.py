from pydantic import BaseModel, Field, field_validator

class KeywordExtractionCreate(BaseModel):
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
    keywords: list[str]