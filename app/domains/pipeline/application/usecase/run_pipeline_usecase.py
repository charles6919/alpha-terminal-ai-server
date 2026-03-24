import asyncio
import logging
from datetime import datetime
from typing import Optional

from app.domains.pipeline.application.response.analysis_log_response import AnalysisLogResponse
from app.domains.pipeline.application.response.stock_summary_response import StockSummaryResponse
from app.domains.stock_analyzer.application.usecase.get_or_create_analysis_usecase import GetOrCreateAnalysisUseCase
from app.domains.stock_collector.application.usecase.collect_articles_usecase import CollectArticlesUseCase
from app.domains.stock_normalizer.application.request.normalize_raw_article_request import NormalizeRawArticleRequest
from app.domains.stock_normalizer.application.usecase.normalize_raw_article_usecase import NormalizeRawArticleUseCase

logger = logging.getLogger(__name__)

NEWS_SOURCE_TYPES = {"NEWS"}
REPORT_SOURCE_TYPES = {"DISCLOSURE", "REPORT"}


class RunPipelineUseCase:
    def __init__(
        self,
        watchlist_repository,
        raw_article_repository,
        collectors: list,
        normalize_usecase: NormalizeRawArticleUseCase,
        analysis_usecase: GetOrCreateAnalysisUseCase,
    ):
        self._watchlist_repository = watchlist_repository
        self._raw_article_repository = raw_article_repository
        self._collectors = collectors
        self._normalize_usecase = normalize_usecase
        self._analysis_usecase = analysis_usecase

    async def execute(self, selected_symbols: Optional[list[str]] = None, account_id: Optional[int] = None) -> dict:
        watchlist_items = self._watchlist_repository.find_all(account_id=account_id)
        if not watchlist_items:
            return {"message": "관심종목이 없습니다.", "processed": [], "summaries": [], "report_summaries": [], "logs": []}

        if selected_symbols:
            selected_set = {symbol.upper() for symbol in selected_symbols}
            watchlist_items = [item for item in watchlist_items if item.symbol.upper() in selected_set]
            if not watchlist_items:
                return {"message": "선택한 관심종목이 없습니다.", "processed": [], "summaries": [], "report_summaries": [], "logs": []}

        results = []
        summaries = []
        report_summaries = []
        logs = []

        for item in watchlist_items:
            symbol = item.symbol
            name = item.name

            collect_usecase = CollectArticlesUseCase(self._raw_article_repository, self._collectors)
            await asyncio.to_thread(collect_usecase.execute, symbol)

            raw_articles = self._raw_article_repository.find_all(symbol=symbol)
            if not raw_articles:
                results.append({"symbol": symbol, "skipped": True, "reason": "수집된 기사 없음"})
                continue

            # 뉴스와 공시·리포트 분리
            news_articles = [r for r in raw_articles if r.source_type in NEWS_SOURCE_TYPES]
            report_articles = [r for r in raw_articles if r.source_type in REPORT_SOURCE_TYPES]

            news_best = await self._analyze_best(news_articles[:3], symbol)
            report_best = await self._analyze_best(report_articles[:3], symbol)

            if news_best:
                analysis, source_type, url = news_best
                tags = [t.label for t in analysis.tags]
                summaries.append(StockSummaryResponse(
                    symbol=symbol, name=name,
                    summary=analysis.summary, tags=tags,
                    sentiment=analysis.sentiment,
                    sentiment_score=analysis.sentiment_score,
                    confidence=analysis.confidence,
                    source_type=source_type,
                    url=url,
                ))
                logs.append(AnalysisLogResponse(
                    analyzed_at=datetime.now(), symbol=symbol, name=name,
                    summary=analysis.summary, tags=tags,
                    sentiment=analysis.sentiment,
                    sentiment_score=analysis.sentiment_score,
                    confidence=analysis.confidence,
                    source_type=source_type,
                ))

            if report_best:
                analysis, source_type, url = report_best
                tags = [t.label for t in analysis.tags]
                report_summaries.append(StockSummaryResponse(
                    symbol=symbol, name=name,
                    summary=analysis.summary, tags=tags,
                    sentiment=analysis.sentiment,
                    sentiment_score=analysis.sentiment_score,
                    confidence=analysis.confidence,
                    source_type=source_type,
                    url=url,
                ))
                logs.append(AnalysisLogResponse(
                    analyzed_at=datetime.now(), symbol=symbol, name=name,
                    summary=analysis.summary, tags=tags,
                    sentiment=analysis.sentiment,
                    sentiment_score=analysis.sentiment_score,
                    confidence=analysis.confidence,
                    source_type=source_type,
                ))

            if news_best or report_best:
                results.append({"symbol": symbol, "skipped": False})
            else:
                results.append({"symbol": symbol, "skipped": True, "reason": "분석 실패"})

        return {
            "message": "파이프라인 완료",
            "processed": results,
            "summaries": summaries,
            "report_summaries": report_summaries,
            "logs": logs,
        }

    async def _analyze_best(self, raw_articles, symbol):
        """주어진 raw_article 목록에서 가장 높은 confidence의 분석 결과 반환"""
        best_analysis = None
        best_source_type = None
        best_url = None

        for raw in raw_articles:
            try:
                try:
                    published_at = datetime.fromisoformat(str(raw.published_at))
                except Exception:
                    published_at = datetime.now()

                normalized = await self._normalize_usecase.execute(NormalizeRawArticleRequest(
                    id=str(raw.id),
                    source_type=raw.source_type,
                    source_name=raw.source_name,
                    title=raw.title,
                    body_text=raw.body_text or raw.title,
                    published_at=published_at,
                    symbol=raw.symbol,
                    lang=raw.lang or "ko",
                ))

                analysis = await self._analysis_usecase.execute(normalized.id)

                if best_analysis is None or analysis.confidence > best_analysis.confidence:
                    best_analysis = analysis
                    best_source_type = raw.source_type
                    best_url = getattr(raw, "url", None)

            except Exception as e:
                logger.warning(f"[Pipeline] {symbol} 분석 실패: {e}")
                continue

        if best_analysis is None:
            return None
        return best_analysis, best_source_type, best_url
