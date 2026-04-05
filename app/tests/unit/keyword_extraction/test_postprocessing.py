import pytest

from app.services.keyword_extraction.postprocessing import KeywordPostProcessor


@pytest.fixture
def processor():
    return KeywordPostProcessor()


def test_clean_empty(processor):
    result = processor.clean_empty(["патент", "", " ", "поиск"])

    assert result == ["патент", "поиск"]


def test_remove_exact_duplicates(processor):
    result = processor.remove_exact_duplicates(["патент", "патент", "поиск"])

    assert result == ["патент", "поиск"]


def test_lemmatize(processor):
    lemma = processor.lemmatize("патенты")

    assert isinstance(lemma, str)
    assert len(lemma) > 0


def test_remove_morphological_duplicates(processor):
    phrases = ["патент", "патенты", "поиск"]

    result = processor.remove_morphological_duplicates(phrases)

    assert len(result) <= len(phrases)


def test_remove_nested_phrases(processor):
    phrases = [
        "машинное обучение",
        "обучение"
    ]

    result = processor.remove_nested_phrases(phrases)

    assert "машинное обучение" in result
    assert "обучение" not in result


def test_process_full_pipeline(processor):
    phrases = [
        "патент",
        "патенты",
        "",
        "поиск",
        "поиск",
        "машинное обучение",
        "обучение"
    ]

    result = processor.process(phrases)

    assert isinstance(result, list)
    assert len(result) > 0
