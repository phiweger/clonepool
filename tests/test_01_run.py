# test_01_run.py
# Test whether the command line tool can be executed.

import pytest
from subprocess import run

def test_prog_help():
    completed = run(['clonepool',  '--help'])
    assert completed.returncode == 0
