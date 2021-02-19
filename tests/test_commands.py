import pytest
from cli.interpreter import run
from cli.commands import SUCCESS, FAIL


def test_cat(capsys):
    exitCode = run('cat LICENSE kek')
    out, err = capsys.readouterr()
    assert exitCode == FAIL
    assert out.startswith('MIT License')
    assert err == 'cat: kek: No such file or directory\n'


def test_echo(capsys):
    exitCode = run('echo Hello,            world!')
    out, err = capsys.readouterr()
    assert exitCode == SUCCESS
    assert out == 'Hello, world!\n'
    assert err == ''


def test_wc(capsys):
    exitCode = run('wc LICENSE .gitignore kek')
    out, err = capsys.readouterr()
    assert exitCode == FAIL
    assert out.startswith('21\t169\t1075\tLICENSE')
    assert out.endswith('150\t397\t2874\ttotal\n')
    assert err == 'wc: kek: No such file or directory\n'


def test_pwd(capsys):
    exitCode = run('pwd')
    out, err = capsys.readouterr()
    assert exitCode == SUCCESS
    assert out.endswith('cli\n')
    assert err == ''
