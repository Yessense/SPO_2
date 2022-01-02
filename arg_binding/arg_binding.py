import types
from collections import OrderedDict
from types import FunctionType
from typing import Any, Dict, Optional, Tuple, List
from dis import COMPILER_FLAG_NAMES as compiler_flag_names

COMPILER_FLAG_NAMES = {1: 'OPTIMIZED',
                       2: 'NEWLOCALS',
                       4: 'VARARGS',
                       8: 'VARKEYWORDS',
                       16: 'NESTED',
                       32: 'GENERATOR',
                       64: 'NOFREE',
                       128: 'COROUTINE',
                       256: 'ITERABLE_COROUTINE',
                       512: 'ASYNC_GENERATOR'}

# The code object has a variable positional parameter (*args-like).
CO_VARARGS = 0x0004

# The code object has a variable keyword parameter (**kwargs-like).
CO_VARKEYWORDS = 0x0008

CO_OPTIMIZED = 0x0001
CO_NEWLOCALS = 0x0002
CO_NESTED = 0x0010
CO_GENERATOR = 0x0020
CO_NOFREE = 0x0040

ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
ERR_MISSING_POS_ARGS = 'Missing positional arguments'
ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'


def bind_args(func: FunctionType, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    """Bind values from `args` and `kwargs` to corresponding arguments of `func`

    :param func: function to be inspected
    :param args: positional arguments to be bound
    :param kwargs: keyword arguments to be bound
    :return: `dict[argument_name] = argument_value` if binding was successful,
             raise TypeError with one of `ERR_*` error descriptions otherwise
    """

    # Tuple с значениями по-умолчанию позиционных аргументов функции.
    defaults: Optional[Tuple[Any]] = func.__defaults__

    # Словарь значений по умолчанию аргументов функции, которые можно передавать только по имени
    kwdefaults: Dict = func.__kwdefaults__

    # Bitwise mask
    co_flags: int = func.__code__.co_flags

    # Name of variables in tuple
    co_varnames: Tuple[str] = func.__code__.co_varnames
    # Count of unnamed arguments
    co_arg_count: int = func.__code__.co_argcount
    # Count of named only arguments
    co_kwonlyargcount: int = func.__code__.co_kwonlyargcount

    call_args: Dict[str, Any] = {}
    f_kwargs: Dict[str, Any] = {}

    # ----------------------------------------
    # POS ARGS
    # ----------------------------------------
    # number of default elements
    n_defaults = len(defaults) if defaults is not None else 0
    n_args = len(args)

    if n_defaults + n_args < co_arg_count:
        raise TypeError(ERR_MISSING_POS_ARGS)

    if n_args > co_arg_count:
        if (co_flags & CO_VARARGS):
            if (co_flags & CO_VARKEYWORDS):
                kw_name = co_varnames[-1]
                call_args[kw_name] = f_kwargs
                args_name_pos = -2
            else:
                args_name_pos = -1
            name = co_varnames[args_name_pos]
            call_args[name] = args[n_args - co_arg_count:]
        else:
            raise TypeError(ERR_TOO_MANY_POS_ARGS)

    defaults_pos = 0
    for i in range(co_arg_count):
        name = co_varnames[i]
        if i <= n_args:
            call_args[name] = args[i]
        else:
            call_args[name] = defaults[defaults_pos]
            defaults_pos += 1

    # ----------------------------------------
    # KW ARGS
    # ----------------------------------------

    for i in range(co_kwonlyargcount):
        name = co_varnames[co_arg_count + i]
        if name in kwargs:
            call_args[name] = kwargs[name]
        elif name in kwdefaults:
            call_args[name] = kwdefaults[name]
        else:
            raise TypeError(ERR_MISSING_KWONLY_ARGS)

    for key, value in kwargs:
        if key not in co_varnames and (CO_VARKEYWORDS & co_flags):
            f_kwargs[key] = value
        else:
            raise TypeError(ERR_TOO_MANY_KW_ARGS)

    return call_args


def my_func(a, b=2, c=1, d=None, *args, **kwargs):
    # print(a)
    # print(b)
    # print(c)
    # print(args)
    # print(kwargs)
    return None


if __name__ == '__main__':
    bind_args(my_func, )
