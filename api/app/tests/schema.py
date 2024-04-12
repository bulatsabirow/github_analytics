import datetime
import random
from typing import Optional

from faker import Faker
from pydantic import BaseModel, Field, computed_field


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


class TestRepositoryAnalytics(BaseModel):
    position: int
    date: datetime.date = Field(default_factory=lambda: fake.unique.date_between())
    commits: int = Field(default_factory=lambda: fake.random_int(10, 20))
    authors: list[str] = Field(default_factory=lambda: [fake.unique.name() for _ in range(10)])
