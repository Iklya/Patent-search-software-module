import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from elasticsearch import NotFoundError
from elasticsearch.exceptions import NotFoundError as ESNotFoundError

from app.services.patent_indexing.elasticsearch_service import ElasticsearchService
from app.services.patent_indexing.index_mapping import INDEX_MAPPING


@pytest.fixture
def es_service():
    with patch("app.services.patent_indexing.elasticsearch_service.AsyncElasticsearch") as mock_es:
        mock_client = AsyncMock()
        mock_es.return_value = mock_client
        service = ElasticsearchService()
        service.client = mock_client
        service.INDEX_MAPPING = INDEX_MAPPING
        yield service


@pytest.mark.asyncio
async def test_index_exists_true(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=True)

    result = await es_service.index_exists()

    assert result is True
    es_service.client.indices.exists.assert_called_once_with(index=es_service.index_name)


@pytest.mark.asyncio
async def test_index_exists_false(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=False)

    result = await es_service.index_exists()

    assert result is False
    es_service.client.indices.exists.assert_called_once_with(index=es_service.index_name)


@pytest.mark.asyncio
async def test_create_index_if_not_exists_creates(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=False)
    es_service.client.indices.create = AsyncMock()

    await es_service.create_index_if_not_exists()

    es_service.client.indices.create.assert_called_once_with(
        index=es_service.index_name,
        body=INDEX_MAPPING
    )


@pytest.mark.asyncio
async def test_create_index_if_not_exists_already_exists(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=True)
    es_service.client.indices.create = AsyncMock()

    await es_service.create_index_if_not_exists()

    es_service.client.indices.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_meta_index_if_not_exists_creates(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=False)
    es_service.client.indices.create = AsyncMock()

    await es_service.create_meta_index_if_not_exists()

    es_service.client.indices.create.assert_called_once_with(index=es_service.meta_index)


@pytest.mark.asyncio
async def test_create_meta_index_if_not_exists_already_exists(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=True)
    es_service.client.indices.create = AsyncMock()

    await es_service.create_meta_index_if_not_exists()

    es_service.client.indices.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_last_indexed_id_exists(es_service):
    mock_response = {"_source": {"last_indexed_patent_id": 123}}
    es_service.client.get = AsyncMock(return_value=mock_response)

    result = await es_service.get_last_indexed_id()

    assert result == 123
    es_service.client.get.assert_called_once_with(
        index=es_service.meta_index,
        id=es_service.meta_doc_id
    )


@pytest.mark.asyncio
async def test_get_last_indexed_id_not_found(es_service):
    es_service.client.get = AsyncMock(side_effect=NotFoundError("404", "Not Found", {}))

    result = await es_service.get_last_indexed_id()

    assert result == 0


@pytest.mark.asyncio
async def test_update_last_indexed_id(es_service):
    es_service.client.index = AsyncMock()

    await es_service.update_last_indexed_id(456)

    es_service.client.index.assert_called_once_with(
        index=es_service.meta_index,
        id=es_service.meta_doc_id,
        document={"last_indexed_patent_id": 456}
    )


@pytest.mark.asyncio
async def test_delete_index_both_exist(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=True)
    es_service.client.indices.delete = AsyncMock()

    await es_service.delete_index()

    assert es_service.client.indices.delete.call_count == 2
    es_service.client.indices.delete.assert_any_call(index=es_service.index_name)
    es_service.client.indices.delete.assert_any_call(index=es_service.meta_index)


@pytest.mark.asyncio
async def test_delete_index_none_exist(es_service):
    es_service.client.indices.exists = AsyncMock(return_value=False)
    es_service.client.indices.delete = AsyncMock()

    await es_service.delete_index()

    es_service.client.indices.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_index_only_patents_exists(es_service):
    async def exists_side_effect(index):
        return index == es_service.index_name
    
    es_service.client.indices.exists = AsyncMock(side_effect=exists_side_effect)
    es_service.client.indices.delete = AsyncMock()

    await es_service.delete_index()

    assert es_service.client.indices.delete.call_count == 1
    es_service.client.indices.delete.assert_called_once_with(index=es_service.index_name)


@pytest.mark.asyncio
async def test_bulk_index_success(es_service):
    es_service.client.bulk = AsyncMock()
    
    documents = [
        {"patent_id": 1, "title": "Patent 1"},
        {"patent_id": 2, "title": "Patent 2"}
    ]

    await es_service.bulk_index(documents)

    expected_operations = [
        {"index": {"_index": es_service.index_name, "_id": 1}},
        {"patent_id": 1, "title": "Patent 1"},
        {"index": {"_index": es_service.index_name, "_id": 2}},
        {"patent_id": 2, "title": "Patent 2"}
    ]
    
    es_service.client.bulk.assert_called_once_with(operations=expected_operations)


@pytest.mark.asyncio
async def test_bulk_index_empty_list(es_service):
    es_service.client.bulk = AsyncMock()

    await es_service.bulk_index([])

    es_service.client.bulk.assert_called_once_with(operations=[])


@pytest.mark.asyncio
async def test_bulk_index_exception(es_service):
    es_service.client.bulk = AsyncMock(side_effect=Exception("Bulk error"))
    
    documents = [{"patent_id": 1, "title": "Patent 1"}]

    with pytest.raises(Exception):
        await es_service.bulk_index(documents)


@pytest.mark.asyncio
async def test_close(es_service):
    es_service.client.close = AsyncMock()

    await es_service.close()

    es_service.client.close.assert_called_once()
