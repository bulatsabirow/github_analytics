import asyncio
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import Repository, RepositoryAnalytics
from core.db import get_async_session
from core.repo import BaseDatabaseService


class RepositoryDatabaseService(BaseDatabaseService):
    table_name = "repositories"
    pydantic_model = Repository


class RepositoryAnalyticsDatabaseService(BaseDatabaseService):
    table_name = "repo_analytics"
    pydantic_model = RepositoryAnalytics


def get_repository_database_service(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> RepositoryDatabaseService:
    return RepositoryDatabaseService(session)
