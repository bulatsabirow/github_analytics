from typing import Optional, ClassVar

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.query_builders import QueryBuilder


class BaseDatabaseService:
    table_name: ClassVar[Optional[str]] = None
    pydantic_model: ClassVar[BaseModel] = BaseModel

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute(self, query: QueryBuilder):
        raw_results = await self.session.execute(text(query._query + ";"))
        query._query = ""

        return raw_results.mappings().all()
