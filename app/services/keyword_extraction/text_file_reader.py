from fastapi import status, HTTPException, UploadFile

from app.core.logger import get_logger
from app.core.settings import settings


logger = get_logger(__name__)


class TextFileReader:
    """
    Используется для валидации и чтения входного текстового файла.
    """
    def __init__(self):
        self.max_text_length = settings.file_text_max_length


    async def read(self, file: UploadFile) -> str:
        self.validate_extension(file)

        content = await self.read_content(file)

        self.validate_not_empty(content)

        text = self.decode_content(content)

        return self.truncate_text(text)


    def validate_extension(self, file: UploadFile) -> None:
        if not file.filename or not file.filename.endswith(".txt"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Разрешены только .txt файлы."
            )


    async def read_content(self, file: UploadFile) -> bytes:
        try:
            return await file.read()
        except Exception:
            logger.exception("Ошибка чтения файла.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось прочитать файл."
            )


    def validate_not_empty(self, content: bytes) -> None:
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл пуст."
            )


    def decode_content(self, content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Файл должен быть в кодировке UTF-8."
            )


    def truncate_text(self, text: str) -> str:
        return text[:self.max_text_length]
