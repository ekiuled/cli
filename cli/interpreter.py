from cli.commands import (ExitCode, SUCCESS,
                          Command, Cat, Echo, Wc, Pwd, Grep, Exit, External)
from cli.parser import parse
from typing import TextIO, List
import sys
from os import pipe


environment = dict()


def assignment(inp: TextIO,
               out: TextIO,
               err: TextIO,
               args: List[str]) -> ExitCode:
    """
    Выполняет присваивание значения переменной.
    Игнорирует параметры-потоки ввода/вывода.
    """
    variable, value = args
    environment[variable] = value
    return SUCCESS


commands = {'cat': Cat(),
            'echo': Echo(),
            'wc': Wc(),
            'pwd': Pwd(),
            'grep': Grep(),
            'exit': Exit(),
            '=': assignment}


def get_command(command: str) -> Command:
    """Возвращает объект-команду по её имени."""

    return commands.get(command, External(command))


def run(line: str) -> ExitCode:
    """Выполняет одну строку: команду или пайплайн."""

    pipeline = parse(line, environment)

    if not pipeline:
        return SUCCESS

    if len(pipeline) == 1:
        command, args = pipeline[0]
        exitCode = get_command(command)(sys.stdin,
                                        sys.stdout,
                                        sys.stderr,
                                        args)
        return exitCode

    prev_inp, new_out = pipe()
    command, args = pipeline[0]
    with open(new_out, 'w') as out:
        get_command(command)(sys.stdin,
                             out,
                             sys.stderr,
                             args)

    for command, args in pipeline[1:-1]:
        new_inp, new_out = pipe()
        with open(prev_inp) as inp:
            with open(new_out, 'w') as out:
                get_command(command)(inp,
                                     out,
                                     sys.stderr,
                                     args)
        prev_inp = new_inp

    command, args = pipeline[-1]
    with open(prev_inp) as inp:
        exitCode = get_command(command)(inp,
                                        sys.stdout,
                                        sys.stderr,
                                        args)

    return exitCode
