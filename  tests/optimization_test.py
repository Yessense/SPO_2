import dis

s = 'def hello():\n    print("hello")'
c = compile(s, '<string>', 'exec')
print(dis.dis(s))