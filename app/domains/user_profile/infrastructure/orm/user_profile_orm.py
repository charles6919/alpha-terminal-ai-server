from sqlalchemy import Column, Integer, String, Text

from app.infrastructure.database.session import Base


class UserProfileORM(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, nullable=False, unique=True)
    preferred_stocks = Column(Text, nullable=False, default="")   # JSON 문자열로 저장 ex) '["005930","000660"]'
    interests_text = Column(Text, nullable=False, default="")
    investment_style = Column(String(20), nullable=False, default="")      # "단기"|"중장기"|"장기"
    risk_tolerance = Column(String(20), nullable=False, default="")        # "낮음"|"중간"|"높음"
    preferred_sectors = Column(Text, nullable=False, default="")           # JSON list ex) '["IT","반도체"]'
    analysis_preference = Column(String(20), nullable=False, default="")   # "뉴스중심"|"공시중심"|"혼합"
    keywords_of_interest = Column(Text, nullable=False, default="")        # JSON list ex) '["AI반도체"]'
