from collections import Counter
from typing import Dict, List

from app.domains.market_video.domain.service.keyword_synonym_service import KeywordSynonymService


class NounExtractionService:
    """명사 필터링, 동의어 통합, 빈도 집계 — 순수 Python 비즈니스 로직."""

    MIN_NOUN_LENGTH = 2

    def __init__(self) -> None:
        self._synonym_service = KeywordSynonymService()

    def filter_nouns(self, nouns: List[str]) -> List[str]:
        """의미 없는 단어 제거."""
        return [n for n in nouns if len(n) >= self.MIN_NOUN_LENGTH]

    def count_frequencies(self, nouns: List[str]) -> Dict[str, int]:
        """동의어 통합 후 빈도수 내림차순 정렬된 dict 반환."""
        raw_counter = Counter(nouns)
        merged = self._synonym_service.merge(raw_counter)
        return dict(merged.most_common())
