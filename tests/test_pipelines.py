from cli.interpreter import run
from cli.commands import SUCCESS


def test_cat_wc(capsys):
    assert run('cat LICENSE kek | wc') == SUCCESS
    out, err = capsys.readouterr()
    assert out == '21\t169\t1075\n'
    assert err == 'cat: kek: No such file or directory\n'


def test_echo_cat(capsys):
    assert run('echo meow | cat') == SUCCESS
    out, err = capsys.readouterr()
    assert out == 'meow\n'
    assert err == ''
