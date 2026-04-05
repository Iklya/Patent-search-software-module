import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.patent_collection.patent_parser_service import PatentParserService


@pytest.fixture
def service():
    collection = AsyncMock()
    preparation = MagicMock()
    return PatentParserService(collection, preparation)


@pytest.mark.asyncio
async def test_filter_existing_links(service):
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.fetchall = MagicMock(return_value=[("link1",)])
    session.execute = AsyncMock(return_value=mock_result)

    result = await service.filter_existing_links(session, ["link1", "link2", "link3"])

    assert result == ["link2", "link3"]


@pytest.mark.asyncio
async def test_filter_existing_links_empty_list(service):
    session = AsyncMock()

    result = await service.filter_existing_links(session, [])

    assert result == []
    session.execute.assert_not_called()


@pytest.mark.asyncio
async def test_filter_existing_links_all_existing(service):
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.fetchall = MagicMock(return_value=[("link1",), ("link2",), ("link3",)])
    session.execute = AsyncMock(return_value=mock_result)

    result = await service.filter_existing_links(session, ["link1", "link2", "link3"])

    assert result == []


@pytest.mark.asyncio
async def test_fetch_page_html_success(service):
    page = AsyncMock()
    page.goto = AsyncMock()
    
    async def evaluate_side_effect(script):
        if "scrollHeight" in script:
            return 100
        return None
    
    page.evaluate = AsyncMock(side_effect=evaluate_side_effect)
    page.content = AsyncMock(return_value="<html><body>Test</body></html>")
    page.wait_for_timeout = AsyncMock()

    html = await service.fetch_page_html(page, "http://test.com")

    assert "<html>" in html
    assert page.goto.call_count == 1


@pytest.mark.asyncio
async def test_fetch_page_html_scroll_until_stable(service):
    page = AsyncMock()
    page.goto = AsyncMock()
    
    scroll_heights = [100, 200, 200, 200]
    call_count = 0
    
    async def evaluate_side_effect(script):
        nonlocal call_count
        if "scrollHeight" in script:
            height = scroll_heights[call_count % len(scroll_heights)]
            call_count += 1
            return height
        return None
    
    page.evaluate = AsyncMock(side_effect=evaluate_side_effect)
    page.content = AsyncMock(return_value="<html></html>")
    page.wait_for_timeout = AsyncMock()

    html = await service.fetch_page_html(page, "http://test.com")

    assert html == "<html></html>"


@pytest.mark.asyncio
async def test_create_browser_page(service):
    with patch("app.services.patent_collection.patent_parser_service.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_chromium = AsyncMock()
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        
        mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
        mock_playwright_instance.chromium = mock_chromium
        mock_chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        
        p, browser, page = await service.create_browser_page()
        
        assert p == mock_playwright_instance
        assert browser == mock_browser
        assert page == mock_page


@pytest.mark.asyncio
async def test_close_browser(service):
    p = AsyncMock()
    browser = AsyncMock()
    
    await service.close_browser(p, browser)
    
    browser.close.assert_awaited_once()
    p.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_single_patent(service):
    service.create_browser_page = AsyncMock()
    service.fetch_page_html = AsyncMock(return_value="<html></html>")
    service.preparation_service.prepare_patent_json = MagicMock(return_value={"publication_number": "RU123"})
    service.close_browser = AsyncMock()
    
    mock_playwright = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    service.create_browser_page.return_value = (mock_playwright, mock_browser, mock_page)
    
    result = await service.parse_single_patent("http://test.com/patent/RU123")
    
    assert result == {"publication_number": "RU123"}
    service.fetch_page_html.assert_called_once_with(mock_page, "http://test.com/patent/RU123")
    service.close_browser.assert_awaited_once_with(mock_playwright, mock_browser)


@pytest.mark.asyncio
async def test_parse_patents_full_flow(service):
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.fetchall = MagicMock(return_value=[])
    session.execute = AsyncMock(return_value=mock_result)
    
    service.create_browser_page = AsyncMock()
    service.close_browser = AsyncMock()
    
    mock_playwright = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    service.create_browser_page.return_value = (mock_playwright, mock_browser, mock_page)
    
    mock_collection = AsyncMock()
    mock_collection.collect_patent_links = AsyncMock(return_value=["url1", "url2"])
    service.collection_service = mock_collection
    
    service.filter_existing_links = AsyncMock(return_value=["url1"])
    service.fetch_page_html = AsyncMock(return_value="<html></html>")
    service.preparation_service.prepare_patent_json = MagicMock(
        return_value={"publication_number": "RU123"}
    )
    
    result = await service.parse_patents(
        session=session,
        query="test",
        limit=2,
        date_from="2024-01-01",
        date_to="2024-01-02"
    )
    
    assert len(result) == 1
    service.close_browser.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_patents_empty_links(service):
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.fetchall = MagicMock(return_value=[])
    session.execute = AsyncMock(return_value=mock_result)
    
    service.create_browser_page = AsyncMock()
    service.close_browser = AsyncMock()
    
    mock_playwright = AsyncMock()
    mock_browser = AsyncMock()
    mock_page = AsyncMock()
    service.create_browser_page.return_value = (mock_playwright, mock_browser, mock_page)
    
    mock_collection = AsyncMock()
    mock_collection.collect_patent_links = AsyncMock(return_value=[])
    service.collection_service = mock_collection
    
    result = await service.parse_patents(
        session=session,
        query="test",
        limit=2,
        date_from="2024-01-01",
        date_to="2024-01-02"
    )
    
    assert result == []
