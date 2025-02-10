from dataclasses import dataclass
from functools import lru_cache
from typing import List

import requests

from .ecfr_api_utils import Regulation, Agency, get_regulation


class IntFeatureExtractor:

    def extract(self, regulation: Regulation) -> int:
        raise NotImplementedError


class WordCountExtractor(IntFeatureExtractor):

    def _get_one_paragraph_word_count(self, paragraph: str) -> int:
        """
        Dumb approach of counting words as text w/ spaces, can improve
        w/ NLP (e.g. simple way would be using spacy)
        """
        return len(paragraph.split(" "))

    def extract(self, regulation: Regulation) -> int:
        return sum(self._get_one_paragraph_word_count(x) for x in regulation.paragraphs)


class DeiWordCountExtractor(IntFeatureExtractor):

    def extract(self, regulation: Regulation) -> int:
        raise NotImplementedError


@dataclass
class RegulationFeatures:
    word_count: int

    @classmethod
    def from_regulation(cls, regulation: Regulation) -> "RegulationFeatures":
        return cls(word_count=WordCountExtractor().extract(regulation=regulation))


@dataclass
class AgencyFeatures:
    word_count: int

    @classmethod
    def from_regulation_features(
        cls, regulation_features: List[RegulationFeatures]
    ) -> "AgencyFeatures":
        word_count = sum(x.word_count for x in regulation_features)
        return cls(word_count=word_count)


def get_agency_features(agency: Agency, date: str) -> AgencyFeatures:
    # regulations = []
    regulation_features = []
    for cfr_reference in agency.cfr_references:
        regulation = get_regulation(reference=cfr_reference, date=date)
        regulation_features.append(
            RegulationFeatures.from_regulation(regulation=regulation)
        )
    return AgencyFeatures.from_regulation_features(regulation_features)
