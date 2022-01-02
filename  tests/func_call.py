import dis
from inspect import getcallargs

s = """
def my_func(a, b, c=1, *args, **kwargs):
    # print(a)
    # print(b)
    # print(c)
    # print(args)
    # print(kwargs)
    return None

my_func(a=1, b=2, c=3)
"""

print(dis.dis(s))