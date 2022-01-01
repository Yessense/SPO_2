import sys
from types import FunctionType
from typing import cast

import pytest

# don't use `inspect` pls
sys.modules['inspect'] = None  # type: ignore # noqa

from .arg_binding import (
    bind_args,
    ERR_TOO_MANY_POS_ARGS,
    ERR_TOO_MANY_KW_ARGS,
    ERR_MULT_VALUES_FOR_ARG,
    ERR_MISSING_POS_ARGS,
    ERR_MISSING_KWONLY_ARGS,
)


def test_positional() -> None:
    def foo(a, b, c): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, 1, 2, 3) \
        == dict(a=1, b=2, c=3)
    assert bind_args(foo, 'abc', [1, 2, 3], None) \
        == dict(a='abc', b=[1, 2, 3], c=None)


def test_positional_wrong() -> None:
    def foo(a, b, c): pass      # type: ignore
    foo = cast(FunctionType, foo)

    with pytest.raises(TypeError, match=ERR_MISSING_POS_ARGS):
        bind_args(foo, 1, 2)
    with pytest.raises(TypeError, match=ERR_TOO_MANY_POS_ARGS):
        bind_args(foo, 1, 2, 3, 4)


def test_keyword() -> None:
    def foo(a, b, c): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, a=1, b=2, c=3) \
        == dict(a=1, b=2, c=3)
    assert bind_args(foo, c=None, a='abc', b=[1, 2, 3]) \
        == dict(a='abc', b=[1, 2, 3], c=None)


def test_keyword_wrong() -> None:
    def foo(a, b, c): pass      # type: ignore
    foo = cast(FunctionType, foo)

    with pytest.raises(TypeError, match=ERR_MISSING_POS_ARGS):
        bind_args(foo, a=1, c=3)
    with pytest.raises(TypeError, match=ERR_MULT_VALUES_FOR_ARG):
        bind_args(foo, 1, 2, 3, a=10)
    with pytest.raises(TypeError, match=ERR_TOO_MANY_KW_ARGS):
        bind_args(foo, a='abc', b=[1, 2, 3], d=123)


def test_positional_default() -> None:
    def foo(a, b=2, c=3): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, 1) == dict(a=1, b=2, c=3)
    assert bind_args(foo, 'abc', c=10) == dict(a='abc', b=2, c=10)
    with pytest.raises(TypeError, match=ERR_MISSING_POS_ARGS):
        bind_args(foo, b=2, c=3)


def test_kwonly() -> None:
    def foo(*, a, b, c): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, a=1, b=2, c=3) \
        == dict(a=1, b=2, c=3)
    assert bind_args(foo, c=None, a='abc', b=[1, 2, 3]) \
        == dict(a='abc', b=[1, 2, 3], c=None)


def test_kwonly_wrong() -> None:
    def foo(*, a, b, c): pass      # type: ignore
    foo = cast(FunctionType, foo)

    with pytest.raises(TypeError, match=ERR_TOO_MANY_POS_ARGS):
        bind_args(foo, 1, 2, 3)
    with pytest.raises(TypeError, match=ERR_MISSING_KWONLY_ARGS):
        bind_args(foo, a=1, b=2)


def test_kwonly_default() -> None:
    def foo(*, a=1, b=2, c=3): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo) == dict(a=1, b=2, c=3)
    assert bind_args(foo, c=None) == dict(a=1, b=2, c=None)
    with pytest.raises(TypeError, match=ERR_TOO_MANY_POS_ARGS):
        bind_args(foo, 100)


def test_varargs() -> None:
    def foo(*wtfargs): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, 1, 'a', None, [1, 2, 3]) \
        == dict(wtfargs=(1, 'a', None, [1, 2, 3]))
    assert bind_args(foo) == dict(wtfargs=())


def test_varkwargs() -> None:
    def foo(**kekwargs): pass      # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, foo=1, bar='spam', baz=['eggs']) \
        == dict(kekwargs=dict(foo=1, bar='spam', baz=['eggs']))
    assert bind_args(foo) == dict(kekwargs={})


def test_everything() -> None:
    def foo(a, b, c=None, *args, d, e, f='default', **kwargs): pass  # type: ignore
    foo = cast(FunctionType, foo)

    assert bind_args(foo, 1, 2, 3, d=4, e=5, f=6) \
        == dict(a=1, b=2, c=3, args=(), d=4, e=5, f=6, kwargs={})
    assert bind_args(foo, 1, 2, d=4, e=5) \
        == dict(a=1, b=2, c=None, args=(), d=4, e=5, f='default', kwargs={})
    assert bind_args(foo, 1, 2, 3, 4, 5, 6, d=4, e=5, z=100) \
        == dict(a=1, b=2, c=3, args=(4, 5, 6), d=4, e=5, f='default', kwargs={'z': 100})
    with pytest.raises(TypeError, match=ERR_MISSING_KWONLY_ARGS):
        bind_args(foo, 1, 2, 3, 4, 5, 6)
    with pytest.raises(TypeError, match=ERR_MISSING_KWONLY_ARGS):
        bind_args(foo, 1, 2)
