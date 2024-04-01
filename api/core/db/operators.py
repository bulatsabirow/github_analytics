from typing import Any

from core.db.security import EscapeSQLQueryMetaClass


class Operator:
    """
    Base class for SQL operators.
    """

    def __repr__(self):
        return NotImplemented


class EscapedOperator(Operator, metaclass=EscapeSQLQueryMetaClass):
    """
    SQL operator supporting expressions with escaped parameters
    """

    pass


class Between(EscapedOperator):
    def __init__(self, start: Any, end: Any):
        self.start = start
        self.end = end

    def __repr__(self):
        return "BETWEEN %s AND %s" % (self.start, self.end)


class Equals(EscapedOperator):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return "= %s" % self.value


class Exists(Operator):
    def __init__(self, subquery: str):
        self.subquery = subquery

    def __repr__(self):
        return "EXISTS (%s)" % self.subquery
