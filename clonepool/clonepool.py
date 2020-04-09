#!/usr/bin/env python3

'''
Address len 1 means w fully connected graphs
'''
import sys

import click
import numpy as np

from clonepool.utils import set_up_pools, simulate_pool


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
    '-o', '--layout', required=True, default='layout.csv',
    help='Path to layout')
@click.option(
    '--simulate', default=None,
    help='Path to +/- simulated pool results')
def layout(prevalence, pool_size, pool_count, replicates, samples, layout, simulate):
    
    max_sample_support = int(np.floor((pool_size * pool_count) / replicates))
    
    assert samples <= max_sample_support, \
    f'The chosen parameters support a maximum of {max_sample_support} samples'
    
    pool_log = set_up_pools(pool_count, samples, pool_size, replicates)

    if simulate:
        positive_pools = simulate_pool(
            pool_count, replicates, pool_size, prevalence)
        
        with open(simulate, 'w+') as file:
            file.write('pool,result\n')
            state = ['+' if (k in positive_pools) else '-' for k in pool_log]
            for pool, s in zip(pool_log.keys(), state):
                file.write(f'{pool},{s}\n') 

    with open(layout, 'w+') as file:
        file.write('sample,pool\n')
        for k, v in pool_log.items():
            for i in v:
                file.write(f'{i},{k}\n')


@click.command()
def resolve():
    # TODO evaluate flag
    # result = resolve_samples_felix(pool_log, sample_map, positive_pools, nsamples, npools)
    print('foo')


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

