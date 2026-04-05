from app.services.keyword_extraction.patent_text_builder import PatentTextBuilder


def test_build_text():
    builder = PatentTextBuilder()

    patent = {
        "title": "Название",
        "abstract": "Аннотация",
        "claims": "Формула",
        "description": "Описание"
    }

    text = builder.build(patent)

    assert "Название" in text


def test_truncate():
    builder = PatentTextBuilder()
    builder.max_text_length = 10

    patent = {
        "title": "Очень длинный текст патента"
    }

    text = builder.build(patent)

    assert len(text) <= 10
