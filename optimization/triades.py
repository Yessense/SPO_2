import ast
import _ast
import copy
from typing import Dict, Union, List, Set


# ------------------------------------------------------------
# Многоадресный код с неявно именуемым результатом (триады)
# ------------------------------------------------------------
# Триады представляют собой запись операций в форме из трех составляющих:
# операция и два операнда. Например, в строковой записи триады могут иметь вид:
# <операция>(<операнд1>,<операнд2>).

class Tri:
    number = 0

    def __init__(self, op: Union[_ast.operator, _ast.Assign, str],
                 left: Union[_ast.Name, _ast.Num, int],
                 right: Union[_ast.Name, _ast.Num, int]):
        self.op = op
        self.left = left
        self.right = right
        self.number = Tri.number
        Tri.number += 1

    def element_repr(self, element: Union[int, _ast.Num, _ast.Name]) -> str:
        if isinstance(element, int):
            if element < 0:
                return f'Null'
            else:
                return f'^{element}'
        elif isinstance(element, _ast.Num):
            return f'{element.n}'
        elif isinstance(element, _ast.Name):
            return f'{element.id}'

    def op_repr(self, op):
        if isinstance(op, str):
            return op
        else:
            return f'{self.op.__class__.__name__}'

    def __str__(self):
        return f'{self.number}. ' \
               f'({self.op_repr(self.op)}, ' \
               f'{self.element_repr(self.left)}, ' \
               f'{self.element_repr(self.right)})'


def parse_bin_op(op: _ast.BinOp) -> Tri:
    left: Union[_ast.Name, _ast.Num, int]
    right: Union[_ast.Name, _ast.Num, int]

    if isinstance(op.left, _ast.BinOp):
        left = parse_bin_op(op.left).number
    else:
        left = op.left

    if isinstance(op.right, _ast.BinOp):
        right = parse_bin_op(op.right).number
    else:
        right = op.right
    tri = Tri(op=op.op, left=left, right=right)
    triades.append(tri)
    return tri


def make_triades_from_ast(ast: _ast.Module):
    for op in ast.body:
        if isinstance(op, _ast.Assign):
            left: Union[_ast.Name, _ast.Num, int]
            right: Union[_ast.Name, _ast.Num, int]

            left = op.targets[0]
            if isinstance(op.value, _ast.BinOp):
                right = parse_bin_op(op.value).number
            else:
                right = op.value

            tri = Tri(op=op, left=left, right=right)
            triades.append(tri)


triades: List[Tri] = []

statement_1 = """
i = 1 + 1
i = 3
j = 6 * i + i
"""

statement_1_parsed: _ast.Module = ast.parse(statement_1, "<string>", "exec")

# nodes = ast.walk(statement_1_parsed)

make_triades_from_ast(statement_1_parsed)


def show_triades(triades: List[Tri]):
    print(*triades, sep='\n')


show_triades(triades)

# ------------------------------------------------------------
# Свертка объектного кода
# ------------------------------------------------------------
# Свертка объектного кода – это выполнение во время компиляции тех операций
# исходной программы, для которых значения операндов уже известны. Нет необходимости
# многократно выполнять эти операции в результирующей программе – вполне достаточно
# один раз выполнить их при компиляции.

names_values_map: Dict[str, Union[float, int]] = dict()


def optimize_triade(triade: Tri):
    # 1. Если операнд есть переменная, которая содержится в таблице Т, то операнд заменяется
    # на соответствующее значение константы.
    if not isinstance(triade.op, _ast.Assign):
        if isinstance(triade.left, _ast.Name):
            if triade.left.id in names_values_map:
                num = _ast.Num(n=names_values_map[triade.left.id])
                for field in triade.left._fields:
                    setattr(num, field, triade.left.__getattribute__(field))
                triade.left = num
    if isinstance(triade.right, _ast.Name):
        if triade.right.id in names_values_map:
            num = _ast.Num(n=names_values_map[triade.right.id], )
            for field in triade.right._fields:
                setattr(num, field, triade.right.__getattribute__(field))
            triade.right = num

    # 2. Если операнд есть ссылка на особую триаду типа С(К,0), то операнд заменяется на
    # значение константы К.

    if isinstance(triade.left, int) and triade.left >= 0:
        linked_tri = triades[triade.left]
        if isinstance(linked_tri.op, str) and linked_tri.op == 'Const':
            num = _ast.Num(n=linked_tri.left.n)
            for field in linked_tri.left._fields:
                setattr(num, field, linked_tri.left.__getattribute__(field))
            triade.left = num

    if isinstance(triade.right, int) and triade.right >= 0:
        linked_tri = triades[triade.right]
        if isinstance(linked_tri.op, str) and linked_tri.op == 'Const':
            num = _ast.Num(n=linked_tri.left.n)
            for field in linked_tri.left._fields:
                setattr(num, field, linked_tri.left.__getattribute__(field))
            triade.right = num

    # 3. Если все операнды триады являются константами, то триада может быть свернута.
    # Тогда данная триада выполняется и вместо нее помещается особая триада вида С(К,0), где
    # К – константа, являющаяся результатом выполнения свернутой триады. (При генерации
    # кода для особой триады объектный код не порождается, а потому она в дальнейшем
    # может быть просто исключена.)
    if isinstance(triade.op, _ast.operator):
        if isinstance(triade.left, _ast.Num) and isinstance(triade.right, _ast.Num):
            if isinstance(triade.op, _ast.Add):
                left = triade.left.n + triade.right.n
            elif isinstance(triade.op, _ast.Mult):
                left = triade.left.n * triade.right.n
            triade.left = triade.left
            triade.left.n = left
            triade.op = 'Const'
            triade.right = -1

    # 4. Если триада является присваиванием типа А:=В, тогда:
    # - если В — константа, то А со значением константы заносится в таблицу Т (если там
    # уже было старое значение для А, то это старое значение исключается);
    if isinstance(triade.op, _ast.Assign):
        if isinstance(triade.right, _ast.Num):
            names_values_map[triade.left.id] = triade.right.n


def optimize_triades(triades: List[Tri]):
    triade: Tri
    for i, triade in enumerate(triades):
        optimize_triade(triade)

    show_triades(triades)


def remove_const_triades(triades: List[Tri]):
    return [triade for triade in triades if not (isinstance(triade.op, str) and triade.op == 'Const')]


def perform_code_conv(triades: List[Tri]):
    for i in range(len(triades)):
        print('-' * 60)
        print(f'{i}. Iteration of conv algorithm.')
        optimize_triades(triades)

    triades = remove_const_triades(triades)
    return triades


triades = perform_code_conv(triades)
print('-' * 60)
print(f'Remove constant triades')
show_triades(triades)

# ------------------------------------------------------------
# Исключение лишних операций
# ------------------------------------------------------------
# Исключение избыточных вычислений (лишних операций) заключается в
# нахождении и удалении из объектного кода операций, которые повторно обрабатывают
# одни и те же операнды.

print('-' * 60)
print(f'Creating new triades')
print('-' * 60)
Tri.number = 0

statement_2 = """
d = d + c * b
a = d + c * b
c = d + c * b
"""

print(statement_2)
print('-' * 60)

triades: List[Tri] = []
statement_2_parsed: _ast.Module = ast.parse(statement_2, "<string>", "exec")
make_triades_from_ast(statement_2_parsed)
show_triades(triades)

triades_dependency: Dict[int, int] = {}
var_dependency: List[Dict[str, int]] = []


def get_operand_dependency_value(operand: Union[_ast.Name, int, _ast.Num], i_var_dependency) -> int:
    if isinstance(operand, _ast.Name):
        if not operand.id in i_var_dependency:
            i_var_dependency[operand.id] = 0
        return i_var_dependency[operand.id]
    if isinstance(operand, _ast.Num):
        return 0
    if isinstance(operand, int):
        if operand >= 0:
            return triades_dependency[operand]


def get_dependencies(triades: List[Tri]):
    for i, triade in enumerate(triades):
        if i != 0:
            i_var_dependency: Dict[str, int] = copy.deepcopy(var_dependency[i - 1])
        else:
            i_var_dependency = {}
        left_value: int = get_operand_dependency_value(triade.left, i_var_dependency)
        right_value: int = get_operand_dependency_value(triade.right, i_var_dependency)
        triades_dependency[i] = 1 + max(left_value, right_value)
        if isinstance(triade.op, _ast.Assign):
            if isinstance(triade.left, _ast.Name):
                name = triade.left.id
                i_var_dependency[name] = i + 1
        var_dependency.append(i_var_dependency)


get_dependencies(triades)


def print_var_dependencies():
    print('Printing variable dependencies:')
    for i, i_var_dependency in enumerate(var_dependency):
        print(f'{i}. Variable depencdencies')
        for key, value in i_var_dependency.items():
            print(f'Variable: {key.__repr__()}, value: {value}')


def print_triades_dependencies():
    print('Printing variable dependencies:')
    for key, value in triades_dependency.items():
        print(f'Triade: {key.__repr__()}, value: {value}')


print_var_dependencies()
print_triades_dependencies()


def replace_same_triades(triades: List[Tri]):
    for i, triade_i in enumerate(triades):
        for j, triade_j in zip(range(i - 1), triades):
            if isinstance(triade_i.op, _ast.operator) and isinstance(triade_j.op, _ast.operator):
                if type(triade_i.op) == type(triade_j.op):
                    if (isinstance(triade_i.left, _ast.Name) and
                            isinstance(triade_i.right, _ast.Name) and
                            isinstance(triade_j.left, _ast.Name) and
                            isinstance(triade_j.right, _ast.Name) and
                            triade_i.left.id == triade_j.left.id and
                            triade_i.right.id == triade_j.right.id):
                        same_tri = Tri('Same', left=j, right=-1)
                        triades[i] = same_tri
            if isinstance(triade_j.op, str) and triade_j.op == 'Same':
                if



replace_same_triades(triades)
show_triades(triades)
print("done")