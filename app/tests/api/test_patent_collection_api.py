import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.dependencies import get_patent_parser_service
from app.db_dependency import get_db_session


@pytest.fixture
def client():
    parser_mock = AsyncMock()
    parser_mock.parse_patents.return_value = []

    session_mock = AsyncMock()

    app.dependency_overrides[get_patent_parser_service] = lambda: parser_mock
    app.dependency_overrides[get_db_session] = lambda: session_mock

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_load_patents_success(client):
    with patch("app.routers.patent_collection_router.PatentIndexingService") as MockIndexing:
        mock_indexer = MagicMock()
        mock_indexer.index_all_patents = AsyncMock()
        mock_indexer.es = MagicMock()
        mock_indexer.es.client = AsyncMock()
        mock_indexer.es.client.close = AsyncMock()
        MockIndexing.return_value = mock_indexer
        
        response = client.post(
            "/patents/load",
            json={
                "query": "",
                "limit": 1,
                "date_from": "2015-03-27",
                "date_to": "2020-01-02"
            }
        )

        assert response.status_code == 200
        assert "message" in response.json()


def test_load_patents_value_error():
    parser_mock = AsyncMock()
    parser_mock.parse_patents.side_effect = ValueError("bad query")

    app.dependency_overrides[get_patent_parser_service] = lambda: parser_mock

    client = TestClient(app)

    response = client.post(
        "/patents/load",
        json={"query": "x", "limit": 5}
    )

    assert response.status_code == 400
    assert "bad query" in response.json()["detail"]


def test_load_patents_internal_error():
    parser_mock = AsyncMock()
    parser_mock.parse_patents.side_effect = Exception("Unexpected error")

    app.dependency_overrides[get_patent_parser_service] = lambda: parser_mock

    client = TestClient(app)

    response = client.post(
        "/patents/load",
        json={"query": "x", "limit": 5}
    )

    assert response.status_code == 500
    assert "Не удалось выполнить загрузку патентов" in response.json()["detail"]
