import inspect
import dis


def my_func(a, b=2, c=1, d=None, *args, lol, hi=True, **kwargs):
    # print(a)
    # print(b)
    a = 1
    a = 2
    # print(c)
    print(args)
    print(kwargs)
    return None

def new_func(*args, **kwargs):
    # print(a)
    # print(b)
    # print(c)
    print(args)
    print(kwargs)
    return None

if __name__ == '__main__':
    # {
    #     'a': 10,
    #     'b': 20,
    #     'c': None,
    #     args: (),
    #     kwargs: {
    #         'verbose': True,
    #     },
    # }
    a = inspect.signature(my_func)
    b = a.bind(1, 2, 3, 1234, 'asdf', '123', '123', lol=True, hello=1)
    c = inspect.getcallargs(my_func, 1, 2, 3, 1234, 'asdf', '123', '123', lol=True, hello=1 )
    print(c)


    dis.show_code(my_func)
    print(f'Defaults: {my_func.__defaults__}')
    print(f'KW defaults: {my_func.__kwdefaults__}')
    print(f'Flags: {my_func.__code__.co_flags}')
    print(f'Var names: {my_func.__code__.co_varnames}')
    print(f'Arg count: {my_func.__code__.co_argcount}')

    print(f'Kw only arg count: {my_func.__code__.co_kwonlyargcount}')
    new_func()
    print("")

