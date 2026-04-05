from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.patent_collection.patent_collection_service import PatentCollectionService


@pytest.fixture
def service():
    page = AsyncMock()
    return PatentCollectionService(page)


def test_set_query(service):
    assert service.set_query("fiber optic") == "fiber%20optic"
    assert service.set_query("") == ""


def test_extract_publication_number(service):
    link = "https://patents.google.com/patent/RU123A"
    pub = service.extract_publication_number(link)
    assert pub == "RU123A"


@pytest.mark.asyncio
async def test_find_patent_links(service):
    service.page.eval_on_selector_all = AsyncMock(
        return_value=["patent/RU1", "patent/RU2"]
    )
    links = await service.find_patent_links()
    assert len(links) == 2


def test_set_search_url(service):
    url = service.set_search_url("test", "20240101", 0)
    assert "after=publication:20240101" in url
    assert "before=publication:20240101" in url
    assert "q=test" in url
    assert "page=0" in url


def test_set_search_url_without_query(service):
    url = service.set_search_url("", "20240101", 1)
    assert "q=" not in url
    assert "page=1" in url


def test_add_patents_to_collection(service):
    links = ["https://patents.google.com/patent/RU1", "https://patents.google.com/patent/RU2"]
    results = []
    result = service.add_patents_to_collection(links, results, 5)
    assert result is False
    assert len(results) == 2


def test_add_patents_to_collection_reaches_limit(service):
    links = ["https://patents.google.com/patent/RU1", "https://patents.google.com/patent/RU2"]
    results = []
    result = service.add_patents_to_collection(links, results, 1)
    assert result is True
    assert len(results) == 1


def test_add_patents_to_collection_invalid_link(service):
    links = ["invalid_link"]
    results = []
    result = service.add_patents_to_collection(links, results, 5)
    assert result is False
    assert len(results) == 0


@pytest.mark.asyncio
async def test_load_patents_page(service):
    service.page.goto = AsyncMock()
    service.page.wait_for_selector = AsyncMock()
    service.page.wait_for_timeout = AsyncMock()
    
    await service.load_patents_page("http://test.com")
    
    service.page.goto.assert_called_once()
    service.page.wait_for_selector.assert_called_once()
    service.page.wait_for_timeout.assert_called_once()


@pytest.mark.asyncio
async def test_search_patents_by_date(service):
    service.set_search_url = MagicMock(return_value="http://test.com")
    service.load_patents_page = AsyncMock()
    service.find_patent_links = AsyncMock(return_value=["link1", "link2"])
    service.add_patents_to_collection = MagicMock(return_value=False)
    
    results = []
    await service.search_patents_by_date(results, "query", "20240101", 10)
    
    service.load_patents_page.assert_called()
    service.find_patent_links.assert_called()


@pytest.mark.asyncio
async def test_search_patents_by_date_no_links(service):
    service.set_search_url = MagicMock(return_value="http://test.com")
    service.load_patents_page = AsyncMock()
    service.find_patent_links = AsyncMock(return_value=[])
    
    results = []
    await service.search_patents_by_date(results, "query", "20240101", 10)
    
    service.find_patent_links.assert_called()


@pytest.mark.asyncio
async def test_collect_patent_links(service):
    service.search_patents_by_date = AsyncMock()
    
    result = await service.collect_patent_links("test", 5, "2024-01-01", "2024-01-03")
    
    assert isinstance(result, list)
    assert service.search_patents_by_date.call_count >= 1
