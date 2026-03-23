from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.patent_search.patent_search_service import PatentSearchService
from app.schemas.search_schemas.patent_search_schema import PatentSearchCreate, PatentSearch
from app.dependencies import get_patent_search_service


router = APIRouter(
    prefix="/patents",
    tags=["Patent Search"]
)


@router.post(
    "/search",
    response_model=PatentSearch,
    status_code=status.HTTP_200_OK
)
async def search_patents(
    request: PatentSearchCreate,
    service: PatentSearchService = Depends(get_patent_search_service)
):
    try:
        total, results = await service.search(**request.model_dump(exclude_none=True))

        return PatentSearch(
            total=total,
            search_result=results)
    
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось выполнить поиск патентов."
        )
