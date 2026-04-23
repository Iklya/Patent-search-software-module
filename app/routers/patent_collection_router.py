from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patent_collection.patent_parser_service import PatentParserService
from app.services.patent_storage.patent_storage_service import PatentStorageService
from app.services.patent_indexing.patent_indexing_service import PatentIndexingService
from app.schemas.patent_collection_schema import PatentsLoadCreate, PatentUrlsRequest
from app.dependencies import get_patent_parser_service
from app.db_dependency import get_db_session


router = APIRouter(
    prefix="/patents",
    tags=["Patent Collection"]
)


@router.post(
    "/load",
    status_code=status.HTTP_200_OK
)
async def load_patents(
    request: PatentsLoadCreate,
    service: PatentParserService = Depends(get_patent_parser_service),
    session: AsyncSession = Depends(get_db_session)
):
    try:
        storage = PatentStorageService(session)
        indexer = PatentIndexingService(session)

        patents = await service.parse_patents(
            session,
            **request.model_dump(mode="json")
        )
        
        await storage.store_patents(patents)

        await indexer.index_all_patents()

        return {
            "message": f"Актуализация базы патентов новыми документами в размере {len(patents)} шт. выполнена успешно."
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось выполнить загрузку патентов."
        )
    
    finally:
        if indexer:
            await indexer.es.client.close()


'''Дополнительный эндпоинт для патентного поиска
    (позволяет сохранять в хранилища и индексировать конкретные патенты по ссылке)'''
@router.post("/load-by-urls")
async def load_patents_by_urls(
    request: PatentUrlsRequest,
    service: PatentParserService = Depends(get_patent_parser_service),
    session: AsyncSession = Depends(get_db_session)
):
    try:
        storage = PatentStorageService(session)
        indexer = PatentIndexingService(session)

        patents = await service.parse_patents_from_urls(
            session=session,
            urls=request.urls
        )

        await storage.store_patents(patents)
        await indexer.index_all_patents()

        return {
            "message": f"Загружено патентов: {len(patents)}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка загрузки патентов по URL: {e}"
        )

    finally:
        if indexer:
            await indexer.es.client.close()
