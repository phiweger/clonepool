# test_01_run.py
# Test whether the help can be invoked for the tool's commands.

import pytest
from subprocess import run

def run_prog_cmd_help(cmd):
    run(['clonepool', cmd, '--help'])

def test_layout():
    run_prog_cmd_help('layout')

def test_simulate():
    run_prog_cmd_help('simulate')

def test_resolve():
    run_prog_cmd_help('resolve')
