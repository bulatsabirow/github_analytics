from typing import Optional, ClassVar, Union, Type

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from services.db.query_builders import QueryBuilder


class BaseDatabaseService:
    table_name: ClassVar[Optional[str]] = None
    pydantic_model: ClassVar[Type[BaseModel]] = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, query: Union[QueryBuilder, str], mode: str = "all", **kwargs):
        raw_results = await self.session.execute(text(str(query) + ";"), kwargs)

        try:
            query._query = ""
        except AttributeError:
            pass
        finally:
            return getattr(raw_results.mappings(), mode)()
