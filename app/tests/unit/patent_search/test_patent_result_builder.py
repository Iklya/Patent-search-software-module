import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.patent_search.patent_result_builder import PatentResultBuilder


@pytest.fixture
def builder():
    session = AsyncMock()
    builder = PatentResultBuilder(session)

    builder.find_patents_from_database = AsyncMock()
    builder.apply_highlight_for_text_fields = MagicMock(
        return_value=("t", "a", "c", "d")
    )

    return builder


@pytest.mark.asyncio
async def test_build_results_empty(builder):
    result = await builder.build_results([])
    assert result == []


@pytest.mark.asyncio
async def test_build_results_success(builder):
    builder.find_patents_from_database.return_value = {
        1: MagicMock(
            id=1,
            publication_number="PN",
            application_number="AN",
            title="title",
            country_code="US",
            kind_code="A",
            filing_date=None,
            publication_date=None,
            inventors=[],
            classifications=[],
            citations=[],
            concepts=[],
            source_url="url",
            parsed_at=None
        )
    }

    result = await builder.build_results([
        {"patent_id": 1, "score": 1.0, "highlight": {}}
    ])

    assert len(result) == 1


def test_apply_highlight_no_text(builder):
    result = builder.apply_highlight("", ["<mark>test</mark>"])
    assert result == ""


def test_apply_highlight_no_fragments(builder):
    result = builder.apply_highlight("test text", None)
    assert result == "test text"


def test_apply_highlight_success(builder):
    text = "hello world"
    fragments = ["<mark>world</mark>"]

    result = builder.apply_highlight(text, fragments)

    assert "<mark>" in result
