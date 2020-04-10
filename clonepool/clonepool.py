#!/usr/bin/env python3

'''
Address len 1 means w fully connected graphs
'''
from collections import defaultdict
import sys

import click
import numpy as np

from clonepool.utils import set_up_pools, simulate_pool, resolve_samples


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
    help='Number of samples (required)')
@click.option(
    '-r', '--replicates', default=2, type=int,
    help='Number of sample replicates [2]')
@click.option(
    '-p', '--prevalence', default=0.05, type=float,
    help='Expected prevalence [0.05]')
@click.option(
    '-P', '--pool-size', required=True, type=int,
    help='How many samples go into each pool (required)')
@click.option(
    '-w', '--pool-count', default=94, type=int,
    help='Number of pools [94]')
@click.option(
    '-o', '--layout', required=True, default='layout',
    help='Path to layout')
@click.option(
    '--simulate', is_flag=True,
    help='Simulate pool results')
def layout(prevalence, pool_size, pool_count, replicates, samples, layout, simulate):
    
    max_sample_support = int(np.floor((pool_size * pool_count) / replicates))
    
    assert samples <= max_sample_support, \
    f'The chosen parameters support a maximum of {max_sample_support} samples'
    
    pool_log = set_up_pools(pool_count, samples, pool_size, replicates)

    with open(layout, 'w+') as file:
        file.write('pool\tresult\tsamples\n')  # header

        if simulate:
            positive_pools = simulate_pool(
                pool_count, replicates, pool_size, prevalence)
        
            state = ['+' if (k in positive_pools) else '-' for k in pool_log]
            for (k, v), s in zip(pool_log.items(), state):
                file.write(
                    f'{k}\t{s}\t{",".join([str(i) for i in sorted(v)])}\n')

        else:
            for k, v in sorted(pool_log.items()):
                file.write(
                    f'{k}\t-\t{",".join([str(i) for i in sorted(v)])}\n')


@click.command()
@click.option(
    '--layout', default=None,
    help='Path to +/- pool results')
@click.option(
    '--result', default=None,
    help='Path to +/- sample results')
def resolve(layout, result):
    pool_log = defaultdict(list)    # pool: [samples]
    sample_map = defaultdict(list)  # sample: [pools]
    positive_pools = []

    with open(layout, 'r') as file:
        _ = next(file)  # header
        for line in file:
            pool, state, samples = line.strip().split('\t')
            samples = samples.split(',')

            if state == '+':
                positive_pools.append(pool)

            pool_log[pool].extend(samples)

            for i in samples:
                sample_map[i].append(pool)

    effective_samples, states = resolve_samples(
        pool_log, sample_map, positive_pools, len(sample_map), len(pool_log))
    print(f'Effective number of samples: {effective_samples}')
    
    with open(result, 'w+') as out:
        out.write('sample\tresult\n')
        # TODO: sort items?
        for i, j in states.items():
            if j == -1:
                out.write(f'{i}\t-\n')
            elif j == 0:
                out.write(f'{i}\tNA\n')
            elif j == 1:
                out.write(f'{i}\t+\n')
            else:
                print('Something weird just happend')
                sys.exit(-1)











# if __name__ == '__main__':
#     laylayout()


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

