"""
Simplified VM code which works for some cases.
You need extend/rewrite code to pass all cases.
"""

import builtins
import dis
import types
import typing as tp
from collections import OrderedDict


def cmp_outcome(op, v, w):
    if op == '<':
        return v < w
    elif op == '<=':
        return v <= w
    elif op == '==':
        return v == w
    elif op == '!=':
        return v != w
    elif op == '>':
        return v > w
    elif op == '>=':
        return v >= w
    elif op == 'in':
        return v in w
    elif op == 'not in':
        return v not in w
    elif op == 'is':
        return v is w
    elif op == 'is not':
        return v is not w
    elif op == 'is not':
        return v is not w
    elif op == 'exception match':
        return None


class Instruction:
    def __init__(self, opname: str, offset: int, argval: tp.Any):
        self.opname: str = opname
        self.offset: int = offset
        self.argval: tp.Any = argval


class Frame:
    """
    Frame header in cpython with description
        https://github.com/python/cpython/blob/3.6/Include/frameobject.h#L17

    Text description of frame parameters
        https://docs.python.org/3/library/inspect.html?highlight=frame#types-and-members
    """

    def __init__(self,
                 frame_code: types.CodeType,
                 frame_builtins: tp.Dict[str, tp.Any],
                 frame_globals: tp.Dict[str, tp.Any],
                 frame_locals: tp.Dict[str, tp.Any]) -> None:
        self.current_offset = None
        self.code = frame_code
        self.builtins = frame_builtins
        self.globals = frame_globals
        self.locals = frame_locals
        self.data_stack: tp.Any = []
        self.return_value = None
        self.shift = 2

        instruction: dis.Instruction
        self.instructions = [Instruction(opname=instruction.opname.lower() + "_op",
                                         offset=instruction.offset,
                                         argval=instruction.argval)
                             for instruction in dis.get_instructions(self.code)]
        self.max_offset = len(self.instructions)

    def run(self) -> tp.Any:
        self.current_offset = 0
        while self.current_offset < self.max_offset:
            instruction: Instruction = self.instructions[self.current_offset]
            # print(f'Before: {self.current_offset}')
            getattr(self, instruction.opname)(instruction.argval)
            self.current_offset += 1
            # print(f'After: {self.current_offset}')
        return self.return_value

    def jump_forward_op(self, arg):
        self.current_offset += arg // self.shift
        self.current_offset -= 1

    def pop_jump_if_true_op(self, arg) -> None:
        cond = self.pop()
        if not cond:
            return None
        else:
            self.current_offset = arg // self.shift - 1

    def pop_jump_if_false_op(self, arg) -> None:
        cond = self.pop()
        if cond:
            return None
        else:
            self.current_offset = arg // self.shift - 1

    def top(self) -> tp.Any:
        return self.data_stack[-1]

    def pop(self) -> tp.Any:
        return self.data_stack.pop()

    def push(self, *values: tp.Any) -> None:
        self.data_stack.extend(values)

    def popn(self, n: int) -> tp.Any:
        """
        Pop a number of values from the value stack.
        A list of n values is returned, the deepest value first.
        """
        if n > 0:
            returned = self.data_stack[-n:]
            self.data_stack[-n:] = []
            return returned
        else:
            return []

    def call_function_op(self, arg: int) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-CALL_FUNCTION

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L3121
        """
        arguments = self.popn(arg)
        f = self.pop()
        self.push(f(*arguments))

    def load_name_op(self, arg: str) -> None:
        """
        Partial realization

        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-LOAD_NAME

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L2057
        """
        # TODO: parse all scopes
        if arg in self.locals:
            self.push(self.locals[arg])
        elif arg in self.globals:
            self.push(self.globals[arg])
        elif arg in self.builtins:
            self.push(self.builtins[arg])
        else:
            raise NameError

    def load_global_op(self, arg: str) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-LOAD_GLOBAL

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L2108
        """
        if arg in self.globals:
            self.push(self.globals[arg])
        elif arg in self.builtins:
            self.push(self.builtins[arg])
        else:
            raise NameError

    def load_const_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-LOAD_CONST

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L1088
        """
        self.push(arg)

    def return_value_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-RETURN_VALUE

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L1641
        """
        self.return_value = self.pop()

    def pop_top_op(self, arg: tp.Any) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-POP_TOP

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L1102
        """
        self.pop()

    def make_function_op(self, arg: int) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-MAKE_FUNCTION

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L3203

        Parse stack:
            https://github.com/python/cpython/blob/3.7/Objects/call.c#L158

        Call function in cpython:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L4554
        """
        name = self.pop()  # the qualified name of the function (at TOS)  # noqa
        code = self.pop()  # the code associated with the function (at TOS1)

        ERR_TOO_MANY_POS_ARGS = 'Too many positional arguments'
        ERR_TOO_MANY_KW_ARGS = 'Too many keyword arguments'
        ERR_MULT_VALUES_FOR_ARG = 'Multiple values for arguments'
        ERR_MISSING_POS_ARGS = 'Missing positional arguments'
        ERR_MISSING_KWONLY_ARGS = 'Missing keyword-only arguments'

        CO_VARARGS = 0x0004
        CO_VARKEYWORDS = 0x0008

        if arg & 0x08:
            closure = self.pop()
        if arg & 0x04:
            annotations = self.pop()
        if arg & 0x02:
            kwdefaults = self.pop()
        else:
            kwdefaults = None
        if arg & 0x01:
            defaults = self.pop()
        else:
            defaults = None

        def f(*args: tp.Any, **kwargs: tp.Any) -> tp.Any:
            co_flags: int = code.co_flags
            co_varnames: tp.Tuple[str] = code.co_varnames
            co_arg_count: int = code.co_argcount
            co_kwonlyargcount: int = code.co_kwonlyargcount

            parsed_args: tp.Dict[str, tp.Any] = {}
            f_kwargs: tp.Dict[str, tp.Any] = {}
            f_varargs: tp.Tuple[tp.Any] = tuple()

            # ----------------------------------------
            # KW ARGS
            # ----------------------------------------

            for key, value in kwargs.items():
                if key in co_varnames:
                    parsed_args[key] = value
                elif co_flags & CO_VARKEYWORDS:
                    f_kwargs[key] = value
                else:
                    raise TypeError(ERR_TOO_MANY_KW_ARGS)

            # ----------------------------------------
            # POS ARGS
            # ----------------------------------------

            # number of default elements
            n_defaults = len(defaults) if defaults is not None else 0
            n_args = len(args)
            defaults_pos = co_arg_count - n_defaults

            for i, name in zip(range(co_arg_count), co_varnames):
                if i < n_args:
                    parsed_args[name] = args[i]
                    if name in kwargs:
                        raise TypeError(ERR_MULT_VALUES_FOR_ARG)
                elif name in kwargs:
                    parsed_args[name] = kwargs[name]
                elif n_defaults and n_defaults > i - defaults_pos >= 0:
                    parsed_args[name] = defaults[i - defaults_pos]
                else:
                    raise TypeError(ERR_MISSING_POS_ARGS)

            # ----------------------------------------
            # *Args
            # ----------------------------------------

            if n_args > co_arg_count:
                if co_flags & CO_VARARGS:
                    f_varargs = args[co_arg_count:]
                else:
                    raise TypeError(ERR_TOO_MANY_POS_ARGS)

            # ----------------------------------------
            # kwonly
            # ----------------------------------------

            kwonly_pos = co_arg_count
            for i in range(co_kwonlyargcount):
                name = co_varnames[kwonly_pos + i]
                if (name not in kwargs and
                        (kwdefaults is None or
                         name not in kwdefaults)):
                    raise TypeError(ERR_MISSING_KWONLY_ARGS)
                elif (kwdefaults is not None and
                      name in kwdefaults and
                      name not in parsed_args):
                    parsed_args[name] = kwdefaults[name]

            # ----------------------------------------
            # args, kwargs names
            # ----------------------------------------

            args_name_pos = -1

            if co_flags & CO_VARKEYWORDS:
                kwargs_name = co_varnames[-1]
                parsed_args[kwargs_name] = f_kwargs
                args_name_pos -= 1

            if co_flags & CO_VARARGS:
                args_name = co_varnames[args_name_pos]
                parsed_args[args_name] = f_varargs

            f_locals = dict(self.locals)
            f_locals.update(parsed_args)

            frame = Frame(code, self.builtins, self.globals, f_locals)  # Run code in prepared environment
            return frame.run()

        self.push(f)

    def store_name_op(self, arg: str) -> None:
        """
        Operation description:
            https://docs.python.org/3/library/dis.html#opcode-STORE_NAME

        Operation realization:
            https://github.com/python/cpython/blob/3.7/Python/ceval.c#L1923
        """
        const = self.pop()
        self.locals[arg] = const

    def binary_power_op(self, arg: str) -> None:
        exp = self.pop()
        base = self.pop()
        res = pow(base, exp, None)
        self.push(res)

    def compare_op_op(self, arg: str) -> None:
        right = self.pop()
        left = self.pop()
        res = cmp_outcome(arg, left, right)
        self.push(res)
        if res is None:
            raise TypeError

    def load_fast_op(self, arg: str):
        value = self.locals[arg]
        self.push(value)

    def store_fast_op(self, arg):
        value = self.pop()
        self.locals[arg] = value

    def binary_add_op(self, arg):
        right = self.pop()
        left = self.pop()
        sum = left + right
        self.push(sum)

    def binary_multiply_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left * right
        self.push(res)

    def binary_or_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left | right
        self.push(res)

    def binary_xor_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left ^ right
        self.push(res)

    def binary_and_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left & right
        self.push(res)

    def binary_floor_divide_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left // right
        self.push(res)

    def binary_matrix_multiply_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left @ right
        self.push(res)

    def binary_lshift_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left << right
        self.push(res)

    def binary_rshift_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left >> right
        self.push(res)

    def binary_subtract_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left - right
        self.push(res)

    def binary_true_divide_op(self, arg):
        right = self.pop()
        left = self.pop()
        res = left / right
        self.push(res)

    def inplace_add_op(self, arg):
        right = self.pop()
        left = self.pop()
        left += right
        self.push(left)

    def inplace_and_op(self, arg):
        right = self.pop()
        left = self.pop()
        left &= right
        self.push(left)

    def inplace_division_op(self, arg):
        right = self.pop()
        left = self.pop()
        left /= right
        self.push(left)

    def inplace_floor_divide_op(self, arg):
        right = self.pop()
        left = self.pop()
        left //= right
        self.push(left)

    def inplace_lshift_op(self, arg):
        right = self.pop()
        left = self.pop()
        left <<= right
        self.push(left)

    def inplace_matrix_multiply_op(self, arg):
        right = self.pop()
        left = self.pop()
        left @= right
        self.push(left)

    def inplace_module_op(self, arg):
        right = self.pop()
        left = self.pop()
        left %= right
        self.push(left)

    def inplace_multiply_op(self, arg):
        right = self.pop()
        left = self.pop()
        left *= right
        self.push(left)

    def inplace_or_op(self, arg):
        right = self.pop()
        left = self.pop()
        left |= right
        self.push(left)

    def inplace_power_op(self, arg):
        right = self.pop()
        left = self.pop()
        left **= right
        self.push(left)

    def inplace_rshift_op(self, arg):
        right = self.pop()
        left = self.pop()
        left >>= right
        self.push(left)

    def inplace_subtract_op(self, arg):
        right = self.pop()
        left = self.pop()
        left -= right
        self.push(left)

    def inplace_xor_op(self, arg):
        right = self.pop()
        left = self.pop()
        left ^= right
        self.push(left)

    def inplace_true_divide_op(self, arg):
        right = self.pop()
        left = self.pop()
        left /= right
        self.push(left)


class VirtualMachine:
    def run(self, code_obj: types.CodeType) -> None:
        """
        :param code_text_or_obj: code for interpreting
        """
        globals_context: tp.Dict[str, tp.Any] = {}
        frame = Frame(code_obj, builtins.globals()['__builtins__'], globals_context, globals_context)
        return frame.run()
