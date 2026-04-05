import pytest
from pydantic import ValidationError

from app.core.settings import Settings


MODEL_FIELDS = list(Settings.model_fields.keys())

REQUIRED_ENV_VARS = [field.upper() for field in MODEL_FIELDS]


@pytest.mark.parametrize("env_var", REQUIRED_ENV_VARS)
def test_each_required_env_variable(monkeypatch, env_var):
    monkeypatch.delenv(env_var, raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_all_required_env_variables_present():
    settings = Settings()

    for field in MODEL_FIELDS:
        value = getattr(settings, field)

        assert value is not None, f"{field} is None"

        if isinstance(value, str):
            assert value.strip() != "", f"{field} is empty string"


def test_env_variable_types():
    settings = Settings()

    int_fields = [
        "max_chunks",
        "generation_max_length",
        "generation_num_beams",
        "generation_no_repeat_ngram_size",
        "max_user_input_length",
        "google_patent_text_max_length",
        "file_text_max_length",
        "google_patents_max_pages",
        "google_patents_results_per_page",
        "playwright_page_load_timeout",
        "playwright_selector_timeout",
        "playwright_scroll_wait",
        "playwright_patent_timeout",
        "playwright_scroll_iterations",
        "playwright_scroll_wait_after",
        "indexing_batch_size",
        "max_result_window",
    ]

    for field in int_fields:
        value = getattr(settings, field)
        assert isinstance(value, int), f"{field} must be int"
        assert value > 0, f"{field} must be > 0"

    float_fields = ["chunk_overlap_ratio"]

    for field in float_fields:
        value = getattr(settings, field)
        assert isinstance(value, float), f"{field} must be float"
        assert 0 <= value <= 1, f"{field} must be in [0, 1]"


def test_string_fields_not_empty():
    settings = Settings()

    string_fields = [
        "database_url",
        "hdfs_url",
        "model_path",
        "google_patents_base_url",
        "elasticsearch_url",
    ]

    for field in string_fields:
        value = getattr(settings, field)
        assert isinstance(value, str), f"{field} must be string"
        assert value.strip() != "", f"{field} must not be empty"


def test_settings_instantiation_from_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    monkeypatch.setenv("HDFS_URL", "http://test")
    monkeypatch.setenv("MODEL_PATH", "model")

    settings = Settings()

    assert settings.database_url == "postgresql://test"
    assert settings.hdfs_url == "http://test"
    assert settings.model_path == "model"
