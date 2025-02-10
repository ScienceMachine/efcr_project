from dataclasses import dataclass
from typing import List, Dict, Union

import requests


BASE_URL = "https://www.ecfr.gov/"


@dataclass
class CfrReference:
    title: int
    chapter: str  # NB: can be Arabic or Roman numeral (seems not to matter, just request whichever is provided)


@dataclass
class Agency:
    name: str
    short_name: str
    cfr_references: List[CfrReference]

    @classmethod
    def from_json(cls, json_response: Dict[str, Union[str, int]]) -> "Agency":
        raise NotImplementedError


@dataclass
class Chapter:
    paragraphs: List[str]
    # other metadata

    @classmethod
    def from_response(cls, response: requests.Response) -> "Chapter":
        raise NotImplementedError


def get_agencies() -> List[Agency]:
    raise NotImplementedError


def get_chapter_api_response(title: int, chapter: str, date: str) -> requests.Response:
    raise NotImplementedError
