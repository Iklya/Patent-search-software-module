from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

from app.core.logger import get_logger


logger = get_logger(__name__)


class ParserPreparationService:
    """
    Используется для автоматизированного сбора информации об определённом патенте
    """
    def prepare_patent_json(self, html: str, source_url: str):
        logger.debug(f"Подготовка данных патента: {source_url}")
        soup = BeautifulSoup(html, "lxml")

        pub_number = self.extract_publication_number(soup)
        country_code, kind_code = self.extract_country_kind(pub_number)

        timeline_dates = self.extract_dates_from_timeline(soup, pub_number)
        filing_date = (timeline_dates['filing_date'])
        publication_date = (timeline_dates['publication_date'])

        return {
            "publication_number": pub_number,
            "application_number": self.extract_application_number(soup),
            "title": self.extract_title(soup),
            "country_code": country_code,
            "kind_code": kind_code,
            "filing_date": filing_date,
            "publication_date": publication_date,
            "inventors": self.extract_inventors(soup),
            "classifications": self.extract_classifications(soup),
            "abstract": self.extract_abstract(soup),
            "claims": self.extract_claims(soup),
            "description": self.extract_description(soup),
            "source_url": source_url,
            "parsed_at": datetime.now().isoformat()
        }
     

    def extract_publication_number(self, soup):
        m = re.search(r'\b([A-Z]*\d+[A-Z0-9]*)\b', soup.get_text())
        if m:
            return m.group(1)
        
        return None
    
    
    def extract_country_kind(self, publication_number):
        if not publication_number:
            logger.warning("Не удалось извлечь publication_number")
            return None, None
        
        m = re.match(r'^([A-Z]*)(\d+)([A-Z0-9]*)?$', publication_number)
        if m:
            return m.group(1), m.group(3)

        return None, None


    def extract_dates_from_timeline(self, soup, pub_number):
        dates = {'filing_date': None, 'publication_date': None}
        timeline = soup.find("application-timeline")
        if not timeline:
            return dates

        events = timeline.find_all("div", class_="event")
        for event in events:
            date_span = event.find(["div"], class_=["filed", "publication", "granted"])
            if not date_span:
                continue
            
            date_text = date_span.get_text(strip=True)
            date = self.extract_date(date_text)
            if not date:
                continue

            title_div = event.find("div", class_="title")
            if not title_div:
                continue

            title_text = title_div.get_text(strip=True).lower()
            if 'filed' in title_text:
                dates['filing_date'] = date

            if any(w in title_text for w in [f'publication of {pub_number.lower()}', 'granted']):
                dates['publication_date'] = date

        return dates
    

    def extract_date(self, text: str) -> str | None:
        if not text:
            return None

        m = re.search(r'(\d{4})-(\d{2})-(\d{2})', text.strip())
        if m:
            y, mth, d = m.groups()
            return f"{y}-{mth.zfill(2)}-{d.zfill(2)}"
        
        return None


    def extract_title(self, soup):
        t = soup.find("meta", {"name": "DC.title"})
        if t:
            return t["content"].strip()
        
        return None


    def extract_inventors(self, soup):
        inventors = []

        dl = soup.find("dl", class_="important-people")
        if not dl:
            return inventors

        inventor_dt = None
        for dt in dl.find_all("dt"):
            text = dt.get_text(strip=True).lower()
            if "inventor" in text:
                inventor_dt = dt
                break

        if inventor_dt:
            current = inventor_dt.next_sibling
            while current:
                if current.name == "dt":
                    break

                if current.name == "dd":
                    name_tag = current.find("a") or current
                    name = name_tag.get_text(strip=True)
                    if name and name not in inventors:
                        inventors.append(name)

                current = current.next_sibling

        return inventors


    def extract_application_number(self, soup):
        timeline = soup.find("application-timeline")

        if timeline:
            text = timeline.get_text(" ", strip=True)
            m = re.search(r'Application\s+([A-Z]*\d+[A-Z0-9/]*)', text, re.IGNORECASE)
            if m:
                return m.group(1)

        return None
        
    # TODO: переделать выбор классификаций
    def extract_classifications(self, soup):
        cls = []

        main = soup.select("classification-tree state-modifier")
        if not main:
            return cls

        for m in main:
            code = m.get("data-cpc")
            if code and code not in cls:
                cls.append(code.strip())

        return sorted(cls)


    def extract_abstract(self, soup):
        tag = soup.find(["div"], class_="abstract")
        if tag:
            return tag.get_text(" ", strip=True)
        
        return None


    def extract_description(self, soup):
        tag = soup.find(["div"], class_="description")
        if tag:
            return tag.get_text(" ", strip=True)
        
        return None


    def extract_claims(self, soup):
        tag = soup.find(["div"], class_="claims")
        if tag:
            return tag.get_text(" ", strip=True)
        
        return None
