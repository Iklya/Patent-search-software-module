from fastapi import FastAPI

app = FastAPI(
    title="Программный модуль патентного поиска",
    version="1.0.0"
)


@app.get("/")
async def root():
    """
    Корневой маршрут для подтверждения работы API.
    """
    return {"message": "Программный модуль патентного поиска!"}