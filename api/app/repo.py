from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import Repository, RepositoryAnalytics
from core.db import get_async_session
from core.db.operators import Equals, Between
from core.db.query_builders import QueryBuilder
from core.db.repo import BaseDatabaseService


class RepositoryDatabaseService(BaseDatabaseService):
    table_name = "repositories"
    pydantic_model = Repository

    async def fetch_repositories(self, sort, order):
        query = QueryBuilder().select(self.table_name, "*").order_by(**{sort: order})
        return await self.execute(query)


class RepositoryAnalyticsDatabaseService(BaseDatabaseService):
    table_name = "repo_analytics"
    pydantic_model = RepositoryAnalytics

    async def fetch_repositories_analytics(self, owner, repo, since, until, sort, order):
        query = (
            QueryBuilder()
            .select(self.table_name, "date", "commits", "authors")
            .join(joined_table="repositories", on=f"{self.table_name}.position = repositories.position_cur")
            .where(
                repo=Equals(f'\'{"/".join([owner, repo])}\''),
                date=Between(f"'{since}'", f"'{until}'"),
            )
            .order_by(**{sort: order})
        )
        return await self.execute(query)


def get_repository_database_service(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RepositoryDatabaseService:
    return RepositoryDatabaseService(session)


def get_repository_analytics_database_service(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RepositoryAnalyticsDatabaseService:
    return RepositoryAnalyticsDatabaseService(session)
