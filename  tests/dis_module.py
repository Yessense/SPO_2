import dis

s = '[1, "hello", 3]'

print(dis.dis(s))

c = compile(s, '<string>', 'exec')

print(c)

print(c.co_code)

print(* list(dis.get_instructions(s)), sep='\n')

