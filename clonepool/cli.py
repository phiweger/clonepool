# cli.py

import click

from clonepool.clonepool import layout, simulate, resolve

@click.command('layout')
@click.option(
    '-n', '--samples', required=False, type=int,
    help='Number of samples')
@click.option(
    '-P', '--pool-size', required=True, type=int,
    help='How many samples go into each pool')
@click.option(
    '-r', '--replicates', default=2, type=int,
    help='Number of replicates per sample [2]')
@click.option(
    '-w', '--pool-count', default=94, type=int,
    help='Number of pools (wells) [94]')
@click.argument(
    'layout_file', required=False, default='-', type=click.File('w'))
def layout_cli(pool_size, pool_count, replicates, samples, layout_file):
    '''
    Generate pool layout. This assigns all samples to their respecitve pools.

    Writes to STDOUT or the given layout file.
    '''
    layout(pool_size, pool_count, replicates, samples, layout_file)


@click.command('simulate')
@click.option(
    '-l', '--layout', required=True, type=click.File('r'),
    help='Path to input file containing pool layout')
@click.option(
    '-p', '--prevalence', default=0.05, type=click.FloatRange(0, 1),
    help='Sample prevalence used for simulation [0.05]')
@click.option(
    '-P', '--false-positives', default=0, type=click.FloatRange(0, 1),
    help='Fraction of false-positive pools [0]')
@click.option(
    '-N', '--false-negatives', default=0, type=click.FloatRange(0, 1),
    help='Fraction of false-negative pools [0]')
@click.argument(
    'out_layout_file', required=False, default='-', type=click.File('w'))
def simulate_cli(layout, prevalence, false_positives, false_negatives, out_layout_file):
    '''
    For a given pool layout, simulate a test run. Uses a defined sample
    prevalence to determine a random set of positive samples and,
    successively, flags all pools as positive containing any of these samples.

    Writes to STDOUT or the given layout file.
    '''
    simulate(layout, prevalence, false_positives, false_negatives, out_layout_file)


@click.command('resolve')
@click.option(
    '--layout', '-l', required=True, type=click.File('r'),
    help='Path to layout file containing +/- pool results')
@click.argument(
    'sample_results_file', required=False, default='-', type=click.File('w'))
def resolve_cli(layout, sample_results_file):
    '''
    Resolve sample status from pool results. As this is not always
    possible, some samples may remain in an uncertain state.
    Writes to STDOUT or the given results file.
    '''
    resolve(layout, sample_results_file)
