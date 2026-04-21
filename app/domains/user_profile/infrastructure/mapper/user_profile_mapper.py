import json
from datetime import datetime

from app.domains.user_profile.domain.entity.user_interaction import UserInteraction
from app.domains.user_profile.domain.entity.user_profile import UserProfile
from app.domains.user_profile.infrastructure.orm.user_interaction_orm import UserInteractionORM
from app.domains.user_profile.infrastructure.orm.user_profile_orm import UserProfileORM


class UserProfileMapper:
    @staticmethod
    def _load_json_list(raw: str) -> list:
        try:
            return json.loads(raw) if raw else []
        except (json.JSONDecodeError, TypeError):
            return []

    @staticmethod
    def to_entity(orm: UserProfileORM) -> UserProfile:
        return UserProfile(
            id=orm.id,
            account_id=orm.account_id,
            preferred_stocks=UserProfileMapper._load_json_list(orm.preferred_stocks),
            interests_text=orm.interests_text or "",
            investment_style=orm.investment_style or "",
            risk_tolerance=orm.risk_tolerance or "",
            preferred_sectors=UserProfileMapper._load_json_list(orm.preferred_sectors),
            analysis_preference=orm.analysis_preference or "",
            keywords_of_interest=UserProfileMapper._load_json_list(orm.keywords_of_interest),
        )

    @staticmethod
    def to_orm(entity: UserProfile) -> UserProfileORM:
        return UserProfileORM(
            account_id=entity.account_id,
            preferred_stocks=json.dumps(entity.preferred_stocks, ensure_ascii=False),
            interests_text=entity.interests_text,
            investment_style=entity.investment_style,
            risk_tolerance=entity.risk_tolerance,
            preferred_sectors=json.dumps(entity.preferred_sectors, ensure_ascii=False),
            analysis_preference=entity.analysis_preference,
            keywords_of_interest=json.dumps(entity.keywords_of_interest, ensure_ascii=False),
        )


class UserInteractionMapper:
    @staticmethod
    def to_entity(orm: UserInteractionORM) -> UserInteraction:
        return UserInteraction(
            id=orm.id,
            account_id=orm.account_id,
            symbol=orm.symbol,
            interaction_type=orm.interaction_type,
            count=orm.count,
            content=orm.content,
            name=orm.name,
            market=orm.market,
            created_at=orm.created_at or datetime.now(),
        )

    @staticmethod
    def to_orm(entity: UserInteraction) -> UserInteractionORM:
        return UserInteractionORM(
            account_id=entity.account_id,
            symbol=entity.symbol,
            interaction_type=entity.interaction_type,
            count=entity.count,
            content=entity.content,
            name=entity.name,
            market=entity.market,
        )
