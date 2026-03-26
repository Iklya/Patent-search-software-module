from app.core.logger import get_logger
from app.core.settings import settings


logger = get_logger(__name__)


class PatentTextBuilder:
    """
    Используется для формирования текста патента из структурированного JSON.
    """
    def __init__(self):
        self.max_text_length = settings.google_patent_text_max_length
    
    
    def build(self, patent_json: dict) -> str:
        fields = [
            patent_json.get("title") or "",
            patent_json.get("abstract") or "",
            patent_json.get("claims") or "",
            patent_json.get("description") or "",
        ]

        text = "\n\n".join([f for f in fields if f.strip()])
        
        text = text[:self.max_text_length]
        logger.debug(f"Собран текст патента. Длина: {len(text)} символов")

        return text