'''
Address len 1 means npools fully connected graphs
'''

from collections import defaultdict, Counter
from itertools import combinations

import networkx as nx
import numpy as np
from tqdm import tqdm


# nsamples = 500
# maxpool = 10
# nreplicates = 1  # == degree of each node
# p = 0.1
# npools = 94


def simulate_pool(npools, nreplicates, maxpool, p):

    nsamples = int(maxpool * npools / nreplicates)
    npositive = int(np.floor(p * nsamples))
    # maxpool = np.ceil(nreplicates * nsamples / npools)

    # print(f'{nsamples} samples can be processed')
    # print(f'{npositive} should be positive')

    samples = np.arange(0, nsamples)
    pool_cnt = {k: maxpool for k in np.arange(0, npools)}
    pool_log = defaultdict(list)
    
    # g = nx.Graph()
    # g.add_nodes_from(samples)

    # Set up pools
    for i in samples:
        pool = []
        cnt = maxpool
    
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
            pool_log[pool].append(i)



    # Simulate positive samples
    positive_samples = np.random.choice(
        np.arange(0, nsamples),
        size=npositive,
        replace=False)
    
    
    # Which pools become positive as a consequence?
    positive_pools = set()
    for k, v in pool_log.items():
        # Samples 0 throuugh 19 are Ccov positive (0.02)
        for i in positive_samples:
            if i in v:
                positive_pools.add(k)
    # print(f'{len(positive_pools)} pools are positive ({round(len(positive_pools) / npools, 4)})')


    # Resolve
    sample_map = defaultdict(list)
    for i in samples:
        for k, v in pool_log.items():
            if i in v:
                sample_map[i].append(k)


    # If any pool in which the sample is contained is negative, the sample
    # is negative. If all pools the sample is in are positive, we cannot
    # resolve its state.
    # uncertain .. 1, resolved .. 0
    state = defaultdict(int)
    for k, v in sample_map.items():
        # ..., 492: [33, 48, 68], ...
        if all([(i in positive_pools) for i in v]):
            state[k] += 1
        else:
            state[k] += 0
    # TODO: all w/ 0 are negative, add to result
    old = sum(state.values())
    # print(f'{old} unresolved')
    # print(f'{old} samples cannot be resolved in first round')
    
    # Catch case where all is resolved straight away
    if old == 0:
        result = round(nsamples / npools, 4)
        return result
    
    # If not all samples are resolved, iterate until they are or the number
    # of unresolved samples converges (does not get smaller)
    while old > 0:
    
        for sample, _ in state.items():
            sample_pools = sample_map[sample]
            # assert len(sample_pools) == nreplicates
            
            for pool in sample_pools:
                s = [state[i] for i in pool_log[pool]]
                # if sum(s) > 0:
                #     print(s)
                if sum(s) == 1:
                    state[sample] = 0
        new = sum(state.values())
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


with open('sim.csv', 'w+') as out:
    for i in tqdm(range(25)):
        for maxpool in [3, 5, 10, 20]:
            for nrep in [1, 2, 3, 4, 5]:
                for p in np.arange(0.01, 0.3, 0.01):
                    samples = simulate_pool(
                        npools=94, nreplicates=nrep, maxpool=maxpool, p=p)
                    # spr .. samples per reactions
                    out.write(f'{i},{maxpool},{nrep},{p},{samples}\n')


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
    ylab('samples per reaction') +
    xlab('prevalence') +
    labs(color='replicates') +
    guides(color=guide_legend(override.aes=list(size=10)))

ggsave('sim.pdf', width=12, height=10, units='cm')
'''

