import pytest
from fastapi import UploadFile
from io import BytesIO

from app.services.keyword_extraction.text_file_reader import TextFileReader


@pytest.fixture
def reader():
    return TextFileReader()


@pytest.mark.asyncio
async def test_read_valid_file(reader):

    file = UploadFile(
        filename="test.txt",
        file=BytesIO(b"test text")
    )

    text = await reader.read(file)

    assert text == "test text"


@pytest.mark.asyncio
async def test_invalid_extension(reader):

    file = UploadFile(
        filename="test.pdf",
        file=BytesIO(b"text")
    )

    with pytest.raises(Exception):
        await reader.read(file)


@pytest.mark.asyncio
async def test_empty_file(reader):

    file = UploadFile(
        filename="test.txt",
        file=BytesIO(b"")
    )

    with pytest.raises(Exception):
        await reader.read(file)


def test_truncate_text(reader):
    reader.max_text_length = 5

    result = reader.truncate_text("123456789")

    assert result == "12345"
