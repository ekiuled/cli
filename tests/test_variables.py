from cli.interpreter import run
from cli.commands import SUCCESS  # , FAIL


def test_var_echo(capsys):
    assert run('a=123') == SUCCESS
    assert run('echo $a') == SUCCESS
    out, err = capsys.readouterr()
    assert out == '123\n'
    assert err == ''


def test_var_cat(capsys):
    assert run('a=EN') == SUCCESS
    assert run('b=SE') == SUCCESS
    assert run('cat LIC$a$b | wc') == SUCCESS
    out, err = capsys.readouterr()
    assert out == '21\t169\t1075\n'
    assert err == ''
