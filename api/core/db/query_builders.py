from typing import Type

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.queries import Query, SelectQuery, WhereQuery, OrderByQuery, JoinQuery


class QueryBuilder:
    def __init__(self, _query: str = ""):
        self._query = _query

    def _execute_base_query(self, query: Type[Query], *args, **kwargs) -> "QueryBuilder":
        return self.__class__(_query=self._query + str(query(*args, **kwargs)))

    def select(self, _from, *args) -> "QueryBuilder":
        self._query = ""
        return self._execute_base_query(SelectQuery, _from, *args)

    def where(self, **kwargs) -> "QueryBuilder":
        return self._execute_base_query(WhereQuery, **kwargs)

    def order_by(self, **kwargs) -> "QueryBuilder":
        return self._execute_base_query(OrderByQuery, **kwargs)

    def join(self, joined_table: str, on: str) -> "QueryBuilder":
        return self._execute_base_query(JoinQuery, **{"joined_table": joined_table, "on": on})
