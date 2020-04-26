'''
CLI

https://kushaldas.in/posts/building-command-line-tools-in-python-with-click.html
'''
import click

from clonepool.clonepool import layout_cli, simulate_cli, resolve_cli

# Do not sort the command list alphabetically, but use order in which commands
# are added.
class UnsortedGroup(click.Group):
    def list_commands(self, ctx):
        return self.commands

cli = UnsortedGroup()

cli.add_command(layout_cli)
cli.add_command(simulate_cli)
cli.add_command(resolve_cli)
