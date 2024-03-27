import datetime
import typing
from typing import Optional, Annotated, Literal, TypeVar, TypeAlias

from fastapi.params import Query
from pydantic import BaseModel, Field, field_validator


class Repository(BaseModel):
    repo: Annotated[str, Field(max_length=512)]
    owner: Annotated[str, Field(max_length=256)]
    position_cur: Annotated[int, Field(ge=1, le=100)]
    position_prev: Annotated[Optional[int], Field(ge=1, le=100, default=None)]
    stars: Annotated[int, Field(ge=0)]
    watchers: Annotated[int, Field(ge=0)]
    forks: Annotated[int, Field(ge=0)]
    open_issues: Annotated[int, Field(ge=0)]
    language: Annotated[Optional[str], Field(max_length=128)]


class RepositoryAnalytics(BaseModel):
    date: datetime.date
    commits: Annotated[int, Field(ge=0)]
    authors: list[str]


class RepositoryQueryParams(BaseModel):
    sort: Literal[tuple(Repository.schema().get("properties").keys())] | None = Field(Query(default="position_cur"))
    order: Literal["asc", "desc"] | None = Field(Query(default="asc"))
