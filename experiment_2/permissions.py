from functools import wraps

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def human_gate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"about to call tool {func.__name__}({args}, {kwargs})")
        answer = input("Are you sure you want to proceed? (y/n): ")
        if answer.lower() in ("y", "yes", ""):
            result = func(*args, **kwargs)
            logger.info(f"tool {func.__name__} returned \n{result}\n=====")
            return result
        else:
            return f"tool {func.__name__} was restricted by the system from executing"

    return wrapper
