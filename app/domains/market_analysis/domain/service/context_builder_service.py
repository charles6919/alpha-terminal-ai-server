from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WatchlistContext:
    symbol: str
    name: str
    themes: list[str] = field(default_factory=list)


class ContextBuilderService:
    """관심종목·테마·사용자 프로필을 LangChain 프롬프트 컨텍스트 문자열로 조합하는 Domain Service."""

    def build(self, stocks: list[WatchlistContext], user_profile: Optional[object] = None) -> str:
        lines = []

        # BL-BE-56: 사용자 프로필이 있으면 컨텍스트 상단에 추가 (빈 필드 생략)
        # BL-BE-81: getattr로 안전한 속성 접근 (AttributeError → 500 방지)
        if user_profile:
            profile_lines = []
            if getattr(user_profile, 'investment_style', ''):
                profile_lines.append(f"- 투자 스타일: {user_profile.investment_style}")
            if getattr(user_profile, 'risk_tolerance', ''):
                profile_lines.append(f"- 위험 허용도: {user_profile.risk_tolerance}")
            preferred_sectors = getattr(user_profile, 'preferred_sectors', [])
            if preferred_sectors:
                profile_lines.append(f"- 관심 섹터: {', '.join(preferred_sectors)}")
            if getattr(user_profile, 'analysis_preference', ''):
                profile_lines.append(f"- 분석 선호: {user_profile.analysis_preference}")
            keywords_of_interest = getattr(user_profile, 'keywords_of_interest', [])
            if keywords_of_interest:
                profile_lines.append(f"- 관심 키워드: {', '.join(keywords_of_interest)}")
            preferred_stocks = getattr(user_profile, 'preferred_stocks', [])
            if preferred_stocks:
                profile_lines.append(f"- 관심 종목: {', '.join(preferred_stocks)}")
            if getattr(user_profile, 'interests_text', ''):
                profile_lines.append(f"- 관심사: {user_profile.interests_text}")
            if profile_lines:
                lines.append("[사용자 투자 성향]")
                lines.extend(profile_lines)
                lines.append("")

        if not stocks:
            lines.append("사용자의 관심종목이 없습니다.")
            return "\n".join(lines)

        lines.append("[사용자 관심종목 및 테마]")
        for stock in stocks:
            themes_str = ", ".join(stock.themes) if stock.themes else "테마 정보 없음"
            lines.append(f"- {stock.name} ({stock.symbol}): {themes_str}")
        return "\n".join(lines)
