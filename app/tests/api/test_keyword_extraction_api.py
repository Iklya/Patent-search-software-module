import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app
from app.dependencies import get_keyword_extraction_service
from app.services.keyword_extraction.keyword_extraction_service import KeywordExtractionException


@pytest.fixture
def client():
    service_mock = MagicMock()
    service_mock.extract_keywords.return_value = ["патент", "поиск"]

    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_extract_keywords_success(client):
    response = client.post(
        "/keywords/extract",
        json={"text": "Устройство содержит волокна со спиралью."}
    )

    assert response.status_code == 200

    data = response.json()

    assert "keywords" in data
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) > 0
    assert all(isinstance(k, str) and k.strip() != "" for k in data["keywords"])
    assert len(data["keywords"]) == len(set(data["keywords"]))


def test_request_without_body(client):
    response = client.post("/keywords/extract")
    assert response.status_code == 422


def test_empty_string(client):
    response = client.post(
        "/keywords/extract",
        json={"text": ""}
    )
    assert response.status_code == 422


def test_whitespace_string(client):
    response = client.post(
        "/keywords/extract",
        json={"text": "     "}
    )
    assert response.status_code == 422


def test_too_long_text(client):
    long_text = "a" * 20000

    response = client.post(
        "/keywords/extract",
        json={"text": long_text}
    )

    assert response.status_code == 422


def test_missing_text_field(client):
    response = client.post(
        "/keywords/extract",
        json={}
    )
    assert response.status_code == 422


def test_business_exception():
    service_mock = MagicMock()
    service_mock.extract_keywords.side_effect = KeywordExtractionException("Нет данных")

    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    client = TestClient(app)

    response = client.post(
        "/keywords/extract",
        json={"text": "Тест"}
    )

    assert response.status_code == 400


def test_internal_error():
    service_mock = MagicMock()
    service_mock.extract_keywords.side_effect = Exception("Ошибка")

    app.dependency_overrides[get_keyword_extraction_service] = lambda: service_mock

    client = TestClient(app)

    response = client.post(
        "/keywords/extract",
        json={"text": "Тест"}
    )

    assert response.status_code == 500


def test_non_informative_text(client):
    app.dependency_overrides.clear()

    client = TestClient(app)

    response = client.post(
        "/keywords/extract",
        json={"text": "1234567890"}
    )

    assert response.status_code == 400