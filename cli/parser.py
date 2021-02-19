from typing import NamedTuple
# import re


CommandArgs = NamedTuple('CommandArgs',
                         [('command', str), ('args', list[str])])


def parse(line: str) -> list[CommandArgs]:
    """Парсит строку в список команд и их аргументов."""

    commands = line.split('|')
    commands = [command.split() for command in commands]
    return [(name, args) for name, *args in commands]
