import os

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from dotenv import load_dotenv

from app.services.keyword_extraction.postprocessing import KeywordPostProccessor


load_dotenv()


class KeywordExtractionError(Exception):
    pass


class KeywordExtractionService:
    def __init__(self) -> None:
        self.model_path: str = self.get_model_path()
        self.max_input_length: int = self.get_max_input_length()
        self.tokenizer = None
        self.model = None
        self.post_processor = KeywordPostProccessor()


    def extract_keywords(self, text: str) -> list[str]:
        self.ensure_model_loaded()

        inputs = self.prepare_inputs(text)
        output_tokens = self.generate_keywords(inputs)
        raw_keywords = self.decode_output(output_tokens)

        postprocessed_keywords = self.post_processor.process(raw_keywords)

        if not postprocessed_keywords:
            raise KeywordExtractionError("Недостаточно данных для извлечения ключевых фраз. Пожалуйста, введите более содержательный текст.")

        return postprocessed_keywords


    def get_model_path(self) -> str:
        model_path = os.getenv("MODEL_PATH")
        if not model_path:
            raise KeywordExtractionError("Переменая MODEL_PATH не определена.")
        
        if not os.path.exists(model_path):
            raise KeywordExtractionError(f"Путь модели не найден: {model_path}")
        
        return model_path


    def get_max_input_length(self) -> int:
        length_value = os.getenv("MAX_INPUT_LENGTH")
        if not length_value:
            raise KeywordExtractionError("Переменая MAX_INPUT_LENGTH не определена.")
        
        return int(length_value)


    def ensure_model_loaded(self) -> None:
        if self.model is None or self.tokenizer is None:
            self.load_model()
    

    def load_model(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_path,
            dtype=torch.float32
        )
        self.model.eval()
    

    def prepare_inputs(self, text: str) -> dict:
        return self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_input_length
        )
    
    
    def generate_keywords(self, inputs: dict) -> torch.Tensor:
        with torch.no_grad():
            return self.model.generate(
                **inputs,
                max_length=64,
                num_beams=5,
                early_stopping=True
            )
        
        
    def decode_output(self, tokens: torch.Tensor) -> list[str]:
        decoded_values = self.tokenizer.decode(
            tokens[0],
            skip_special_tokens=True
        )

        keywords = [phrase.strip() for phrase in decoded_values.split(";") if phrase.strip()]

        if not keywords:
            raise KeywordExtractionError("Недостаточно данных для извлечения ключевых фраз. Пожалуйста, введите более содержательный текст.")
        
        return keywords