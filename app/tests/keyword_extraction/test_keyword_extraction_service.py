import pytest
from unittest.mock import MagicMock

from app.services.keyword_extraction.keyword_extraction_service import (
    KeywordExtractionService,
    KeywordExtractionException
)


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setenv("MODEL_PATH", "app/ml_models/keyt5_patent")
    monkeypatch.setenv("MAX_INPUT_LENGTH", "10000")

    svc = KeywordExtractionService()

    svc.ensure_model_loaded = MagicMock()
    svc.prepare_inputs = MagicMock(return_value={"input_ids": None})
    svc.generate_keywords = MagicMock(return_value=[[1, 2, 3]])
    svc.decode_output = MagicMock(return_value=["патент", "поиск", "патент"])

    return svc


def test_extract_keywords_success(service):
    result = service.extract_keywords("Текст")

    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(k, str) and k.strip() != "" for k in result)
    assert len(result) == len(set(result))


def test_extract_keywords_empty_result(service):
    service.decode_output = MagicMock(return_value=[])

    with pytest.raises(KeywordExtractionException):
        service.extract_keywords("Текст")


def test_model_path_not_set(monkeypatch):
    monkeypatch.delenv("MODEL_PATH", raising=False)
    monkeypatch.setenv("MAX_INPUT_LENGTH", "10000")

    with pytest.raises(KeywordExtractionException):
        KeywordExtractionService()


def test_max_length_not_set(monkeypatch):
    monkeypatch.setenv("MODEL_PATH", "app/ml_models/keyt5_patent")
    monkeypatch.delenv("MAX_INPUT_LENGTH", raising=False)

    with pytest.raises(KeywordExtractionException):
        KeywordExtractionService()