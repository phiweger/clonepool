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
    return np.random.choice(
        np.arange(0, nsamples),
        size=npositive,
        replace=False)

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
    # Sample state: 0 == uncertain, +1 == pos, -1 == neg
    sample_state = {sample: 0 for sample in sample_map}

    # First, mark all samples from negative pools as negative.
    for pool, samples in pool_log.items():
        if pool not in positive_pools:
            for sample in samples:
                sample_state[sample] = -1               # negative

    # Now, detect positives: only possible if exactly one sample in the pool
    # is uncertain and all others are negative.
    for pool, samples in pool_log.items():
        if pool in positive_pools:
            uncertain_samples = [s for s in samples if sample_state[s] == 0]
            if len(uncertain_samples) == 1:
                sample_state[uncertain_samples[0]] = +1         # positive

    # There is no iterative refinement. All negative samples can be detected
    # by looking at negative pools. Since the pools don't change their state,
    # no others will be found. Even detecting a positive sample will not help:
    # if there is another uncertain sample alongside a positive sample, it
    # could be either positive or negative.
    # For positive samples, it's the same. Detecting a positive sample cannot
    # yield new information to detect other positive samples.

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
    # result = resolve_samples(    pool_log, sample_map, positive_pools, nsamples, npools)
    
    # result = resolve_samples_felix(pool_log, sample_map, positive_pools, nsamples, npools)
    return positive_pools


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