import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

import requests
from lxml import etree


BASE_URL = "https://www.ecfr.gov/"


@dataclass
class CfrReference:
    title: int
    chapter: Optional[
        str
    ]  # NB: can be Arabic or Roman numeral (seems not to matter, just request whichever is provided)
    subtitle: Optional[str]
    subchapter: Optional[str]
    part: Optional[str]
    subpart: Optional[str]
    section: Optional[str]
    appendix: Optional[str]

    @classmethod
    def from_json(cls, json_list: List[Dict[str, Any]]) -> List["CfrReference"]:
        result = []
        for d in json_list:
            result.append(
                cls(
                    title=d["title"],
                    chapter=d.get("chapter"),
                    subtitle=d.get("subtitle"),
                    subchapter=d.get("subchapter"),
                    part=d.get("part"),
                    subpart=d.get("subpart"),
                    section=d.get("section"),
                    appendix=d.get("appendix"),
                )
            )
        return result

    @property
    def query_params(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class Agency:
    name: str
    short_name: str
    cfr_references: List[CfrReference]

    @classmethod
    def from_json(cls, json_response: Dict[str, Any]) -> "Agency":
        return cls(
            name=json_response["name"],
            short_name=json_response["short_name"],
            cfr_references=CfrReference.from_json(json_response["cfr_references"]),
        )


@dataclass
class Regulation:
    paragraphs: List[str]
    # other metadata

    @classmethod
    def from_response(cls, response: requests.Response) -> "Regulation":
        """
        Currently dumb approach to get all text in <P></P> xml tags in
        a given chapter, not yet robust to differences in tags between
        different titles/chapters/etc.

        Also currently ignores headings and other potentially useful
        metadata
        """
        root = etree.fromstring(response.content)
        paragraph_tags = root.xpath("//P")
        paragraph_texts = []
        for paragraph_tag in paragraph_tags:
            text = paragraph_tag.text
            if text:
                text = text.strip()
                text = re.sub(r"\s+", " ", text)
                if text:  # skip empty strings
                    paragraph_texts.append(text)
        return cls(paragraphs=paragraph_texts)


def get_agencies() -> List[Agency]:
    agencies_endpoint = "/api/admin/v1/agencies.json"
    url = urljoin(BASE_URL, agencies_endpoint)
    r = requests.get(url)
    full_json = r.json()
    return [Agency.from_json(d) for d in full_json["agencies"]]


def get_regulation(reference: CfrReference, date: str) -> Regulation:
    """
    Get the XML response for a full title & chapter in ecfr_api_utils

    date is in YYYY-MM-DD format
    """
    full_xml_endpoint = f"/api/versioner/v1/full/{date}/title-{reference.title}.xml"
    url = urljoin(BASE_URL, full_xml_endpoint)
    params = reference.query_params
    r = requests.get(url, params=params)
    return Regulation.from_response(response=r)
