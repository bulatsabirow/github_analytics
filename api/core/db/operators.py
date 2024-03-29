from typing import Any


class Operator:
    """
    Base class for SQL operators.
    """

    def __repr__(self):
        return NotImplemented


class Between(Operator):
    def __init__(self, start: Any, end: Any):
        self.start = start
        self.end = end

    def __repr__(self):
        return "BETWEEN %s AND %s" % (self.start, self.end)


class Equals(Operator):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return "= %s" % self.value
