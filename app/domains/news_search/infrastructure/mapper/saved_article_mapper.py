from app.domains.news_search.domain.entity.saved_article import SavedArticle
from app.domains.news_search.infrastructure.orm.saved_article_orm import SavedArticleORM


class SavedArticleMapper:
    @staticmethod
    def to_entity(orm: SavedArticleORM) -> SavedArticle:
        return SavedArticle(
            id=orm.id,
            account_id=orm.account_id,
            title=orm.title,
            link=orm.link,
            source=orm.source,
            snippet=orm.snippet,
            published_at=orm.published_at,
            saved_at=orm.saved_at,
        )

    @staticmethod
    def to_orm(entity: SavedArticle) -> SavedArticleORM:
        return SavedArticleORM(
            account_id=entity.account_id,
            title=entity.title,
            link=entity.link,
            source=entity.source,
            snippet=entity.snippet,
            published_at=entity.published_at,
        )
