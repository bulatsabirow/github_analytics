from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import Repository, RepositoryAnalytics
from core.db import get_async_session
from core.db.operators import Equals, Between, Exists
from core.db.query_builders import QueryBuilder
from core.db.repo import BaseDatabaseService
from core.db.utils import wrap_string_into_single_quotes


class RepositoryDatabaseService(BaseDatabaseService):
    table_name = "repositories"
    pydantic_model = Repository

    async def fetch_repositories(self, sort, order):
        query = QueryBuilder().select("*").from_(self.table_name).order_by(**{sort: order})
        return await self.execute(query)


class RepositoryAnalyticsDatabaseService(BaseDatabaseService):
    table_name = "repo_analytics"
    pydantic_model = RepositoryAnalytics

    async def check_repository_exists(self, owner, repo):
        query = QueryBuilder().select(
            Exists(
                QueryBuilder()
                .select("1")
                .from_("repositories")
                .where(repo=Equals(wrap_string_into_single_quotes("/".join([owner, repo]))))
            )
        )
        result = await self.execute(query, mode="one")
        return result.get("exists")

    async def fetch_repositories_analytics(self, owner, repo, since, until, sort, order):
        query = (
            QueryBuilder()
            .select("date", "commits", "authors")
            .from_(self.table_name)
            .join(joined_table="repositories", on=f"{self.table_name}.position = repositories.position_cur")
            .where(
                repo=Equals(wrap_string_into_single_quotes("/".join([owner, repo]))),
                date=Between(wrap_string_into_single_quotes(since), wrap_string_into_single_quotes(until)),
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
