import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.patent_storage.postgresql_service import PostgreSQLService
from app.models.inventors import Inventor
from app.models.classifications import Classification
from app.models.citations import Citation


@pytest.fixture
def pg_service():
    session = MagicMock()
    session.add = MagicMock()
    return PostgreSQLService(session)


@pytest.mark.asyncio
async def test_get_or_create_inventor_exists(pg_service):
    mock_inventor = MagicMock(spec=Inventor)
    mock_inventor.full_name = "John Doe"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_inventor)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_inventor("John Doe")

    assert result == mock_inventor
    pg_service.session.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_inventor_new(pg_service):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_inventor("Jane Smith")

    assert isinstance(result, Inventor)
    assert result.full_name == "Jane Smith"
    pg_service.session.add.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_classification_exists(pg_service):
    mock_class = MagicMock(spec=Classification)
    mock_class.code = "G01N33/00"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_class)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_classification("G01N33/00")

    assert result == mock_class
    pg_service.session.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_classification_new(pg_service):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_classification("H04L29/06")

    assert isinstance(result, Classification)
    assert result.code == "H04L29/06"
    pg_service.session.add.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_citation_exists(pg_service):
    mock_citation = MagicMock(spec=Citation)
    mock_citation.publication_number = "US1234567B"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_citation)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_citation("US1234567B")

    assert result == mock_citation
    pg_service.session.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_citation_new(pg_service):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_citation("EP9876543A")

    assert isinstance(result, Citation)
    assert result.publication_number == "EP9876543A"
    pg_service.session.add.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_concept_exists(pg_service):
    from app.models.concepts import Concept
    
    mock_concept = MagicMock(spec=Concept)
    mock_concept.name = "machine learning"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_concept)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_concept("machine learning")

    assert result == mock_concept
    pg_service.session.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_concept_new(pg_service):
    from app.models.concepts import Concept
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    pg_service.session.execute = AsyncMock(return_value=mock_result)

    result = await pg_service.get_or_create_concept("neural network")

    assert isinstance(result, Concept)
    assert result.name == "neural network"
    pg_service.session.add.assert_called_once()
