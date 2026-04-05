import pytest
from bs4 import BeautifulSoup

from app.services.patent_collection.patent_preparation_service import ParserPreparationService


def test_extract_date():
    svc = ParserPreparationService()
    result = svc.extract_date("2024-01-05")
    assert result == "2024-01-05"


def test_extract_date_invalid():
    svc = ParserPreparationService()
    result = svc.extract_date("invalid")
    assert result is None


def test_extract_country_kind():
    svc = ParserPreparationService()
    country, kind = svc.extract_country_kind("RU123A")
    assert country == "RU"
    assert kind == "A"


def test_extract_country_kind_no_kind():
    svc = ParserPreparationService()
    country, kind = svc.extract_country_kind("RU123")
    assert country == "RU"
    assert kind == ""


def test_extract_country_kind_none():
    svc = ParserPreparationService()
    country, kind = svc.extract_country_kind(None)
    assert country is None
    assert kind is None


def test_extract_publication_number():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html>RU123456A</html>', 'lxml')
    result = svc.extract_publication_number(soup)
    assert result == "RU123456A"


def test_extract_publication_number_not_found():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html></html>', 'lxml')
    result = svc.extract_publication_number(soup)
    assert result is None


def test_extract_title():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<meta name="DC.title" content="Test Patent">', 'lxml')
    result = svc.extract_title(soup)
    assert result == "Test Patent"


def test_extract_title_not_found():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html></html>', 'lxml')
    result = svc.extract_title(soup)
    assert result is None


def test_extract_abstract():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<div class="abstract">Test abstract</div>', 'lxml')
    result = svc.extract_abstract(soup)
    assert result == "Test abstract"


def test_extract_abstract_not_found():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html></html>', 'lxml')
    result = svc.extract_abstract(soup)
    assert result is None


def test_extract_description():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<div class="description">Test description</div>', 'lxml')
    result = svc.extract_description(soup)
    assert result == "Test description"


def test_extract_description_not_found():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html></html>', 'lxml')
    result = svc.extract_description(soup)
    assert result is None


def test_extract_claims():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<div class="claims">Test claims</div>', 'lxml')
    result = svc.extract_claims(soup)
    assert result == "Test claims"


def test_extract_claims_not_found():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html></html>', 'lxml')
    result = svc.extract_claims(soup)
    assert result is None


def test_extract_application_number():
    svc = ParserPreparationService()
    html = '<application-timeline>Application RU2023123456</application-timeline>'
    soup = BeautifulSoup(html, 'lxml')
    result = svc.extract_application_number(soup)
    assert result == "RU2023123456"


def test_extract_application_number_not_found():
    svc = ParserPreparationService()
    soup = BeautifulSoup('<html></html>', 'lxml')
    result = svc.extract_application_number(soup)
    assert result is None


def test_extract_application_number_no_match():
    svc = ParserPreparationService()
    html = '<application-timeline>No application number here</application-timeline>'
    soup = BeautifulSoup(html, 'lxml')
    result = svc.extract_application_number(soup)
    assert result is None


def test_prepare_patent_json():
    svc = ParserPreparationService()
    html = """
    <html>
        <meta name="DC.title" content="Test Patent">
        <application-timeline></application-timeline>
    </html>
    """
    result = svc.prepare_patent_json(html, "http://test")
    assert result["title"] == "Test Patent"
    assert result["source_url"] == "http://test"
