# test_01_run.py
# Test whether the help can be invoked for the tool's commands.

import pytest
from subprocess import run

def run_prog_cmd_help(cmd):
    completed = run(['clonepool', cmd, '--help'])
    assert completed.returncode == 0

@pytest.mark.parametrize("cmd", [
    'layout',
    'simulate',
    'resolve',
    pytest.param('foobar', marks=pytest.mark.xfail),   # this should fail
])
def test_cmd_help(cmd):
    run_prog_cmd_help(cmd)
