from typing import NamedTuple, Dict, Generator, List
import re


CommandArgs = NamedTuple('CommandArgs',
                         [('command', str), ('args', List[str])])


def variable_expansion(word: str, environment: Dict[str, str]) -> str:
    """Подставляет значения из окружения вместо переменных."""

    return re.sub(r'\$([^$\s\'"]+)',
                  lambda s: environment.get(s.group(1), ''),
                  word)


def get_words(string: str,
              environment: Dict[str, str]) -> Generator[str, None, None]:
    """Разбивает строку на слова и подставляет переменные."""

    for match in re.findall(r'([^\s"\']+)|"([^"]*)"|\'([^\']*)\'', string):
        single_quoted_word = match[2]
        if single_quoted_word:
            yield single_quoted_word
        else:
            word = max(match)
            yield variable_expansion(word, environment)


def name_args(command: str, environment: Dict[str, str]) -> CommandArgs:
    """Достаёт имя команды и её аргументы."""

    match = re.fullmatch(r'(\S+)=([^\s"\']+|"[^"]*"|\'[^\']*\')', command)
    if match:
        variable = match.group(1)
        value = match.group(2)
        value = next(get_words(value, environment))
        return CommandArgs('=', [variable, value])

    name, *args = list(get_words(command, environment))
    return CommandArgs(name, args)


def parse(line: str, environment: Dict[str, str]) -> List[CommandArgs]:
    """Парсит строку в список команд и их аргументов."""

    commands = filter(None, re.split(r'\s+\|\s+', line.strip()))
    return [name_args(command, environment) for command in commands]
