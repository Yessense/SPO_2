import ast
import _ast

statement_1 = """
def test_func():
    a = 1
    return a
    a = 2
"""

statement_2 = """
def test_func():
    if True:
        return a
        print(a)
    a = 1
    return a
    a = 2
    
"""

statement_3 = """
def test_func():
    if True:
        pass

"""

statement_4 = """
def test_func():
    if True:
        x = 1
    else:
        pass
"""


def dead_code_elimination(obj):
    body_name = "body"
    if hasattr(obj, body_name):
        body = getattr(obj, body_name)
        if isinstance(body, list):
            for i, element in enumerate(body):
                if isinstance(element, _ast.Return):
                    obj.body = obj.body[:i + 1]
                    break
            for element in obj.body:
                dead_code_elimination(element)


def remove_empty_object(obj):
    if hasattr(obj, "orelse"):
        orelse = getattr(obj, "orelse")
        if isinstance(orelse, list):
            if len(orelse) == 1:
                if isinstance(obj.orelse[0], _ast.Pass):
                    obj.orelse = []

    body_name = "body"
    if hasattr(obj, body_name):
        body = getattr(obj, body_name)
        if isinstance(body, list):
            if len(body) == 1:
                if isinstance(obj.body[0], _ast.Pass):
                    return True
            obj.body = [element for element in obj.body if not remove_empty_object(element)]
            return False


statement_1_parsed: _ast.Module = ast.parse(statement_1, "<string>", "exec")
dead_code_elimination(statement_1_parsed)

statement_2_parsed: _ast.Module = ast.parse(statement_2, "<string>", "exec")
dead_code_elimination(statement_2_parsed)

statement_3_parsed: _ast.Module = ast.parse(statement_3, "<string>", "exec")
remove_empty_object(statement_3_parsed)

statement_4_parsed: _ast.Module = ast.parse(statement_4, "<string>", "exec")
remove_empty_object(statement_4_parsed)
print("Done")
