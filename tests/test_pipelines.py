from cli.interpreter import run
from cli.commands import SUCCESS


def test_cat_wc(capsys):
    exitCode = run('cat LICENSE kek | wc')
    out, err = capsys.readouterr()
    assert exitCode == SUCCESS
    assert out == '21\t169\t1075\n'
    assert err == 'cat: kek: No such file or directory\n'


def test_echo_cat(capsys):
    exitCode = run('echo meow | cat')
    out, err = capsys.readouterr()
    assert exitCode == SUCCESS
    assert out == 'meow\n'
    assert err == ''
