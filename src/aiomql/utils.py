"""Utility functions for aiomql."""
def dict_to_string(data: dict, multi=False) -> str:
    """Convert a dict to a string. Use for logging.

    Args:
        data (dict): The dict to convert.
        multi (bool, optional): If True, each key-value pair will be on a new line. Defaults to False.

    Returns:
        str: The string representation of the dict.
    """
    sep = '\n' if multi else ', '
    return f"{sep}".join(f"{key}: {value}\n" for key, value in data.items())