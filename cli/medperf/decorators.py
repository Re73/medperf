import logging
import functools
from collections.abc import Callable

from medperf.utils import pretty_error
import medperf.config as config


def clean_except(func: Callable) -> Callable:
    """Decorator for handling unexpected errors. It allows logging
    and cleaning the project's directory before throwing the error.

    Args:
        func (Callable): Function to handle for unexpected errors

    Returns:
        Callable: Decorated function
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info(f"Running function '{func.__name__}'")
            func(*args, **kwargs)
        except Exception as e:
            logging.error("An unexpected error occured. Terminating.")
            logging.error(e)
            pretty_error("An unexpected error occured", config.ui)

    return wrapper
