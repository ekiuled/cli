from cli.interpreter import run
from cli.commands import SUCCESS


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


def test_command_var(capsys):
    assert run('c=echo') == SUCCESS
    assert run('b=on') == SUCCESS
    assert run('$c pyth$b') == SUCCESS
    out, err = capsys.readouterr()
    assert out == 'python\n'
    assert err == ''


def test_quotes_cat(capsys):
    assert run('a=LICENSE') == SUCCESS
    assert run('b=README.md') == SUCCESS
    assert run('cat "$a" \'$b\' | wc') == SUCCESS
    out, err = capsys.readouterr()
    assert out == '21\t169\t1075\n'
    assert err == 'cat: $b: No such file or directory\n'


def test_quotes_echo(capsys):
    assert run('a=aa') == SUCCESS
    assert run('b=bb') == SUCCESS
    assert run('echo "$a  $b$d" \' $b\'') == SUCCESS
    out, err = capsys.readouterr()
    assert out == 'aa  bb  $b\n'
    assert err == ''


def test_assignment_quotes(capsys):
    assert run('c=123') == SUCCESS
    assert run('b="a\'$c\'e "') == SUCCESS
    assert run('echo "$b"') == SUCCESS
    out, err = capsys.readouterr()
    assert out == "a'123'e \n"
    assert err == ''

    assert run('c=123') == SUCCESS
    assert run('b=\'a"$c"e \'') == SUCCESS
    assert run('echo "$b"') == SUCCESS
    out, err = capsys.readouterr()
    assert out == 'a"$c"e \n'
    assert err == ''
