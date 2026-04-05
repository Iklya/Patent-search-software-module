import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.patent_indexing.patent_indexing_service import PatentIndexingService


@pytest.fixture
def mock_patent():
    patent = MagicMock()
    patent.id = 1
    patent.publication_number = "RU123456A"
    patent.application_number = "RU2023123456"
    patent.country_code = "RU"
    patent.kind_code = "A"
    patent.title = "Test Patent"
    patent.filing_date = "2023-01-01"
    patent.publication_date = "2023-06-01"
    patent.abstract_hdfs_path = "/path/abstract.txt"
    patent.description_hdfs_path = "/path/description.txt"
    patent.claims_hdfs_path = "/path/claims.txt"
    patent.inventors = []
    patent.classifications = []
    return patent


@pytest.mark.asyncio
async def test_index_all_patents_no_new_patents():
    session = AsyncMock()

    svc = PatentIndexingService(session)

    svc.es = MagicMock()
    svc.es.create_index_if_not_exists = AsyncMock()
    svc.es.create_meta_index_if_not_exists = AsyncMock()
    svc.es.get_last_indexed_id = AsyncMock(return_value=0)
    svc.es.close = AsyncMock()

    svc.find_not_indexed_patents = AsyncMock(return_value=[])
    svc.documents_limit = 1000

    await svc.index_all_patents()

    svc.es.create_index_if_not_exists.assert_called_once()
    svc.es.create_meta_index_if_not_exists.assert_called_once()
    svc.es.get_last_indexed_id.assert_called_once()
    svc.find_not_indexed_patents.assert_called_once_with(0)
    svc.es.bulk_index.assert_not_called()
    svc.es.update_last_indexed_id.assert_not_called()
    svc.es.close.assert_called_once()


@pytest.mark.asyncio
async def test_index_all_patents_with_data(mock_patent):
    session = AsyncMock()

    svc = PatentIndexingService(session)

    svc.es = MagicMock()
    svc.es.create_index_if_not_exists = AsyncMock()
    svc.es.create_meta_index_if_not_exists = AsyncMock()
    svc.es.get_last_indexed_id = AsyncMock(return_value=0)
    svc.es.bulk_index = AsyncMock()
    svc.es.update_last_indexed_id = AsyncMock()
    svc.es.close = AsyncMock()

    svc.find_not_indexed_patents = AsyncMock(return_value=[mock_patent])
    svc.documents_limit = 1000
    
    svc.hdfs = MagicMock()
    svc.hdfs.read_file = MagicMock(return_value="Full text content")
    
    svc.build_document = MagicMock(return_value={
        "patent_id": 1,
        "publication_number": "RU123456A",
        "title": "Test Patent"
    })

    await svc.index_all_patents()

    svc.es.bulk_index.assert_called_once()
    svc.es.update_last_indexed_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_index_all_patents_batch_processing(mock_patent):
    session = AsyncMock()

    patents = [mock_patent] * 1500
    for i, p in enumerate(patents):
        p.id = i + 1

    svc = PatentIndexingService(session)

    svc.es = MagicMock()
    svc.es.create_index_if_not_exists = AsyncMock()
    svc.es.create_meta_index_if_not_exists = AsyncMock()
    svc.es.get_last_indexed_id = AsyncMock(return_value=0)
    svc.es.bulk_index = AsyncMock()
    svc.es.update_last_indexed_id = AsyncMock()
    svc.es.close = AsyncMock()

    svc.find_not_indexed_patents = AsyncMock(return_value=patents)
    svc.documents_limit = 1000
    
    svc.hdfs = MagicMock()
    svc.hdfs.read_file = MagicMock(return_value="Full text content")
    
    svc.build_document = MagicMock(return_value={"patent_id": 1})

    await svc.index_all_patents()

    assert svc.es.bulk_index.call_count == 2
    svc.es.update_last_indexed_id.assert_called_once_with(1500)


@pytest.mark.asyncio
async def test_find_not_indexed_patients():
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.all = MagicMock(return_value=[MagicMock(), MagicMock()])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    session.execute = AsyncMock(return_value=mock_result)

    svc = PatentIndexingService(session)

    result = await svc.find_not_indexed_patents(100)

    assert len(result) == 2
    session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_find_not_indexed_patents_empty():
    session = AsyncMock()
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.all = MagicMock(return_value=[])
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    session.execute = AsyncMock(return_value=mock_result)

    svc = PatentIndexingService(session)

    result = await svc.find_not_indexed_patents(100)

    assert result == []


def test_build_document(mock_patent):
    session = AsyncMock()
    svc = PatentIndexingService(session)
    
    svc.hdfs = MagicMock()
    svc.hdfs.read_file = MagicMock(side_effect=["Abstract text", "Description text", "Claims text"])

    result = svc.build_document(mock_patent)

    assert result["patent_id"] == 1
    assert result["publication_number"] == "RU123456A"
    assert result["abstract"] == "Abstract text"
    assert result["description"] == "Description text"
    assert result["claims"] == "Claims text"
    assert svc.hdfs.read_file.call_count == 3


def test_build_document_with_inventors_and_classifications(mock_patent):
    session = AsyncMock()
    svc = PatentIndexingService(session)
    
    mock_inventor1 = MagicMock()
    mock_inventor1.full_name = "John Doe"
    mock_inventor2 = MagicMock()
    mock_inventor2.full_name = "Jane Smith"
    mock_patent.inventors = [mock_inventor1, mock_inventor2]
    
    mock_class1 = MagicMock()
    mock_class1.code = "G01N33/00"
    mock_class2 = MagicMock()
    mock_class2.code = "H04L29/06"
    mock_patent.classifications = [mock_class1, mock_class2]
    
    svc.hdfs = MagicMock()
    svc.hdfs.read_file = MagicMock(return_value="")

    result = svc.build_document(mock_patent)

    assert result["inventors"] == ["John Doe", "Jane Smith"]
    assert result["classifications"] == ["G01N33/00", "H04L29/06"]


@pytest.mark.asyncio
async def test_index_all_patents_handles_exception():
    session = AsyncMock()

    svc = PatentIndexingService(session)

    svc.es = MagicMock()
    svc.es.create_index_if_not_exists = AsyncMock(side_effect=Exception("ES error"))
    svc.es.close = AsyncMock()

    svc.find_not_indexed_patents = AsyncMock()

    with pytest.raises(Exception):
        await svc.index_all_patents()
