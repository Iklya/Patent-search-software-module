import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from app.core.logger import get_logger
from app.core.settings import settings
from app.services.keyword_extraction.postprocessing import KeywordPostProcessor


logger = get_logger(__name__)


class KeywordExtractionException(Exception):
    """
    Используется для возврата HTTP 400 (бизнес-ошибок извлечения ключевых фраз)
    """
    pass


class KeywordExtractionService:
    """
    Используется для реализации бизнес-логики, связанной с
    извлечением ключевых фраз из текстовых данных
    """
    def __init__(self) -> None:
        self.model_path = settings.model_path
        self.max_input_length = settings.max_user_input_length

        self.max_chunks = settings.max_chunks
        self.chunk_overlap_ratio = settings.chunk_overlap_ratio

        self.generation_max_length = settings.generation_max_length
        self.generation_num_beams = settings.generation_num_beams
        self.generation_no_repeat_ngram_size = settings.generation_no_repeat_ngram_size

        self.tokenizer = None
        self.model = None

        self.post_processor = KeywordPostProcessor()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        logger.info(f"Устройство для работы с моделью выбрано: {self.device}")
    

    def extract_keywords(self, text: str) -> list[str]:
        logger.info("Запущено извлечение ключевых фраз.")

        self.validate_text_content(text)
        self.ensure_model_loaded()

        chunks = self.split_into_chunks(text)

        all_keywords = []

        for chunk in chunks:
            try:
                keywords = self.extract_keywords_from_chunk(chunk)
                all_keywords.extend(keywords)

            except KeywordExtractionException:
                logger.warning("Модель не извлекла ключевые фразы из чанка.")

        postprocessed_keywords = self.post_processor.process(all_keywords)

        logger.debug(f"Ключевые фразы после постобработки: {postprocessed_keywords}")

        if not postprocessed_keywords:
            logger.exception("После постобработки не осталось ключевых фраз.")
            raise KeywordExtractionException(
                "Недостаточно данных для извлечения ключевых фраз. "
                "Пожалуйста, введите более содержательный текст."
            )

        logger.info(f"Извлечено ключевых фраз: {len(postprocessed_keywords)}")

        return postprocessed_keywords
    

    def validate_text_content(self, text: str) -> None:
        if not any(char.isalpha() for char in text):
            logger.exception("Текст не содержит буквенных символов.")
            raise KeywordExtractionException("Текст не содержит информативных данных.")


    def ensure_model_loaded(self) -> None:
        if self.model is None or self.tokenizer is None:
            logger.warning("Модель не загружена. Выполняется загрузка.")
            self.load_model()
    

    def load_model(self) -> None:
        try:
            logger.info("Загрузка токенизатора и модели.")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
            self.model.to(self.device)
            self.model.eval()

            logger.info("Модель успешно загружена.")

        except Exception as e:
            logger.exception("Не удалось загрузить модель.")
            raise RuntimeError(f"Ошибка загрузки модели: {e}")
    

    
    def split_into_chunks(self, text: str) -> list[str]:
        tokens = self.tokenizer.encode(text, add_special_tokens=False)

        max_len = self.max_input_length
        overlap = int(max_len * self.chunk_overlap_ratio)

        chunks = []

        start = 0
        while start < len(tokens) and len(chunks) < self.max_chunks:
            end = start + max_len
            chunk_tokens = tokens[start:end]

            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

            start += max_len - overlap

        logger.debug(f"Текст разбит на чанки: {len(chunks)}")

        return chunks
    

    def extract_keywords_from_chunk(self, text: str) -> list[str]:
        inputs = self.prepare_inputs(text)
        output_tokens = self.generate_keywords(inputs)

        return self.decode_output(output_tokens)
    

    def prepare_inputs(self, text: str) -> dict:
        logger.debug("Токенизация входного текста.")

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_input_length
            )
            return {k: v.to(self.device) for k, v in inputs.items()}
        
        except Exception as e:
            logger.exception("Произошла ошибка токенизации.")
            raise RuntimeError(f"Ошибка токенизации: {e}")
    
    
    def generate_keywords(self, inputs: dict) -> torch.Tensor:
        logger.debug("Генерация ключевых фраз моделью.")

        try:
            with torch.no_grad():
                return self.model.generate(
                    **inputs,
                    max_length=self.generation_max_length,
                    num_beams=self.generation_num_beams,
                    no_repeat_ngram_size=self.generation_no_repeat_ngram_size,
                    early_stopping=True
                )
        
        except Exception as e:
            logger.exception("Произошла ошибка генерации.")
            raise RuntimeError(f"Ошибка генерации: {e}")            
        
        
    def decode_output(self, tokens: torch.Tensor) -> list[str]:
        try:
            decoded_values = self.tokenizer.decode(
                tokens[0],
                skip_special_tokens=True
            )

            logger.debug(f"Декодированный вывод модели: {decoded_values}")

            keywords = [phrase.strip() for phrase in decoded_values.split(";") if phrase.strip()]

            if not keywords:
                logger.exception("Модель не вернула ключевые фразы.")
                raise KeywordExtractionException(
                    "Недостаточно данных для извлечения ключевых фраз. "
                    "Пожалуйста, введите более содержательный текст."
                )
            
            return keywords
        
        except KeywordExtractionException:
            raise

        except Exception as e:
            logger.exception("Ошибка декодирования ключевых фраз.")
            raise RuntimeError(f"Ошибка декодирования: {e}")
