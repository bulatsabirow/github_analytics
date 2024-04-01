class EscapeSQLQuery:
    def __init__(self, parameter):
        self.parameter = parameter

    def __repr__(self):
        return ":%s" % self.parameter


class EscapeSQLQueryMetaClass(type):
    """
    Prevents SQL-injection attack by intercepting __init__ method parameters
    and wrapping all of them in 'EscapeSQLQuery' class.
    There's no need to use escaping character ":" everywhere, this metaclass do it itself.
    """

    def __call__(cls, *args, **kwargs):
        args = (EscapeSQLQuery(arg) for arg in args)
        kwargs = {key: EscapeSQLQuery(value) for key, value in kwargs.items()}

        return super().__call__(*args, **kwargs)
