from fastapi import FastAPI

from app.routers.keyword_extraction_router import router as keyword_router

app = FastAPI(
    title="Программный модуль патентного поиска",
    version="1.0.0"
)

app.include_router(keyword_router)


@app.get("/")
async def root():
    """
    Корневой маршрут для подтверждения работы API.
    """
    return {"message": "Программный модуль патентного поиска!"}
