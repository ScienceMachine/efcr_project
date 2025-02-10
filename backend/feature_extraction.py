from dataclasses import dataclass
from .efcr_api_utils import Chapter


class IntFeatureExtractor:

    def extract(self, chapter: Chapter) -> int:
        raise NotImplementedError


class WordCountExtractor(IntFeatureExtractor):

    def _get_one_paragraph_word_count(self, paragraph: str) -> int:
        raise NotImplementedError

    def extract(self, chapter: Chapter) -> int:
        return sum(self._get_one_paragraph_word_count(x) for x in chapter.paragraphs)


@dataclass
class ChapterFeatures:
    word_count: int

    @classmethod
    def from_chapter(cls, chapter: Chapter) -> "ChapterFeatures":
        return cls(word_count=WordCountExtractor().extract(chapter=chapter))
