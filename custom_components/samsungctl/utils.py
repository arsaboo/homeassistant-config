import logging
import inspect
import sys
from functools import update_wrapper

PY3 = sys.version_info[0] > 2
logger = logging.getLogger('samsungctl')


def LogIt(func):
    """
    Logs the function call, if debugging log level is set.
    """
    if PY3:
        if func.__code__.co_flags & 0x20:
            raise TypeError("Can't wrap generator function")
    else:
        if func.func_code.co_flags & 0x20:
            raise TypeError("Can't wrap generator function")

    def wrapper(*args, **kwargs):
        func_name, arg_string = func_arg_string(func, args, kwargs)
        logging.debug(func_name + arg_string)
        return func(*args, **kwargs)

    return update_wrapper(wrapper, func)


def LogItWithReturn(func):
    """
    Logs the function call and return, if debugging log level is set.
    """

    if PY3:
        if func.__code__.co_flags & 0x20:
            raise TypeError("Can't wrap generator function")
    else:
        if func.func_code.co_flags & 0x20:
            raise TypeError("Can't wrap generator function")

    def wrapper(*args, **kwargs):
        func_name, arg_string = func_arg_string(func, args, kwargs)
        logging.debug(func_name + arg_string)
        result = func(*args, **kwargs)
        logging.debug(func_name + " => " + repr(result))
        return result

    return update_wrapper(wrapper, func)


def func_arg_string(func, args, kwargs):
    class_name = ""
    if PY3:
        arg_names = inspect.getfullargspec(func)[0]
    else:
        arg_names = inspect.getargspec(func)[0]
    start = 0
    if arg_names:
        if arg_names[0] == "self":
            class_name = args[0].__class__.__name__ + "."
            start = 1

    res = []
    append = res.append

    for key, value in list(zip(arg_names, args))[start:]:
        append(str(key) + "=" + repr(value))

    for key, value in kwargs.items():
        append(str(key) + "=" + repr(value))

    f_name = class_name + func.__name__
    return f_name, "(" + ", ".join(res) + ")"
