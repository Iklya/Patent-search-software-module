from fastapi import APIRouter, HTTPException, status, Depends, Body, UploadFile, File
from fastapi.concurrency import run_in_threadpool

from app.schemas.keyword_extraction_schema import KeywordExtractionFromUrlRequest, KeywordExtraction
from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionService, KeywordExtractionException
from app.services.keyword_extraction.patent_text_builder import PatentTextBuilder
from app.services.keyword_extraction.text_file_reader import TextFileReader
from app.services.patent_collection.patent_parser_service import PatentParserService
from app.dependencies import (get_keyword_extraction_service, get_text_builder_service,
                                get_patent_parser_service, get_file_reader_service)


router = APIRouter(
    prefix="/keywords",
    tags=["Keyword Extraction"]
)


@router.post(
    "/extract-from-text",
    response_model=KeywordExtraction,
    status_code=status.HTTP_200_OK
)
async def keyword_extraction_from_text(
    text: str = Body(
        ...,
        media_type="text/plain",
        min_length=1,
        max_length=10000
    ),
    service: KeywordExtractionService = Depends(get_keyword_extraction_service)
):
    try:
        keywords = await run_in_threadpool(
            service.extract_keywords,
            text
        )
        return KeywordExtraction(keywords=keywords)
    
    except KeywordExtractionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось извлечь ключевые фразы. Попробуйте повторить операцию позже. {str(e)}"
        )


@router.post(
    "/extract-from-url",
    response_model=KeywordExtraction,
    status_code=status.HTTP_200_OK
)
async def keyword_extraction_from_url(
    request: KeywordExtractionFromUrlRequest,
    parser: PatentParserService = Depends(get_patent_parser_service),
    builder: PatentTextBuilder = Depends(get_text_builder_service),
    service: KeywordExtractionService = Depends(get_keyword_extraction_service)
):
    try:
        patent_json = await parser.parse_single_patent(str(request.url))

        text = builder.build(patent_json)

        keywords = await run_in_threadpool(
            service.extract_keywords,
            text
        )

        return KeywordExtraction(keywords=keywords)

    except KeywordExtractionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось извлечь ключевые фразы по ссылке на патент. Попробуйте повторить операцию позже. {str(e)}"
        )


@router.post(
    "/extract-from-file",
    response_model=KeywordExtraction,
    status_code=status.HTTP_200_OK
)
async def keyword_extraction_from_file(
    file: UploadFile = File(...),
    service: KeywordExtractionService = Depends(get_keyword_extraction_service),
    reader: TextFileReader = Depends(get_file_reader_service)
):
    try:
        text = await reader.read(file)

        keywords = await run_in_threadpool(
            service.extract_keywords,
            text
        )

        return KeywordExtraction(keywords=keywords)


    except KeywordExtractionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Не удалось извлечь ключевые фразы из файла. Попробуйте повторить операцию позже. {str(e)}"
        )
