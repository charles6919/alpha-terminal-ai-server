from typing import List
from pydantic import BaseModel


class UpdateInvestmentProfileRequest(BaseModel):
    investment_style: str = ""        # "단기"|"중장기"|"장기"
    risk_tolerance: str = ""          # "낮음"|"중간"|"높음"
    preferred_sectors: List[str] = [] # ["IT", "반도체", ...]
    analysis_preference: str = ""     # "뉴스중심"|"공시중심"|"혼합"
    keywords_of_interest: List[str] = []
