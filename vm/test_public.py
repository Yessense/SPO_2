import pytest
import sys
import typing as tp

# pls don't use `inspect` and `FunctionType`
from . import function_type_ban  # noqa
sys.modules['inspect'] = None  # type: ignore # noqa

from . import cases
from . import vm_scorer
from . import vm_runner
from . import vm

IDS = [test.name for test in cases.TEST_CASES]
TESTS = [test.text_code for test in cases.TEST_CASES]
SCORER = vm_scorer.Scorer(TESTS)
SCORES = [SCORER.score(test) for test in TESTS]


def test_version() -> None:
    """
    To do this task you need python=3.7.3
    """
    assert '3.7.3' == sys.version.split(' ', maxsplit=1)[0]


@pytest.mark.parametrize("test,score", zip(cases.TEST_CASES, SCORES), ids=IDS)
def test_all_cases(test: cases.Case, score: float) -> None:
    """
    Compare all test cases with etalon
    :param test: test case to check
    :param score: score for test if passed
    """
    code = vm_runner.compile_code(test.text_code)
    globals_context: tp.Dict[str, tp.Any] = {}
    vm_out, vm_err, vm_exc = vm_runner.execute(code, vm.VirtualMachine().run)
    py_out, py_err, py_exc = vm_runner.execute(code, eval, globals_context, globals_context)

    assert vm_out == py_out

    if py_exc is not None:
        assert vm_exc == py_exc
    else:
        assert vm_exc is None

    # Write to stderr for subsequent parsing
    sys.stderr.write("test result score: {}\n".format(score))
    sys.stderr.flush()
