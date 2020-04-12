'''
CLI

https://kushaldas.in/posts/building-command-line-tools-in-python-with-click.html
'''
import click

from clonepool.clonepool import layout, simulate, resolve


@click.group()
def cli():
    pass


cli.add_command(layout)
cli.add_command(simulate)
cli.add_command(resolve)
