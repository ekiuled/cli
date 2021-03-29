from abc import ABC, abstractmethod
from os.path import expanduser
from typing import TextIO, NewType, Tuple, List
import sys
from os import getcwd, chdir, listdir
import subprocess
import re


ExitCode = NewType('ExitCode', int)
SUCCESS = ExitCode(0)
FAIL = ExitCode(1)


class Command(ABC):
    """Базовый класс всех команд."""

    @abstractmethod
    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        """Вызов команды.

        :param inp: входной поток
        :param out: выходной поток
        :param err: поток ошибок
        :param args: агрументы команды
        :returns: код завершения команды
        """
        pass


class Cat(Command):
    """Выводит содержимое файла на экран."""

    def cat(self, fd: TextIO, out: TextIO) -> None:
        """Выводит содержимое потока `fd` в поток `out`."""

        for line in fd:
            print(line, file=out, end='')

    def cat_file(self,
                 filename: str,
                 out: TextIO,
                 err: TextIO) -> ExitCode:
        """
        Выводит содержимое файла `filename`, если он существует,
        в поток `out` и возвращает `SUCCESS`.
        В противном случае сообщает об ошибке в поток `err`
        и возвращает `FAIL`.
        """

        try:
            with open(filename) as fd:
                self.cat(fd, out)
                return SUCCESS
        except IOError:
            print(f'cat: {filename}: No such file or directory', file=err)
            return FAIL

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        if not args:
            self.cat(inp, out)
            return SUCCESS

        exitCode = SUCCESS

        for filename in args:
            ret = self.cat_file(filename, out, err)
            exitCode = max(exitCode, ret)

        return exitCode


class Echo(Command):
    """Выводит на экран свои аргументы."""

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        print(*args, file=out)
        return SUCCESS


class Wc(Command):
    """Выводит количество строк, слов и байт в файле."""

    def wc(self, fd: TextIO) -> tuple:
        """Возвращает количество строк, слов и байт в потоке `fd`."""

        nl, words, byte = 0, 0, 0
        for line in fd:
            nl += 1
            words += len(line.split())
            byte += len(line.encode('utf-8'))
        return nl, words, byte

    def wc_file(self,
                filename: str,
                out: TextIO,
                err: TextIO) -> Tuple[tuple, ExitCode]:
        """
        Выводит количество строк, слов и байт в файле `filename`,
        если он существует, в поток `out` и возвращает их вместе с `SUCCESS`.
        В противном случае сообщает об ошибке в поток `err`
        и возвращает `FAIL`.
        """

        try:
            with open(filename) as fd:
                counts = self.wc(fd)
                print(*counts, filename, file=out, sep='\t')
                return counts, SUCCESS
        except IOError:
            print(f'wc: {filename}: No such file or directory', file=err)
            return (0, 0, 0), FAIL

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        if not args:
            print(*self.wc(inp), file=out, sep='\t')
            return SUCCESS

        if len(args) == 1:
            filename = args[0]
            _, exitCode = self.wc_file(filename, out, err)
            return exitCode

        exitCode = SUCCESS
        total = (0, 0, 0)

        for filename in args:
            counts, ret = self.wc_file(filename, out, err)
            exitCode = max(exitCode, ret)
            total = tuple(map(sum, zip(total, counts)))
        print(*total, 'total', file=out, sep='\t')

        return exitCode


class Pwd(Command):
    """Выводит текущую директорию."""

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        print(getcwd(), file=out)
        return SUCCESS


class Grep(Command):
    """Ищет паттерн в файлах или входном потоке."""

    def match(self,
              pattern: str,
              case_insensitive: bool,
              whole_word: bool,
              line: str) -> bool:
        """Проверяет, подходит ли строка под паттерн."""

        if whole_word:
            pattern = fr'\b{pattern}\b'
        if case_insensitive:
            return re.search(pattern, line, re.IGNORECASE) is not None
        return re.search(pattern, line) is not None

    def grep(self,
             pattern: str,
             case_insensitive: bool,
             whole_word: bool,
             context: int,
             fd: TextIO,
             out: TextIO,
             prefix: str = '') -> ExitCode:
        """
        Выводит строки потока `fd`, содержащие `pattern`, в поток `out`.
        Возвращает SUCCESS, если выведена хотя бы одна строка.
        """

        exitCode = FAIL
        context_counter = 0

        for line in fd:
            context_counter -= 1

            if self.match(pattern, case_insensitive, whole_word, line):
                if context and not exitCode and context_counter < 0:
                    print('--', file=out)
                exitCode = SUCCESS
                context_counter = context + 1

            if context_counter > 0:
                print(f'{prefix}{line}', file=out, end='')

        return exitCode

    def grep_file(self,
                  pattern: str,
                  case_insensitive: bool,
                  whole_word: bool,
                  context: int,
                  filename: str,
                  out: TextIO,
                  err: TextIO,
                  prefix: str = '') -> ExitCode:
        """
        Выводит содержащие `pattern` строки файла `filename`,
        если он существует, в поток `out` и возвращает `SUCCESS`,
        если выведена хотя бы одна строка.
        В противном случае сообщает об ошибке в поток `err`
        и возвращает `FAIL`.
        """

        try:
            with open(filename) as fd:
                return self.grep(pattern,
                                 case_insensitive, whole_word, context,
                                 fd, out, prefix)
        except IOError:
            print(f'grep: {filename}: No such file or directory', file=err)
            return FAIL

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        case_insensitive = False
        whole_word = False
        context = 0

        if '-i' in args:
            case_insensitive = True
            args.remove('-i')

        if '-w' in args:
            whole_word = True
            args.remove('-w')

        if '-A' in args:
            index = args.index('-A')
            if index + 1 >= len(args) or not args[index + 1].isdigit():
                print('grep: option -A requires a numeric argument',
                      file=err)
                return FAIL
            context = int(args[index + 1])
            del args[index:index + 2]

        if not args:
            print('grep: missing pattern', file=err)
            return FAIL
        pattern = args.pop(0)

        if not args:
            return self.grep(pattern,
                             case_insensitive, whole_word, context,
                             inp, out)

        if len(args) == 1:
            filename = args[0]
            return self.grep_file(pattern,
                                  case_insensitive, whole_word, context,
                                  filename, out, err)

        exitCode = SUCCESS

        for filename in args:
            ret = self.grep_file(pattern,
                                 case_insensitive, whole_word, context,
                                 filename, out, err,
                                 f'{filename}:')
            exitCode = max(exitCode, ret)

        return exitCode


class Exit(Command):
    """Выходит из интерпретатора."""

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        sys.exit()


class Cd(Command):
    """Переходит в нужную директорию."""

    def cd(self,
           path: str,
           err: TextIO) -> ExitCode:
        """Переходит в директорию `path`."""

        try:
            chdir(path)
            return SUCCESS
        except FileNotFoundError:
            print(f'cd: {path}: No such file or directory', file=err)
            return FAIL

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        if not args:
            self.cd(expanduser("~"), out)
            return SUCCESS

        if len(args) > 1:
            print('cd: too many arguments', file=err)
            return FAIL

        path = args[0]

        if path == '~':
            path = expanduser("~")

        exitCode = self.cd(path, err)
        return exitCode


class Ls(Command):
    """Печатает содержимое директории."""

    def ls(self,
           path: str,
           out: TextIO,
           err: TextIO) -> ExitCode:
        """Печатает список файлов и директорий в директории `path`."""

        try:
            list_dir = sorted(listdir(path))
            print("\n".join(list_dir), file=out)
            return SUCCESS
        except FileNotFoundError:
            print(f'ls: {path}: No such file or directory', file=err)
            return FAIL

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        if args and len(args) > 1:
            print('ls: too many arguments', file=err)
            return FAIL

        path = args[0] if args else "."

        exitCode = self.ls(path, out, err)
        return exitCode


class External(Command):
    """Вызывает внешнюю команду."""

    def __init__(self, command: str) -> None:
        self.command = command

    def __call__(self,
                 inp: TextIO,
                 out: TextIO,
                 err: TextIO,
                 args: List[str]) -> ExitCode:
        try:
            return ExitCode(subprocess.call([self.command, *args],
                                            stdin=inp,
                                            stdout=out,
                                            stderr=err))
        except KeyboardInterrupt:
            return SUCCESS
        except Exception:
            return FAIL
