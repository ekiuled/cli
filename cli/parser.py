from typing import NamedTuple


CommandArgs = NamedTuple('CommandArgs',
                         [('command', str), ('args', list[str])])


def parse(line: str) -> list[CommandArgs]:
    commands = line.split('|')
    commands = [command.split() for command in commands]
    return [(name, args) for name, *args in commands]
