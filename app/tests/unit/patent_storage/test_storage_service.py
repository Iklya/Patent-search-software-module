from datetime import datetime

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.patent_storage.patent_storage_service import PatentStorageService
from app.models.patents import Patent


@pytest.mark.asyncio
async def test_store_patents_success():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    svc = PatentStorageService(session)

    svc.hdfs = MagicMock()
    svc.hdfs.store_fulltext = MagicMock(return_value=("/abstract.txt", "/claims.txt", "/description.txt"))

    svc.pg = MagicMock()
    svc.pg.get_or_create_inventor = AsyncMock(return_value=MagicMock())
    svc.pg.get_or_create_classification = AsyncMock(return_value=MagicMock())
    svc.pg.get_or_create_citation = AsyncMock(return_value=MagicMock())

    patents = [
        {
            "publication_number": "RU123456A",
            "application_number": "RU2023123456",
            "title": "Test Patent",
            "country_code": "RU",
            "kind_code": "A",
            "filing_date": "2023-01-01",
            "publication_date": "2023-06-01",
            "inventors": ["Ivan Ivanov", "Petr Petrov"],
            "classifications": ["G01N33/00", "H04L29/06"],
            "citations": ["US1234567B", "EP9876543A"],
            "abstract": "abstract text",
            "claims": "claims text",
            "description": "description text",
            "concepts": ["concept1", "concept2"],
            "source_url": "https://patents.google.com/patent/RU123456A",
            "parsed_at": "2024-01-01T00:00:00"
        }
    ]

    await svc.store_patents(patents)

    assert session.add.call_count == 1
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_patents_empty_list():
    session = MagicMock()
    session.commit = AsyncMock()

    svc = PatentStorageService(session)

    await svc.store_patents([])

    session.commit.assert_awaited_once()
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_store_patents_without_publication_number():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    svc = PatentStorageService(session)
    svc.hdfs = MagicMock()
    svc.pg = MagicMock()

    patents = [
        {
            "title": "No Publication Number",
            "country_code": "RU"
        }
    ]

    await svc.store_patents(patents)

    session.add.assert_not_called()
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_patents_with_none_dates():
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    svc = PatentStorageService(session)

    svc.hdfs = MagicMock()
    svc.hdfs.store_fulltext = MagicMock(return_value=(None, None, None))

    svc.pg = MagicMock()
    svc.pg.get_or_create_inventor = AsyncMock(return_value=MagicMock())
    svc.pg.get_or_create_classification = AsyncMock(return_value=MagicMock())
    svc.pg.get_or_create_citation = AsyncMock(return_value=MagicMock())

    patents = [
        {
            "publication_number": "RU123456A",
            "application_number": "RU2023123456",
            "title": "Test Patent",
            "country_code": "RU",
            "kind_code": "A",
            "filing_date": None,
            "publication_date": None,
            "inventors": [],
            "classifications": [],
            "citations": [],
            "abstract": None,
            "claims": None,
            "description": None,
            "concepts": [],
            "source_url": "https://patents.google.com/patent/RU123456A"
        }
    ]

    await svc.store_patents(patents)

    assert session.add.call_count == 1
    session.commit.assert_awaited_once()


def test_parse_date_valid():
    session = MagicMock()
    svc = PatentStorageService(session)

    result = svc.parse_date("2023-12-25")

    assert result == datetime(2023, 12, 25).date()


def test_parse_date_none():
    session = MagicMock()
    svc = PatentStorageService(session)

    result = svc.parse_date(None)

    assert result is None


def test_parse_date_empty_string():
    session = MagicMock()
    svc = PatentStorageService(session)

    result = svc.parse_date("")

    assert result is None
