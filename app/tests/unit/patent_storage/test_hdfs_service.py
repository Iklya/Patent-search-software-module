from datetime import datetime

import pytest
from unittest.mock import MagicMock, patch

from app.services.patent_storage.hdfs_service import HDFSService


def test_build_base_dir_with_date():
    svc = HDFSService()

    patent = {
        "publication_number": "RU123456A",
        "country_code": "RU",
        "publication_date": "2023-01-05"
    }

    path = svc.build_base_dir(patent)

    assert path == "/patents/RU/2023/01/RU123456A"


def test_build_base_dir_without_date():
    svc = HDFSService()

    patent = {
        "publication_number": "US9876543B",
        "country_code": "US",
        "publication_date": None
    }

    path = svc.build_base_dir(patent)

    assert path == "/patents/US/unknown/unknown/US9876543B"


def test_build_base_dir_missing_fields():
    svc = HDFSService()

    patent = {
        "publication_number": "EP123456"
    }

    path = svc.build_base_dir(patent)

    assert path == "/patents/None/unknown/unknown/EP123456"


def test_write_success():
    svc = HDFSService()
    svc.client = MagicMock()
    svc.client.makedirs = MagicMock()
    svc.client.status = MagicMock(return_value=False)
    svc.client.write = MagicMock()

    result = svc.write("/test/path/file.txt", "test content")

    assert result == "/test/path/file.txt"
    svc.client.makedirs.assert_called_once_with("/test/path")
    svc.client.status.assert_called_once_with("/test/path/file.txt", strict=False)
    svc.client.write.assert_called_once_with("/test/path/file.txt", "test content", encoding="utf-8")


def test_write_empty_text():
    svc = HDFSService()
    svc.client = MagicMock()

    result = svc.write("/test/path/file.txt", None)

    assert result is None
    svc.client.write.assert_not_called()


def test_write_file_exists():
    svc = HDFSService()
    svc.client = MagicMock()
    svc.client.makedirs = MagicMock()
    svc.client.status = MagicMock(return_value=True)
    svc.client.write = MagicMock()

    result = svc.write("/test/path/file.txt", "test content")

    assert result == "/test/path/file.txt"
    svc.client.write.assert_not_called()


def test_read_file_success():
    svc = HDFSService()
    svc.client = MagicMock()
    mock_reader = MagicMock()
    mock_reader.read.return_value = "file content"
    svc.client.read.return_value.__enter__.return_value = mock_reader

    result = svc.read_file("/test/path/file.txt")

    assert result == "file content"
    svc.client.read.assert_called_once_with("/test/path/file.txt", encoding="utf-8")


def test_read_file_empty_path():
    svc = HDFSService()

    result = svc.read_file("")

    assert result == ""


def test_read_file_none_path():
    svc = HDFSService()

    result = svc.read_file(None)

    assert result == ""


def test_store_fulltext_success():
    svc = HDFSService()
    svc.build_base_dir = MagicMock(return_value="/patents/RU/2023/01/RU123")
    svc.write = MagicMock(side_effect=["/path/abstract.txt", "/path/description.txt", "/path/claims.txt"])

    patent = {
        "publication_number": "RU123",
        "country_code": "RU",
        "publication_date": "2023-01-05",
        "abstract": "abstract text",
        "description": "description text",
        "claims": "claims text"
    }

    abstract_path, description_path, claims_path = svc.store_fulltext(patent)

    assert abstract_path == "/path/abstract.txt"
    assert description_path == "/path/description.txt"
    assert claims_path == "/path/claims.txt"
    svc.build_base_dir.assert_called_once_with(patent)
    assert svc.write.call_count == 3


def test_store_fulltext_missing_fields():
    svc = HDFSService()
    svc.build_base_dir = MagicMock(return_value="/patents/RU/2023/01/RU123")
    svc.write = MagicMock(return_value=None)

    patent = {
        "publication_number": "RU123",
        "country_code": "RU",
        "publication_date": "2023-01-05"
    }

    abstract_path, description_path, claims_path = svc.store_fulltext(patent)

    assert abstract_path is None
    assert description_path is None
    assert claims_path is None
