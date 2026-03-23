from enum import Enum


class SearchMode(str, Enum):
    AND = "AND"
    OR = "OR"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"