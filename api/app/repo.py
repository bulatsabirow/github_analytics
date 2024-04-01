from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.consts import (
    CREATE_REPOSITORIES_TABLE_QUERY,
    DROP_REPOSITORIES_TABLE_QUERY,
)
from app.schema import Repository, RepositoryAnalytics
from core.db import get_async_session
from core.db.operators import Equals, Between, Exists
from core.db.query_builders import QueryBuilder
from core.db.repo import BaseDatabaseService


class RepositoryDatabaseService(BaseDatabaseService):
    table_name = "repositories"
    pydantic_model = Repository

    async def create_table(self):
        create_table_query = CREATE_REPOSITORIES_TABLE_QUERY
        await self.session.execute(text(create_table_query + ";"))

    async def drop_table(self, is_cascade=True):
        drop_table_query = DROP_REPOSITORIES_TABLE_QUERY + f"{'CASCADE' if is_cascade else ''};"
        await self.session.execute(text(drop_table_query))

    async def fetch_repositories(self, sort, order):
        query = QueryBuilder().select("*").from_(self.table_name).order_by(**{sort: order})
        return await self.execute(query)


class RepositoryAnalyticsDatabaseService(BaseDatabaseService):
    table_name = "repo_analytics"
    pydantic_model = RepositoryAnalytics

    async def check_repository_exists(self, owner, repo):
        query = QueryBuilder().select(
            Exists(QueryBuilder().select("1").from_("repositories").where(repo=Equals("repo")))
        )
        result = await self.execute(query, mode="one", repo="/".join([owner, repo]))
        return result.get("exists")

    async def fetch_repositories_analytics(self, owner, repo, since, until, sort, order):
        query = (
            QueryBuilder()
            .select("date", "commits", "authors")
            .from_(self.table_name)
            .join(joined_table="repositories", on=f"{self.table_name}.position = repositories.position_cur")
            .where(
                repo=Equals("repo"),
                date=Between("since", "until"),
            )
            .order_by(**{sort: order})
        )
        return await self.execute(query, repo="/".join([owner, repo]), since=since, until=until)


def get_repository_database_service(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RepositoryDatabaseService:
    return RepositoryDatabaseService(session)


def get_repository_analytics_database_service(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RepositoryAnalyticsDatabaseService:
    return RepositoryAnalyticsDatabaseService(session)
