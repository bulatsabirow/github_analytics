def wrap_string_into_single_quotes(string: str) -> str:
    """
    Use this function to correctly pass the string parameter to SQL query.
    E.g. wrap_string_into_single_quotes('John') -> 'John', but 'John' -> John
    :param string: any string
    :return: string wrapped into single quotes
    """
    return "'%s'" % string
