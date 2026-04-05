import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from app.main import app
from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionException
from app.dependencies import (
    get_keyword_extraction_service,
    get_patent_parser_service,
    get_text_builder_service,
    get_file_reader_service
)


@pytest.fixture
def client():
    service_mock = MagicMock()
    service_mock.extract_keywords.return_value = ["патент", "поиск"]

    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_extract_from_text_success(client):
    response = client.post(
        "/keywords/extract-from-text",
        content="Устройство содержит волокна со спиралью.",
        headers={"Content-Type": "text/plain"}
    )

    assert response.status_code == 200
    data = response.json()

    assert "keywords" in data
    assert isinstance(data["keywords"], list)


def test_extract_from_text_empty(client):
    response = client.post(
        "/keywords/extract-from-text",
        content="",
        headers={"Content-Type": "text/plain"}
    )

    assert response.status_code == 422


def test_extract_from_text_business_error():
    service_mock = MagicMock()
    service_mock.extract_keywords.side_effect = KeywordExtractionException("Нет данных")

    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    client = TestClient(app)

    response = client.post(
        "/keywords/extract-from-text",
        content="Тест",
        headers={"Content-Type": "text/plain"}
    )

    assert response.status_code == 400


def test_extract_from_url_success():
    parser_mock = AsyncMock()
    parser_mock.parse_single_patent.return_value = {"title": "Test patent"}

    builder_mock = MagicMock()
    builder_mock.build.return_value = "test patent text"

    service_mock = MagicMock()
    service_mock.extract_keywords.return_value = ["патент"]

    app.dependency_overrides[get_patent_parser_service] = lambda: parser_mock
    app.dependency_overrides[get_text_builder_service] = lambda: builder_mock
    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    client = TestClient(app)

    response = client.post(
        "/keywords/extract-from-url",
        json={"url": "https://patents.google.com/patent/US123"}
    )

    assert response.status_code == 200
    assert response.json()["keywords"] == ["патент"]


def test_extract_from_file_success():
    reader_mock = AsyncMock()
    reader_mock.read.return_value = "test text"

    service_mock = MagicMock()
    service_mock.extract_keywords.return_value = ["патент"]

    app.dependency_overrides[get_file_reader_service] = lambda: reader_mock
    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    client = TestClient(app)

    file_data = {
        "file": ("test.txt", b"test text", "text/plain")
    }

    response = client.post(
        "/keywords/extract-from-file",
        files=file_data
    )

    assert response.status_code == 200
    assert response.json()["keywords"] == ["патент"]
