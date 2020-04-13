#!/usr/bin/env python3

'''
Address len 1 means w fully connected graphs
'''
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
)


##############################################################################
##                                   Main                                   ##
##############################################################################


# Compute layoutput in parallel.
# for i in tqdm(range(25)):

'''
csv_layoutput = list()
cpu_count = None                # use None to autodetect, and 1 to debug
with ProcessPoolExecutor(max_workers=cpu_count) as executor:
    iter_count = 24
    print(f'Executing {iter_count} simulation iterations ...')
    for csv_layoutput_of_run in executor.map(simulation_step, range(iter_count)):
    # for i in range(iter_count):                   # use for debugging
    #     csv_layoutput_of_run = simulation_step(i)
        csv_layoutput.extend(csv_layoutput_of_run)

# Write layoutput to csv file.
print('Writing layoutput ... ',)
with open('sim.csv', 'w+') as layout:
    layout.write("".join(csv_layoutput))
print('done.')
'''


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
    max_sample_support = int(np.floor((pool_size * pool_count) / replicates))

    if samples:
        assert samples <= max_sample_support, \
        f'The chosen parameters support a maximum of {max_sample_support} samples'
    else:
        samples = max_sample_support

    # Generate pool layout and write it to output file.
    pool_log       = set_up_pools(pool_count, samples, pool_size, replicates)
    write_layout_file(layout_file, pool_log)


def write_layout_file(layout_file, pool_log, pos_pools=set(), pos_samples=set()):
    '''
    Write the given pool layout (i.e. which samples are assigned to which
    pool) to the given layout file handle. Also add the state of the pool
    (+/-) as inferred from the passed set of positive pools. If ommitted, all
    pools are assumed to be negative. If a set of positive samples is passed,
    add a star "*" to all positive samples to keep the ground truth encoded in
    the layout file.
    '''
    layout_file.write('pool\tresult\tsamples\n')        # write header line

    # Write sorted list of pools, samples, and state.
    for pool, samples in sorted(pool_log.items()):
        state = '+' if (pool in pos_pools) else '-'
        # Sort samples and add a '*' to positive ones.
        samples_starred = [(str(i)+'*' if i in pos_samples else str(i))
                           for i in sorted(samples)]
        samples_csv     = ",".join(samples_starred)
        layout_file.write(f'{pool}\t{state}\t{samples_csv}\n')


def read_layout_file(layout_file):
    '''
    Read layout / pool results file. Returns the pool--sample map (which
    samples does each pool contain?) as well as the sets of positive pools
    (with state '+') and positive samples (marked with a star '*').
    '''
    pool_log       = {}                     # pool: [samples]
    pos_pools   = set()
    pos_samples = set()

    _ = next(layout_file)                   # skip header

    for line in layout_file:
        pool, state, samples_csv = line.strip().split('\t')
        pool = int(pool)

        # Strip trailing '*' from samples and, if any, add to set of positives
        samples = []
        for sample_raw in samples_csv.split(','):
            sample = int(sample_raw.rstrip('*'))
            if sample_raw.endswith('*'):
                pos_samples.add(sample)
            samples.append(sample)

        if state == '+':
            pos_pools.add(pool)

        pool_log[pool] = set(samples)

    return pool_log, pos_pools, pos_samples

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
    # Read existing pool layout, discard old positive pools if any.
    pool_log, _, _ = read_layout_file(layout)

    # Find number of samples
    nsamples = 1 + max(
                [max(pool_samples) for pool_samples in pool_log.values()] )

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
# @click.option(
#     '--result', default=None,
#     help='Path to +/- sample results file')
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
        false_pos_rate, false_neg_rate = get_false_pos_neg_rates(
                sample_state, true_pos_samples)
        eprint(f'False-pos. rate: {false_pos_rate}')
        eprint(f'False-neg. rate: {false_neg_rate}')

    # Print / write results.
    sample_results_file.write('sample\tresult\n')
    for sample, state in sorted(sample_state.items()):
        state_symbol = '+' if state == +1 else '-' if state == -1 else 'NA'
        sample_results_file.write(f'{sample}\t{state_symbol}\n')


def get_false_pos_neg_rates(sample_state, true_pos_samples):
    nfalse_pos, nfalse_neg = 0, 0

    for sample, state in sample_state.items():
        if   state == +1 and sample not in true_pos_samples:
            nfalse_pos += 1
        elif state == -1 and sample in true_pos_samples:
            nfalse_neg += 1

    nsamples = len(sample_state)
    digits = 3                  # round to that many digits
    false_pos_rate = np.round(nfalse_pos / nsamples, digits)
    false_neg_rate = np.round(nfalse_neg / nsamples, digits)

    return false_pos_rate, false_neg_rate

# if __name__ == '__main__':
#     laylayout()


# Plot data using R / GGplot
'''r
library(ggplot2)
library(readr)

df <- read_csv('sim.csv', col_names=c('iter', 'maxpool', 'nrep', 'p', 'spr'))

ggplot(df, aes(x=p, y=spr, color=as.factor(nrep))) +
    geom_jitter(size=0.3) +
    scale_color_brewer(palette='Set2') +
    facet_wrap(~maxpool, scale='free_y') +
    theme_classic() +
    geom_hline(yintercept=1) +
    ylab('resolved samples per reaction') +
    xlab('prevalence') +
    labs(color='replicates') +
    guides(color=guide_legend(override.aes=list(size=10)))

ggsave('sim.pdf', width=12, height=10, units='cm')
'''

