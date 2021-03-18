from cli.interpreter import run
from cli.commands import SUCCESS, FAIL


def test_cat(capsys):
    assert run('cat LICENSE kek') == FAIL
    out, err = capsys.readouterr()
    assert out.startswith('MIT License')
    assert err == 'cat: kek: No such file or directory\n'


def test_echo(capsys):
    assert run('echo Hello,            world!') == SUCCESS
    out, err = capsys.readouterr()
    assert out == 'Hello, world!\n'
    assert err == ''


def test_wc(capsys):
    assert run('wc LICENSE .gitignore kek') == FAIL
    out, err = capsys.readouterr()
    assert out.startswith('21\t169\t1075\tLICENSE')
    assert out.endswith('150\t397\t2874\ttotal\n')
    assert err == 'wc: kek: No such file or directory\n'


def test_pwd(capsys):
    assert run('pwd') == SUCCESS
    out, err = capsys.readouterr()
    assert out.endswith('cli\n')
    assert err == ''


def test_external(pytestconfig):
    capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')
    capmanager.suspend_global_capture(in_=True)
    assert run('flake8') == SUCCESS
    capmanager.resume_global_capture()


def test_grep_i(capsys):
    assert run('grep -i DEF cli/interpreter.py | wc') == SUCCESS
    out, err = capsys.readouterr()
    assert out.startswith('3\t')
    assert err == ''

    assert run('grep DEF cli/interpreter.py') == FAIL
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''


def test_grep_w(capsys):
    assert run('grep grep cli/commands.py | wc') == SUCCESS
    out, err = capsys.readouterr()
    count1, *_ = map(int, out.split())
    assert err == ''
    assert run('grep -w grep cli/commands.py | wc') == SUCCESS
    out, err = capsys.readouterr()
    count2, *_ = map(int, out.split())
    assert err == ''
    assert count1 > count2


def test_grep_A(capsys):
    assert run('grep \'def .*ca\' -A 3 cli/commands.py kek') == FAIL
    out, err = capsys.readouterr()
    assert out.startswith('cli/commands.py')
    assert err == 'grep: kek: No such file or directory\n'
