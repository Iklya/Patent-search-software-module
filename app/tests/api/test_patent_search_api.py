import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.dependencies import get_patent_search_service


@pytest.fixture
def client():
    service_mock = AsyncMock()
    service_mock.search.return_value = {
        "total": 1,
        "page": 1,
        "page_size": 10,
        "results": [{"id": 1}]
    }

    app.dependency_overrides[get_patent_search_service] = lambda: service_mock

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_search_patents_success(client):
    response = client.post(
        "/patents/search",
        json={
            "keywords": ["test"],
            "page": 1,
            "page_size": 10
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 1
    assert "search_result" in data


def test_search_patents_runtime_error():
    service_mock = AsyncMock()
    service_mock.search.side_effect = RuntimeError("Ошибка поиска")

    app.dependency_overrides[get_patent_search_service] = lambda: service_mock

    client = TestClient(app)

    response = client.post(
        "/patents/search",
        json={"page": 1, "page_size": 10}
    )

    assert response.status_code == 400
    assert "Ошибка поиска" in response.text


def test_search_patents_internal_error():
    service_mock = AsyncMock()
    service_mock.search.side_effect = Exception("boom")

    app.dependency_overrides[get_patent_search_service] = lambda: service_mock

    client = TestClient(app)

    response = client.post(
        "/patents/search",
        json={"page": 1, "page_size": 10}
    )

    assert response.status_code == 500
    assert "Не удалось выполнить поиск патентов" in response.text
