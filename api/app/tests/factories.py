from typing import ClassVar, Type, Any

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import RepositoryAnalytics
from app.tests.schema import TestRepository


class TestFactory:
    test_model: ClassVar[Type[BaseModel]] = BaseModel

    def __init__(self, session: AsyncSession, *args, **kwargs):
        self._session = session

    async def create_batch(self, count: int = 1):
        """
        Creates many instances in the database using only one query.
        :param count: count of objects need to be created
        """
        return NotImplemented


class TestRepositoryFactory(TestFactory):
    test_model = TestRepository

    async def create_batch(self, count: int = 1):
        dummy_data = [self.test_model(position_cur=i).model_dump() for i in range(1, count + 1)]
        await self._session.execute(
            text(
                f"""
                    INSERT INTO repositories (
                    repo,
                    owner,
                    position_cur,
                    position_prev,
                    stars,
                    watchers,
                    forks,
                    open_issues,
                    language)
                    VALUES (
                    :repo,
                    :owner,
                    :position_cur,
                    :position_prev,
                    :stars,
                    :watchers,
                    :forks,
                    :open_issues,
                    :language
                    )
        """
            ),
            dummy_data,
        )
        return dummy_data


class TestRepositoryAnalyticsFactory(TestFactory):
    test_model = RepositoryAnalytics

    async def create_batch(self, count: int = 1):
        dummy_data = [self.test_model(position=i).model_dump() for i in range(1, count + 1)]
        await self._session.execute(
            text(
                """
        INSERT INTO repo_analytics(date, commits, authors, position)
        VALUES (:date, :commits, :authors, :position);
        """
            ),
            dummy_data,
        )
