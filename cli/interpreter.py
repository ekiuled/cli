from collections import defaultdict
from cli.commands import ExitCode, SUCCESS, Cat, Echo, Wc, Pwd, Exit
from cli.parser import parse
import sys
import os


environment = defaultdict(str)
commands = {'cat': Cat(),
            'echo': Echo(),
            'wc': Wc(),
            'pwd': Pwd(),
            'exit': Exit()}


def run(line: str) -> ExitCode:
    pipeline = parse(line)

    if not pipeline:
        return SUCCESS

    if len(pipeline) == 1:
        command, args = pipeline[0]
        ec = commands[command].call(sys.stdin, sys.stdout, sys.stderr, args)
        return ec

    prev_inp = sys.stdin
    prev_command, prev_args = pipeline[0]

    for command, args in pipeline[1:]:
        inp, out = os.pipe()
        commands[prev_command].call(prev_inp, out, sys.stderr, prev_args)
        prev_inp, prev_command, prev_args = inp, command, args

    commands[prev_command].call(prev_inp, sys.stdout, sys.stderr, prev_args)
