#!/usr/bin/env python3

'''
Address len 1 means npools fully connected graphs
'''

from collections import defaultdict, Counter
from itertools import combinations

import networkx as nx
import numpy as np
# from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


# nsamples = 500
# maxpool = 10
# nreplicates = 1  # == degree of each node
# p = 0.1
# npools = 94

def set_up_pools(npools, nsamples, maxpool, nreplicates):
    pool_cnt = {k: maxpool for k in np.arange(0, npools)} # how often each pool
    pool_log = defaultdict(set)                # which sample in which pool?

    for i in range(nsamples):
        try:
            address = np.random.choice(
                list(pool_cnt.keys()), nreplicates, replace=False)

            for pool in address:
                pool_cnt[pool] -= 1
                if pool_cnt[pool] == 0:
                    del pool_cnt[pool]

        except ValueError:
            # Cannot take a larger sample than population when 'replace=False'
            # Then random
            address = np.random.choice(
                list(np.arange(0, npools)), size=nreplicates, replace=False)
            # consequence: some pools are larger than maxpool

        for pool in address:
            # for node in pool_log[pool]:
            #     g.add_edge(i, node)
            pool_log[pool].add(i)

    return pool_log

def sample_pos_samples(nsamples, npositive):
    positive_samples_list = np.random.choice(
        np.arange(0, nsamples),
        size=npositive,
        replace=False)
    positive_samples = set(positive_samples_list)
    return positive_samples

def get_pos_pools(sample_map, positive_samples):
    positive_pools = set()
    for positive_sample in positive_samples:
        for pool in sample_map[positive_sample]:
            positive_pools.add(pool)
    # positive_pools = set()
    # for k, v in pool_log.items():
    #     # Samples 0 throuugh 19 are Ccov positive (0.02)
    #     for i in positive_samples:
    #         if i in v:
    #             positive_pools.add(k)
    # # print(f'{len(positive_pools)} pools are positive ({round(len(positive_pools) / npools, 4)})')
    return positive_pools

def make_sample_map(pool_log):
    sample_map = defaultdict(set)
    for pool, samples in pool_log.items():
        for sample in samples:
            sample_map[sample].add(pool)
    # sample_map = defaultdict(list)
    # for i in samples:
    #     for k, v in pool_log.items():
    #         if i in v:
    #             sample_map[i].append(k)
    return sample_map

def resolve_samples(pool_log, sample_map, positive_pools, nsamples, npools):
    # If any pool in which the sample is contained is negative, the sample
    # is negative. If all pools the sample is in are positive, we cannot
    # resolve its state.
    # uncertain .. 1, resolved .. 0
    sample_state = defaultdict(int)
    for sample, pools in sample_map.items():
        # ..., 492: [33, 48, 68], ...
        if all([(pool in positive_pools) for pool in pools]):
            sample_state[sample] += 1
        else:
            sample_state[sample] += 0
    # TODO: all w/ 0 are negative, add to result
    old = sum(sample_state.values())
    # print(f'{old} unresolved')
    # print(f'{old} samples cannot be resolved in first round')

    # Catch case where all is resolved straight away
    if old == 0:
        result = round(nsamples / npools, 4)
        return result

    # If not all samples are resolved, iterate until they are or the number
    # of unresolved samples converges (does not get smaller)
    while old > 0:

        for sample in sample_state:
            sample_pools = sample_map[sample]
            # assert len(sample_pools) == nreplicates

            for pool in sample_pools:
                s = [sample_state[i] for i in pool_log[pool]]
                # if sum(s) > 0:
                #     print(s)
                if sum(s) == 1:
                    sample_state[sample] = 0
        new = sum(sample_state.values())
        # print(new)
        if new == old:  # convergence
            # TODO: Export network view of the remaining samples, i.e.
            # two samples share a connection if they are in the same pool.
            # print(f'convergence at {new}')
            result = round(nsamples / (npools + new), 4)
            return result
        else:
            old = new
    # print(f'{new} samples remain unresolved')
    # All samples resolved
    # return new, mean_size_pool, len(positive_pools)
    result = round(nsamples / npools, 4)
    # print(f'Can process {result} samples per reaction')
    # If this falls below 1, it makees sense to just test each sample
    # individually w/o pooling
    return result

def resolve_samples_felix(pool_log, sample_map, positive_pools, nsamples, npools):
    sample_state     = defaultdict(int)         # +1 == pos, -1 == neg
    sample_queue     = set(sample_map.keys())   # start with all samples
    resolved_samples = set([1])                 # per iteration, start non-empty
    while len(resolved_samples) > 0:
        resolved_samples = set([])              # empty set
        for sample in sample_queue:
            sample_pools = sample_map[sample]
            if any([(pool not in positive_pools) for pool in sample_pools]):
                sample_state[sample] = -1               # sample is negative
                resolved_samples.add(sample)
            else:       # all pools of sample are positive
                # Check whether there is any pool where all other samples are
                # known to be negative. Then this sample must be positive.
                for sample_pool in sample_pools:
                    other_samples = pool_log[sample_pool].copy()
                    other_samples.remove(sample)
                    if all([sample_state[sample] == -1 for sample in other_samples]):
                        sample_state[sample] = +1       # sample is positive
                        resolved_samples.add(sample)
                        break       # we know what we want to know
        sample_queue -= resolved_samples        # remove resolved from queue

    nresolved  = len([s for s, state in sample_state.items() if state != 0])
    nuncertain = nsamples - nresolved

    result = round(nsamples / (npools + nuncertain), 4)
    return result


def simulate_pool(npools, nreplicates, maxpool, p):

    nsamples  = int(np.floor(maxpool * npools / nreplicates))
    npositive = int(np.floor(p * nsamples))

    # print(f'{nsamples} samples can be processed')
    # print(f'{npositive} should be positive')

    samples  = np.arange(0, nsamples)
    pool_log = set_up_pools(npools, nsamples, maxpool, nreplicates)

    # g = nx.Graph()
    # g.add_nodes_from(samples)

    # Simulate positive samples
    positive_samples = sample_pos_samples(nsamples, npositive)

    # Which pools become positive as a consequence?
    sample_map     = make_sample_map(pool_log)
    positive_pools = get_pos_pools(sample_map, positive_samples)

    # Resolve
    result = resolve_samples(    pool_log, sample_map, positive_pools, nsamples, npools)
    # result = resolve_samples_felix(pool_log, sample_map, positive_pools, nsamples, npools)


    return result

def simulation_step(index):
    print(f'starting iteration {index}')
    csv_output = list()
    for maxpool in [3, 5, 10, 20, 30, 40]:
        for nrep in [1, 2, 3, 4, 5]:
            for p in np.arange(0.01, 0.3, 0.01):
                samples = simulate_pool(
                    npools=94, nreplicates=nrep, maxpool=maxpool, p=p)
                # spr .. samples per reactions
                #out.write(f'{index},{maxpool},{nrep},{p},{samples}\n')
                csv_output.append(f'{index},{maxpool},{nrep},{p},{samples}\n')
    return csv_output


##############################################################################
##                                   Main                                   ##
##############################################################################

# Compute output in parallel.
# for i in tqdm(range(25)):
csv_output = list()
cpu_count = None                # use None to autodetect, and 1 to debug
with ProcessPoolExecutor(max_workers=cpu_count) as executor:
    iter_count = 24
    print(f'Executing {iter_count} simulation iterations ...')
    for csv_output_of_run in executor.map(simulation_step, range(iter_count)):
    # for i in range(iter_count):                   # use for debugging
    #     csv_output_of_run = simulation_step(i)
        csv_output.extend(csv_output_of_run)

# Write output to csv file.
print('Writing output ... ',)
with open('sim.csv', 'w+') as out:
    out.write("".join(csv_output))
print('done.')


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

