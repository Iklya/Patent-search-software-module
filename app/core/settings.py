from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError
from app.core.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):

    database_url: str
    hdfs_url: str

    model_path: str
    max_chunks: int
    chunk_overlap_ratio: float
    generation_max_length: int
    generation_num_beams: int
    generation_no_repeat_ngram_size: int

    max_user_input_length: int
    google_patent_text_max_length: int
    file_text_max_length: int

    google_patents_base_url: str
    google_patents_max_pages: int
    google_patents_results_per_page: int

    playwright_page_load_timeout: int
    playwright_selector_timeout: int
    playwright_scroll_wait: int
    playwright_patent_timeout: int
    playwright_scroll_iterations: int
    playwright_scroll_wait_after: int

    elasticsearch_url: str
    indexing_batch_size: int

    max_result_window: int

    model_config = SettingsConfigDict(
        case_sensitive=False
    )


try:
    settings = Settings(_env_file=".env")
    logger.info("Переменные окружения успешно загружены.")

except ValidationError:
    logger.exception("Ошибка загрузки переменных окружения.")
    raise