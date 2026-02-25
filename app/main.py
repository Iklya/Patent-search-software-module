from fastapi import FastAPI
import logging

from app.routers.keyword_extraction_router import router as keyword_router
from app.dependencies import get_keyword_extraction_service


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Программный модуль патентного поиска",
    version="1.0.0"
)

app.include_router(keyword_router)


@app.get("/")
async def root():
    return {"message": "Программный модуль патентного поиска!"}


@app.on_event("startup")
async def startup_event():
    logger.info("Запуск приложения и загрузка ML модели.")
    svc = get_keyword_extraction_service()
    svc.ensure_model_loaded()
    logger.info("Модель успешно загружена.")
