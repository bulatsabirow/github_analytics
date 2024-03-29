from typing import Union


class Query:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return NotImplemented


class SelectQuery(Query):
    def __init__(self, table_name: str, *args):
        self.arguments = args
        self.table_name = table_name

    def __repr__(self) -> str:
        print(f"{self.arguments=}")
        if self.arguments == ("*",):
            params = "*"
        else:
            params = ", ".join(self.arguments)
        return "SELECT %(params)s FROM %(table)s" % {"table": self.table_name, "params": params}


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
