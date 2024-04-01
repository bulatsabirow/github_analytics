from typing import Union


class Query:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return NotImplemented

    def __str__(self) -> str:
        return repr(self)


class SelectQuery(Query):
    def __init__(self, *args):
        self.arguments = args

    def __repr__(self) -> str:
        params = ", ".join(map(str, self.arguments))

        return "SELECT %s" % params


class FromQuery(Query):
    def __init__(self, _from: str):
        self._from = _from

    def __repr__(self) -> str:
        return " FROM %s" % self._from


class WhereQuery(Query):
    def __repr__(self) -> str:
        return " WHERE %s" % " AND ".join(f"{key} {value}" for key, value in self.kwargs.items())


class OrderByQuery(Query):
    def __repr__(self) -> str:
        return " ORDER BY %s" % ", ".join(f"{key} {value}" for key, value in self.kwargs.items())


class JoinQuery(Query):
    def __init__(self, joined_table: str, on: str, **kwargs):
        super().__init__(**kwargs)
        self.joined_table = joined_table
        self.on = on

    def __repr__(self) -> str:
        return " JOIN %(table)s ON %(condition)s" % {"table": self.joined_table, "condition": self.on}
