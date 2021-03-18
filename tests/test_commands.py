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
