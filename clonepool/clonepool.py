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


# -n, --samples: number of samples
# -r, --replicates: number of replicates per sample [2] <-- default value
# -p, --prevalence: prevalence of condition in samples [0.05]
# -P, --pool-size: number of samples per pool
# -m, --pool-count: total number of pools to be tested [94]
# -l, --laylayout: path to pool laylayout file specifying the assignment of
#               samples to pools (TODO description of format)
# -r, --pool-results: path to the file containing the positive / negative
#               test result for each pool (TODO description of format)
@click.command()
@click.option(
    '-n', '--samples', required=True, type=int,
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
# @click.option(
#     '-o', '--layout', required=True, default='layout',
#     help='File to which the generated layout is written')
@click.argument(
    'layout_file', required=False, default='-', type=click.File('w'))
@click.option(
    '--simulate', '-s', is_flag=True,
    help='Simulate pool results from random samples')
@click.option(
    '-p', '--prevalence', default=0.05, type=float,
    help='Sample prevalence used for simulation [0.05]')
def layout(prevalence, pool_size, pool_count, replicates, samples, layout_file, simulate):
    '''
    Generate pool layout. This assigns all samples to their respecitve pools.
    Writes to STDOUT or the given layout file.
    '''

    max_sample_support = int(np.floor((pool_size * pool_count) / replicates))

    assert samples <= max_sample_support, \
    f'The chosen parameters support a maximum of {max_sample_support} samples'

    pool_log = set_up_pools(pool_count, samples, pool_size, replicates)

    positive_pools = \
        simulate_pools(pool_log, samples, prevalence) if simulate else set()
    state = ['+' if (pool in positive_pools) else '-' for pool in pool_log]

    write_layout_file(layout_file, pool_log, state)


def write_layout_file(layout_file, pool_log, state):
    layout_file.write('pool\tresult\tsamples\n')        # write header line

    # Write sorted list of pools, samples, and state.
    for (pool, samples), state in sorted(zip(pool_log.items(), state)):
        sorted_samples = ",".join( [str(i) for i in sorted(samples)] )
        layout_file.write(f'{pool}\t{state}\t{sorted_samples}\n')

def read_layout_file(layout_file):
    '''
    Read layout / pool results file.
    '''
    pool_log       = {}                     # pool: [samples]
    positive_pools = set()

    _ = next(layout_file)                   # skip header

    for line in layout_file:
        pool, state, samples_csv = line.strip().split('\t')
        pool    = int(pool)
        samples = [int(sample) for sample in samples_csv.split(',')]

        if state == '+':
            positive_pools.add(pool)

        pool_log[pool] = set(samples)

    return pool_log, positive_pools

@click.command()
def simulate():
    '''
    For a given pool layout, simulate a test run. Uses a defined sample
    prevalence to determine a random set of positive samples and,
    successively, flags all pools as positive containing any of these samples.
    '''
    pass


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
    # Read layout file including pool test results.
    pool_log, positive_pools = read_layout_file(layout)

    # Resolve samples.
    sample_map = make_sample_map(pool_log)
    effective_samples, states = resolve_samples(
        pool_log, sample_map, positive_pools, len(sample_map), len(pool_log))
    print(f'Effective number of samples: {effective_samples}')

    # Print / write results.
    sample_results_file.write('sample\tresult\n')
    for sample, state in sorted(states.items()):
        if state == -1:
            sample_results_file.write(f'{sample}\t-\n')
        elif state  == 0:
            sample_results_file.write(f'{sample}\tNA\n')
        elif state  == 1:
            sample_results_file.write(f'{sample}\t+\n')
        else:
            print('The state of a pool should be -1, 0 or 1 -- it is neither. This should not have happened, please open an issue so we can find out why this happens.')
            sys.exit(-1)


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

