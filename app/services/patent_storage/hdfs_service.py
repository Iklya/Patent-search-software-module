from hdfs import InsecureClient

import os
from datetime import datetime
from app.core.logger import get_logger


logger = get_logger(__name__)


class HDFSService:
    """
    Используется для организации хранения текстов патентов в HDFS,
    чтения полнотекстовых данных и организации структуры хранения файлов
    """
    def __init__(self, user: str = "root"):
        url = os.getenv("HDFS_URL", "http://namenode:9870")
        self.client = InsecureClient(url, user=user)


    def store_fulltext(self, patent: dict):
        logger.debug("Сохранение полнотекстовых данных патента.")

        base_dir = self.build_base_dir(patent)

        abstract_path = self.write(
            f"{base_dir}/abstract.txt",
            patent.get("abstract"),
        )

        description_path = self.write(
            f"{base_dir}/description.txt",
            patent.get("description"),
        )

        claims_path = self.write(
            f"{base_dir}/claims.txt",
            patent.get("claims"),
        )

        return abstract_path, description_path, claims_path
    

    def build_base_dir(self, patent: dict):
        logger.debug(f"Сборка директории в HDFS для текущего патента.")

        pub_number = patent.get("publication_number")
        country = patent.get("country_code")

        pub_date = patent.get("publication_date")

        if pub_date:
            dt = datetime.fromisoformat(pub_date)
            year = dt.strftime("%Y")
            month = dt.strftime("%m")
        else:
            year = "unknown"
            month = "unknown"

        return f"/patents/{country}/{year}/{month}/{pub_number}"


    def write(self, path: str, text: str | None):
        logger.debug(f"Запись файла в HDFS: {path}")

        if not text:
            logger.warning(f"Пустой текст для записи: {path}")
            return None

        dir_path = os.path.dirname(path)
        self.client.makedirs(dir_path)

        if not self.client.status(path, strict=False):
            self.client.write(path, text, encoding="utf-8")

        return path

    
    def read_file(self, path: str) -> str:
        logger.debug(f"Чтение файла из HDFS: {path}")
        if not path:
            return ""

        with self.client.read(path, encoding="utf-8") as reader:
            return reader.read()
