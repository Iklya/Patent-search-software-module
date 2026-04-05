import pytest

from app.services.patent_search.highlight_service import HighlightService


@pytest.fixture
def service():
    return HighlightService()


def test_add_highlight(service):
    query = {}

    service.add_highlight(query)

    assert "highlight" in query
    assert "fields" in query["highlight"]


def test_extract_highlight_results_success(service):
    response = {
        "hits": {
            "hits": [
                {
                    "_source": {"patent_id": "1"},
                    "_score": 1.5,
                    "highlight": {"title": ["<mark>test</mark>"]}
                }
            ]
        }
    }

    result = service.extract_highlight_results(response)

    assert isinstance(result, list)
    assert result[0]["patent_id"] == 1


def test_extract_highlight_results_empty(service):
    response = {"hits": {"hits": []}}

    result = service.extract_highlight_results(response)

    assert result == []
