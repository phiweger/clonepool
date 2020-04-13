import sys
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

def sample_pos_samples(nsamples, npositives):
    return sample_from_range(nsamples, npositives)

def sample_from_range(length, sample_size):
    '''
    Construct an int range of the given length n, ranging from 0 to n-1, and
    sample sample_size many *different* items from it in a set.
    '''
    return sample_from(np.arange(0, length), sample_size)

def sample_from(obj_list, sample_size):
    '''
    Sample sample_size many *different* items from the given list. Return it
    as a set.
    '''
    return set(np.random.choice(
        obj_list,
        size=sample_size,
        replace=False))

def get_pos_pools(sample_map, positive_samples):
    positive_pools = set()
    for positive_sample in positive_samples:
        for pool in sample_map[positive_sample]:
            positive_pools.add(pool)
    return positive_pools

def make_sample_map(pool_log):
    sample_map = defaultdict(set)
    for pool, samples in pool_log.items():
        for sample in samples:
            sample_map[sample].add(pool)
    return sample_map


def resolve_samples(pool_log, sample_map, positive_pools, nsamples, npools):
    # Sample state: 0 == uncertain, +1 == pos, -1 == neg
    sample_state = {sample: 0 for sample in sample_map}

    # First, mark all samples from negative pools as negative.
    for pool, samples in pool_log.items():
        if pool not in positive_pools:
            for sample in samples:
                sample_state[sample] = -1  # negative

    # Now, detect positives: only possible if exactly one sample in the pool
    # is uncertain and all others are negative.
    for pool, samples in pool_log.items():
        if pool in positive_pools:
            uncertain_samples = [s for s in samples if sample_state[s] != -1]
            if len(uncertain_samples) == 1:
                
                # debug
                # print(uncertain_samples)
                # if not '*' in uncertain_samples[0]:
                #     u = sample_map[uncertain_samples[0]]
                #     for i in u:
                #         print(pool_log[i])
                
                sample_state[uncertain_samples[0]] = 1  # positive

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
    return result, sample_state


def simulate_pools(pool_log, nsamples, prev, false_pos = 0, false_neg = 0):
    '''
    Given a pool--sample map, the number of samples, and a sample
    prevalence, draw positive samples randomly according to their
    prevalence and determine the positive pools from them.
    '''

    npositive = int(np.round(prev * nsamples))

    # g = nx.Graph()
    # g.add_nodes_from(samples)

    # Simulate positive samples
    positive_samples = sample_pos_samples(nsamples, npositive)

    eprint(f'Adding {npositive} positive samples: {sorted(positive_samples)}')

    # Which pools become positive as a consequence?
    sample_map     = make_sample_map(pool_log)
    positive_pools = get_pos_pools(sample_map, positive_samples)

    # Introduce false-negative pools.
    npos_pools = len(positive_pools)
    nfalse_neg = int(np.round(false_neg * npos_pools))
    false_neg_pools = sample_from(list(positive_pools), nfalse_neg)
    eprint(f'Adding {npos_pools} positive pools: {sorted(positive_pools)}.')
    eprint(f'Adding {nfalse_neg} false-negative pools: {sorted(false_neg_pools)}')

    # Introduce false-positive pools.
    nneg_pools = len(pool_log) - npos_pools
    nfalse_pos = int(np.round(false_pos * nneg_pools))
    if nfalse_pos > 0:
        negative_pools = {p for p in pool_log if p not in positive_pools}
        false_pos_pools = sample_from(list(negative_pools), nfalse_pos)
        positive_pools.update(false_pos_pools)
        eprint(f'Adding {nfalse_pos} false-positive pools: {sorted(false_pos_pools)}')

    # Remove false-negatives only after picking false-positives from it. This
    # prevents re-inserting a pool as "false-positive" that has been removed
    # before as a false negative.
    positive_pools -= false_neg_pools

    return positive_pools


# Print to STDERR, cf. https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def simulation_step(index):
    print(f'starting iteration {index}')
    csv_output = list()
    for maxpool in [3, 5, 10, 20, 30, 40]:
        for nrep in [1, 2, 3, 4, 5]:
            for p in np.arange(0.01, 0.3, 0.01):
                # WARNING: THIS IS UNTESTED with the new code.
                pool_log = set_up_pools(npools, nsamples, maxpool, nreplicates)
                positive_pools = simulate_pools(pool_log, nsamples, p)
                sample_map = make_sample_map(pool_log)
                samples, states = resolve_samples(
                        pool_log, sample_map, positive_pools, nsamples, npools)
                    #npools=94, nreplicates=nrep, maxpool=maxpool, p=p)
                # spr .. samples per reactions
                #out.write(f'{index},{maxpool},{nrep},{p},{samples}\n')
                csv_output.append(f'{index},{maxpool},{nrep},{p},{samples}\n')
    return csv_output


