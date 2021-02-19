from abc import ABC, abstractmethod
from typing import TextIO, NewType, Tuple, List
import sys
from os import getcwd


ExitCode = NewType('ExitCode', int)
SUCCESS = ExitCode(0)
FAIL = ExitCode(1)


class Command(ABC):
    @abstractmethod
    def call(self, inp: TextIO, out: TextIO, err: TextIO, args: List[str]) -> ExitCode:
        pass


class Cat(Command):
    """Выводит содержимое файла на экран."""

    def cat(self, fd: TextIO, out: TextIO) -> None:
        for line in fd:
            print(line, file=out, end='')

    def catFile(self, filename: str, out: TextIO, err: TextIO) -> ExitCode:
        try:
            with open(filename) as fd:
                self.cat(fd, out)
                return SUCCESS
        except IOError:
            print(f'cat: {filename}: No such file or directory', file=err)
            return FAIL

    def call(self, inp: TextIO, out: TextIO, err: TextIO, args: List[str]) -> ExitCode:
        if not args:
            self.cat(inp, out)
            return SUCCESS

        exitCode = SUCCESS

        for filename in args:
            ret = self.catFile(filename, out, err)
            exitCode = max(exitCode, ret)

        return exitCode


class Echo(Command):
    """Выводит на экран свои аргументы."""

    def call(self, inp: TextIO, out: TextIO, err: TextIO, args: List[str]) -> ExitCode:
        print(*args, file=out)
        return SUCCESS


class Wc(Command):
    """Выводит количество строк, слов и байт в файле."""

    def wc(self, fd: TextIO) -> tuple:
        nl, words, byte = 0, 0, 0
        for line in fd:
            nl += 1
            words += len(line.split())
            byte += len(line.encode('utf-8'))
        return nl, words, byte

    def wcFile(self, filename: str, out: TextIO, err: TextIO) -> Tuple[tuple, ExitCode]:
        try:
            with open(filename) as fd:
                counts = self.wc(fd)
                print(*counts, filename, file=out, sep='\t')
                return counts, SUCCESS
        except IOError:
            print(f'wc: {filename}: No such file or directory', file=err)
            return None, FAIL

    def call(self, inp: TextIO, out: TextIO, err: TextIO, args: List[str]) -> ExitCode:
        if not args:
            print(*self.wc(inp), file=out, sep='\t')
            return SUCCESS

        if len(args) == 1:
            filename = args[0]
            _, exitCode = self.wcFile(filename, out, err)
            return exitCode

        exitCode = SUCCESS
        total = (0, 0, 0)

        for filename in args:
            counts, ret = self.wcFile(filename, out, err)
            exitCode = max(exitCode, ret)
            total = tuple(map(sum, zip(total, counts)))
        print(*total, 'total', file=out, sep='\t')

        return exitCode


class Pwd(Command):
    """Выводит текущую директорию."""

    def call(self, inp: TextIO, out: TextIO, err: TextIO, args: List[str]) -> ExitCode:
        print(getcwd(), file=out)
        return SUCCESS


class Exit(Command):
    """Выходит из интерпретатора."""

    def call(self, inp: TextIO, out: TextIO, err: TextIO, args: List[str]) -> ExitCode:
        sys.exit()
