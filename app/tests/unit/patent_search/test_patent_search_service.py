import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.patent_search.patent_search_service import PatentSearchService


@pytest.fixture
def service():
    svc = PatentSearchService()

    svc.es = MagicMock()
    svc.es.index_exists = AsyncMock(return_value=True)
    svc.es.client.search = AsyncMock(return_value={
        "hits": {
            "total": {"value": 1},
            "hits": []
        }
    })
    svc.es.close = AsyncMock()

    svc.highlight = MagicMock()
    svc.highlight.add_highlight = MagicMock()
    svc.highlight.extract_highlight_results.return_value = []

    svc.build_final_json = AsyncMock(return_value=[])

    return svc


@pytest.mark.asyncio
async def test_search_success(service):
    result = await service.search(page=1, page_size=10)

    assert result["total"] == 1
    assert "results" in result


@pytest.mark.asyncio
async def test_search_index_not_exists(service):
    service.es.index_exists = AsyncMock(return_value=False)

    with pytest.raises(RuntimeError):
        await service.search()


def test_add_keywords_for_search():
    svc = PatentSearchService()

    must = []
    svc.add_keywords_for_search(must, ["a", "b"], "AND")

    assert len(must) == 1


def test_add_keywords_empty():
    svc = PatentSearchService()

    must = []
    svc.add_keywords_for_search(must, None, "AND")

    assert must == []


def test_add_text_fields():
    svc = PatentSearchService()

    must = []
    svc.add_text_fields_for_search(must, "t", "a", None, None)

    assert len(must) == 2


def test_add_exact_match():
    svc = PatentSearchService()

    filters = []
    svc.add_fields_for_exact_match_search(filters, "pn", None, None, None)

    assert len(filters) == 1


def test_add_date_fields():
    svc = PatentSearchService()

    filters = []
    svc.add_date_fields_for_search(filters, "2020", None, None, None)

    assert len(filters) == 1


def test_apply_result_window_normal():
    svc = PatentSearchService()

    from_page, size, flag = svc.apply_result_window(1, 10)

    assert flag is False


def test_apply_result_window_out_of_range(monkeypatch):
    svc = PatentSearchService()

    from app.core.settings import settings
    monkeypatch.setattr(settings, "max_result_window", 10)

    from_page, size, flag = svc.apply_result_window(5, 10)

    assert flag is True


def test_add_sort_valid():
    svc = PatentSearchService()

    query = {}
    svc.add_sort_field_for_search(query, "title", "asc")

    assert "sort" in query


def test_add_sort_invalid():
    svc = PatentSearchService()

    query = {}
    svc.add_sort_field_for_search(query, "unknown", "asc")

    assert "sort" not in query
