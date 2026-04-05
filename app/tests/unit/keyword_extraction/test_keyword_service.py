import pytest
from unittest.mock import MagicMock

from app.services.keyword_extraction.keyword_extraction_service import (
    KeywordExtractionService,
    KeywordExtractionException
)


@pytest.fixture
def service():
    svc = KeywordExtractionService()

    svc.ensure_model_loaded = MagicMock()

    svc.tokenizer = MagicMock()
    svc.tokenizer.encode.return_value = list(range(20))
    svc.tokenizer.decode.return_value = "keyword1; keyword2"

    svc.prepare_inputs = MagicMock(return_value={"input_ids": None})
    svc.generate_keywords = MagicMock(return_value=[[1, 2, 3]])

    return svc


def test_extract_keywords_success(service):
    result = service.extract_keywords("Тестовый текст содержит текст")

    assert isinstance(result, list)
    assert len(result) > 0


def test_validate_text_content(service):
    with pytest.raises(KeywordExtractionException):
        service.validate_text_content("123456789")


def test_split_into_chunks(service):
    service.max_input_length = 5
    service.chunk_overlap_ratio = 0

    chunks = service.split_into_chunks("текст")

    assert isinstance(chunks, list)
    assert len(chunks) > 0


def test_decode_output_success(service):
    tokens = [[1, 2, 3]]

    result = service.decode_output(tokens)

    assert result == ["keyword1", "keyword2"]


def test_decode_output_empty(service):
    service.tokenizer.decode.return_value = ""

    with pytest.raises(KeywordExtractionException):
        service.decode_output([[1, 2, 3]])
