from typing import Optional

from pydantic import BaseModel
from sqlalchemy import text, String
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDatabaseService:
    table_name: Optional[str] = None
    pydantic_model: BaseModel = BaseModel

    def _get_sql_query(self, sort_field, order):
        return """
            SELECT * FROM %s order by %s %s;
        """ % (
            self.table_name,
            sort_field,
            order,
        )

    def __init__(self, session: AsyncSession):
        self.session = session

    async def select_all(self, field: str, order: str):
        print(f"{field}")
        raw_results = await self.session.execute(text(self._get_sql_query(field, order)))

        return [self.pydantic_model(**raw_item) for raw_item in raw_results.mappings().all()]
