from typing import NamedTuple, Dict
import re


CommandArgs = NamedTuple('CommandArgs',
                         [('command', str), ('args', list[str])])


def variable_expansion(word: str, environment: Dict[str, str]) -> str:
    return re.sub(r'\$([^$\s]+)', lambda s: environment[s.group(1)], word)


def name_args(command: str, environment: Dict[str, str]) -> CommandArgs:
    """Достаёт имя и аргументы из одной команды."""

    match = re.fullmatch(r'(\S+)=(\S*)', command)
    if match:
        variable = match.group(1)
        value = variable_expansion(match.group(2), environment)
        return '=', [variable, value]

    name, *args = map(lambda s: variable_expansion(s, environment),
                      command.split())
    return name, args


def parse(line: str, environment: Dict[str, str]) -> list[CommandArgs]:
    """Парсит строку в список команд и их аргументов."""

    commands = re.split(r'\s+\|\s+', line.strip())
    return [name_args(command, environment) for command in commands]
