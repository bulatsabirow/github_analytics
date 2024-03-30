import random
from typing import Annotated, Optional, ClassVar, Type

from faker import Faker
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.schema import Repository

fake = Faker()


class TestRepository:
    def __init__(self, position_cur: int):
        self.owner: str = fake.name()
        self.repo: str = "/".join((fake.name(), self.owner))
        self.position_cur: int = position_cur
        # 50% - None, 50% - some number from range(1, 101)
        self.position_prev: Optional[int] = None if random.random() > 0.5 else fake.random_int(1, 100)
        self.stars: int = fake.random_int(100000, 400000)
        self.watchers: int = fake.random_int(100000, 400000)
        self.forks: int = fake.random_int(100, 4000)
        self.open_issues: int = fake.random_int(10, 1000)
        # 50% - None, 50% - some language from provided list
        self.language: Optional[str] = (
            None if random.random() > 0.5 else fake.random_element(["Java", "Python", "JavaScript"])
        )

    def as_json(self):
        return {
            "owner": self.owner,
            "position_cur": self.position_cur,
            "repo": self.repo,
            "stars": self.stars,
            "watchers": self.watchers,
            "forks": self.forks,
            "open_issues": self.open_issues,
            "language": self.language,
            "position_prev": self.position_prev,
        }


class TestRepositoryFactory:
    pydantic_model: ClassVar[Type[BaseModel]] = Repository
    instance: ClassVar[Type[TestRepository]] = TestRepository

    def __init__(self, session: AsyncSession):
        self._session = session

    async def batch_create(self, count: int = 1):
        """
        Creates many instances in the database using only one query.
        :param count: count of objects need to be created
        """
        await self._session.execute(
            text(
                """
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
            [self.pydantic_model(**self.instance(i).as_json()).model_dump() for i in range(1, count + 1)],
        )
