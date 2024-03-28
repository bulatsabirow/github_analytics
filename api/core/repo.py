from typing import Optional, ClassVar, Type, Any

from pydantic import BaseModel
from sqlalchemy import text, String, select
from sqlalchemy.ext.asyncio import AsyncSession


class Between:
    def __init__(self, start: Any, end: Any):
        self.start = start
        self.end = end

    def __repr__(self):
        return "BETWEEN %s AND %s" % (self.start, self.end)


class Equals:
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return "= %s" % self.value


class Query:
    def __init__(self, table_name: str, **kwargs):
        self.table_name = table_name
        self.kwargs = kwargs

    def get_sql_query(self):
        return NotImplemented


class SelectQuery(Query):
    def get_sql_query(self):
        return "SELECT * FROM %s" % self.table_name


class WhereQuery(Query):
    def get_sql_query(self):
        return " WHERE %s" % " AND ".join(f"{key} {value}" for key, value in self.kwargs.items())


class OrderByQuery(Query):
    def get_sql_query(self):
        return " ORDER BY %s" % ", ".join(f"{key} {value}" for key, value in self.kwargs.items())


class JoinQuery(Query):
    def __init__(self, table_name: str, joined_table: str, on: str, **kwargs):
        super().__init__(table_name, **kwargs)
        self.joined_table = joined_table
        self.on = on

    def get_sql_query(self):
        return " JOIN %s ON %s" % (self.joined_table, self.on)


class BaseDatabaseService:
    table_name: ClassVar[Optional[str]] = None
    pydantic_model: ClassVar[BaseModel] = BaseModel

    def __init__(self, session: AsyncSession, _query: str = ""):
        self.session = session
        self._query = _query

    def _execute_base_query(self, query: Type[Query], **kwargs) -> "BaseDatabaseService":
        return self.__class__(self.session, _query=self._query + query(self.table_name, **kwargs).get_sql_query())

    def select_all(self) -> "BaseDatabaseService":
        self._query = ""
        return self._execute_base_query(SelectQuery)

    def where(self, **kwargs) -> "BaseDatabaseService":
        return self._execute_base_query(WhereQuery, **kwargs)

    def order_by(self, **kwargs) -> "BaseDatabaseService":
        return self._execute_base_query(OrderByQuery, **kwargs)

    def join(self, joined_table: str, on: str) -> "BaseDatabaseService":
        return self._execute_base_query(JoinQuery, **{"joined_table": joined_table, "on": on})

    async def execute(self):
        print(f"execute {self._query=}")
        raw_results = await self.session.execute(text(self._query + ";"))

        return [self.pydantic_model(**raw_item) for raw_item in raw_results.mappings().all()]
