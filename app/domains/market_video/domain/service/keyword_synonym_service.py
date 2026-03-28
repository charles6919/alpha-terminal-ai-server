from collections import Counter

from app.domains.market_video.domain.service.synonym_table import SYNONYM_GROUPS


class KeywordSynonymService:
    """동의어/유사어를 대표 키워드로 통합하는 Domain Service."""

    def __init__(self) -> None:
        self._mapping: dict[str, str] = {}
        for representative, synonyms in SYNONYM_GROUPS.items():
            for synonym in synonyms:
                self._mapping[synonym] = representative

    def normalize(self, noun: str) -> str:
        return self._mapping.get(noun, noun)

    def merge(self, counter: Counter[str]) -> Counter[str]:
        merged: Counter[str] = Counter()
        for noun, count in counter.items():
            merged[self.normalize(noun)] += count
        return merged
