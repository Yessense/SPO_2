import dis

s = """
def varnames_test(variable):
    assert 1 == 1
    if 1:
        x = 1
    else:
        x = 3
    hello = variable
    hello = 1
    hi = 2
"""

c = compile(s, "<string>", "exec", optimize=0)
a = ast.parse(s, "<string>", "exec")
print(ast.parse(s, "<string>", "exec"))
print(dis.dis(c))

#
# varnames_test(1)
# print(varnames_test.__code__.co_varnames)
#
# dis.dis(varnames_test)
# print(dis.get_instructions(print))
#
# print(dis.get_instructions(varnames_test.__code__))
#
# for instruction in dis.get_instructions(varnames_test.__code__):
#     print(instruction)