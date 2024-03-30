import random
from typing import Optional, ClassVar, Type

from faker import Faker
from pydantic import BaseModel, Field, computed_field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


fake = Faker()


class TestRepository(BaseModel):
    position_cur: int
    owner: str = Field(default_factory=fake.name)

    # 50% - None, 50% - some number from range(1, 101)
    position_prev: Optional[int] = Field(
        default_factory=lambda: None if random.random() > 0.5 else fake.random_int(1, 100)
    )
    stars: int = Field(default_factory=lambda: fake.random_int(100000, 400000))
    watchers: int = Field(default_factory=lambda: fake.random_int(100000, 400000))
    forks: int = Field(default_factory=lambda: fake.random_int(100, 4000))
    open_issues: int = Field(default_factory=lambda: fake.random_int(10, 1000))
    # 50% - None, 50% - some language from provided list
    language: Optional[str] = Field(
        default_factory=lambda: None if random.random() > 0.5 else fake.random_element(["Java", "Python", "JavaScript"])
    )

    @computed_field
    @property
    def repo(self) -> str:
        return "/".join((fake.name(), self.owner))


class TestFactory:
    test_model: ClassVar[Type[BaseModel]] = BaseModel

    def __init__(self, session: AsyncSession):
        self._session = session

    async def batch_create(self, count: int = 1):
        """
        Creates many instances in the database using only one query.
        :param count: count of objects need to be created
        """
        return NotImplemented


class TestRepositoryFactory(TestFactory):
    test_model = TestRepository

    async def batch_create(self, count: int = 1):
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
            [self.test_model(position_cur=i).model_dump() for i in range(1, count + 1)],
        )
