from cli.interpreter import run


GREEN = '1;32;48m'
RED = '1;31;48m'
colors = [GREEN, RED]


try:
    color = GREEN
    while True:
        print(f'\033[{color}> \033[00m', end='')
        line = input()
        color = colors[run(line)]
except EOFError:
    pass
