INDEX_MAPPING = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "ru_analyzer": {
                                "type": "custom",
                                "tokenizer": "standard",
                                "filter": [
                                    "lowercase",
                                    "russian_stop",
                                    "russian_stemmer"
                                ]
                            }
                        },
                        "filter": {
                            "russian_stop": {
                                "type": "stop",
                                "stopwords": "_russian_"
                            },
                            "russian_stemmer": {
                                "type": "stemmer",
                                "language": "russian"
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "patent_id": {"type": "integer"},
                        "publication_number": {"type": "keyword"},
                        "application_number": {"type": "keyword"},
                        "country_code": {"type": "keyword"},
                        "kind_code": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "ru_analyzer"
                        },
                        "abstract": {
                            "type": "text",
                            "analyzer": "ru_analyzer"
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "ru_analyzer"
                        },
                        "claims": {
                            "type": "text",
                            "analyzer": "ru_analyzer"
                        },
                        "inventors": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "classifications": {
                            "type": "keyword"
                        },
                        "filing_date": {
                            "type": "date"
                        },
                        "publication_date": {
                            "type": "date"
                        }
                    }
                }
            }