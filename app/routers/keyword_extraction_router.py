from fastapi import APIRouter, HTTPException, status, Depends, Body

from app.schemas.keyword_extraction_schema import KeywordExtraction
from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionService, KeywordExtractionException
from app.dependencies import get_keyword_extraction_service


router = APIRouter(
    prefix="/keywords",
    tags=["Keyword Extraction"]
)


@router.post(
    "/extract",
    response_model=KeywordExtraction,
    status_code=status.HTTP_200_OK
)
async def keyword_extraction(
    text: str = Body(
        ...,
        media_type="text/plain",
        min_length=1,
        max_length=10000
    ),
    service: KeywordExtractionService = Depends(get_keyword_extraction_service)
):
    try:
        keywords = service.extract_keywords(text)
        return KeywordExtraction(keywords=keywords)
    
    except KeywordExtractionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось извлечь ключевые фразы. Попробуйте повторить операцию позже."
        )