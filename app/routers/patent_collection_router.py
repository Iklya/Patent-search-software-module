from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patent_collection.patent_parser_service import PatentParserService
from app.schemas.patent_collection_schema import PatentsLoadCreate
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
        results = await service.parse(
            session=session,
            **request.model_dump(mode="json")
        )
        
        return {"message": f"Сбор {len(results)} патентов выполнен успешно."}

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
