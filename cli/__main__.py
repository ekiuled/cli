from cli.interpreter import run

try:
    while True:
        print('> ', end='')
        line = input()
        run(line)
except EOFError:
    pass
