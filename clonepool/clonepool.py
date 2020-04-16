# clonepool/clonepool.py

from collections import defaultdict
import sys

import click
import numpy as np

from clonepool.utils import (
    set_up_pools,
    simulate_pools,
    resolve_samples,
    make_sample_map,
    eprint,
    get_false_pos_neg_rates,
    read_layout_file,
    write_layout_file,
)


@click.command()
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
def layout(pool_size, pool_count, replicates, samples, layout_file):
    '''
    Generate pool layout. This assigns all samples to their respecitve pools.

    Writes to STDOUT or the given layout file.
    '''
    # Check if sample count is valid.
    max_sample_support = int(np.floor((pool_size * pool_count) / replicates))
    if not samples:
        samples = max_sample_support
    else:
        if samples > max_sample_support:
            sys.exit( 'ERROR: The chosen parameters support a maximum of '
                     f'{max_sample_support} samples')

    # Generate pool layout and write it to output file.
    pool_log       = set_up_pools(pool_count, samples, pool_size, replicates)
    write_layout_file(layout_file, pool_log)


@click.command()
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
def simulate(layout, prevalence, false_positives, false_negatives, out_layout_file):
    '''
    For a given pool layout, simulate a test run. Uses a defined sample
    prevalence to determine a random set of positive samples and,
    successively, flags all pools as positive containing any of these samples.

    Writes to STDOUT or the given layout file.
    '''
    # Read existing pool layout, discard old positive pools / samples if any.
    pool_log, _, _ = read_layout_file(layout)

    # Find number of samples
    nsamples = 1 + max(
                [max(pool_samples) for pool_samples in pool_log.values()])

    # Sample new positive pools.
    positive_pools, positive_samples = simulate_pools(
            pool_log, nsamples, prevalence, false_positives, false_negatives)

    # Write layout including new pool results.
    write_layout_file(
            out_layout_file, pool_log, positive_pools, positive_samples)


@click.command()
@click.option(
    '--layout', '-l', required=True, type=click.File('r'),
    help='Path to layout file containing +/- pool results')
@click.argument(
    'sample_results_file', required=False, default='-', type=click.File('w'))
def resolve(layout, sample_results_file):
    '''
    Resolve sample status from pool results. As this is not always
    possible, some samples may remain in an uncertain state.
    Writes to STDOUT or the given results file.
    '''
    # Read layout file including pool test results and, possibly, a ground
    # truth set of positive samples
    pool_log, pos_pools, true_pos_samples = read_layout_file(layout)

    # Resolve samples.
    sample_map = make_sample_map(pool_log)
    effective_samples, sample_state = resolve_samples(
        pool_log, sample_map, pos_pools, len(sample_map), len(pool_log))
    eprint(f'Effective number of samples / test: {effective_samples}')

    # Evaluate ground truth if available.
    if len(true_pos_samples) > 0:
        false_pos_rate, false_neg_rate, npos, nneg = get_false_pos_neg_rates(
                sample_state, true_pos_samples)
        eprint(f'False-pos. rate resolved: {false_pos_rate} of {nneg} neg. samples')
        eprint(f'False-neg. rate resolved: {false_neg_rate} of {npos} pos. samples')

    # Print / write results.
    sample_results_file.write('sample\tresult\n')
    for sample, state in sorted(sample_state.items()):
        state_symbol = '+' if state == +1 else '-' if state == -1 else 'NA'
        sample_results_file.write(f'{sample}\t{state_symbol}\n')

# EOF
