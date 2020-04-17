# clonepool/utils.py

import sys
from collections import defaultdict, Counter
from itertools import combinations

import networkx as nx
import numpy as np
from more_itertools import partition
import clonepool.globalopts as opt


def set_up_pools(npools, nsamples, nreplicates):
    pool_size    = int(np.ceil(nsamples * nreplicates / npools))
    pool_cnt     = [pool_size] * npools           # count free slots per pool
    pool_cnt_sum =  pool_size  * npools
    pool_idx     = list(range(npools))            # [0, ..., npools-1]
    pool_probs   = [0] * npools                   # init list of length npools
    pool_log     = [set() for _ in range(npools)] # which sample in which pool?

    try:
        for sample in range(nsamples):
            # Weigh pools by number of free sample slots.
            # Obtain probs for each pool by dividing by total # of free slots.
            for pool, count in enumerate(pool_cnt):
                pool_probs[pool] = count / pool_cnt_sum

            # Choose nreplicates many distinct pool.
            address = np.random.choice(
                pool_idx, nreplicates, replace=False, p=pool_probs)

            # Reduce free slots for chosen pools and add samples to pool_log.
            for pool in address:
                pool_cnt[pool] -= 1         # once 0, it wont be sampled again
                pool_log[pool].add(sample)

            pool_cnt_sum -= nreplicates     # update sum of free slots

    except ValueError:
        # We had bad luck with sampling, there are less than nreplicates
        # many non-full pools (but we do have enough slots in the remaining
        # pools!).
        nonfull_pools, full_pools = [set(iter) for iter in partition(
                                     lambda i: pool_cnt[i]==0, pool_idx)]

        # Process all remaining samples.
        for sample in range(sample, nsamples):
            nnon_full = len(nonfull_pools)

            # Take as many non-full pools as we have, and add as many full
            # pools as neccessary to get enough replicates.
            address = list(nonfull_pools) + list(np.random.choice(
                    list(full_pools), nreplicates-nnon_full, replace=False))

            # Add samples to pool_log as above.
            for pool in address:
                pool_log[pool].add(sample)

            # Book-keeping: keep track of new full pools.
            new_full_pools = set()
            for pool in nonfull_pools:
                pool_cnt[pool] -= 1
                if pool_cnt[pool] == 0:         # pool is now full
                    new_full_pools.add(pool)
            full_pools.update(new_full_pools)
            nonfull_pools -= new_full_pools

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
    for pool, samples in enumerate(pool_log):
        for sample in samples:
            sample_map[sample].add(pool)
    return sample_map


def resolve_samples(pool_log, sample_map, positive_pools, nsamples, npools):
    # Sample state: 0 == uncertain, +1 == pos, -1 == neg
    sample_state = {sample: 0 for sample in sample_map}

    # First, mark all samples from negative pools as negative.
    for pool, samples in enumerate(pool_log):
        if pool not in positive_pools:
            for sample in samples:
                sample_state[sample] = -1  # negative

    # Now, detect positives: only possible if exactly one sample in the pool
    # is uncertain and all others are negative.
    for pool, samples in enumerate(pool_log):
        if pool in positive_pools:
            uncertain_samples = [s for s in samples if sample_state[s] != -1]
            if len(uncertain_samples) == 1:
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

    # Simulate positive samples
    positive_samples = sample_pos_samples(nsamples, npositive)
    eprint(f'Adding {npositive} pos. samples: {sorted(positive_samples)}')

    # Which pools become positive as a consequence?
    sample_map     = make_sample_map(pool_log)
    positive_pools = get_pos_pools(sample_map, positive_samples)

    # Introduce false-negative pools.
    npos_pools = len(positive_pools)
    nfalse_neg = int(np.round(false_neg * npos_pools))
    false_neg_pools = sample_from(list(positive_pools), nfalse_neg)
    eprint(f'Adding {npos_pools} pos. pools: {sorted(positive_pools)}.')
    eprint(f'Adding {nfalse_neg} false-neg. pools: {sorted(false_neg_pools)}')

    # Introduce false-positive pools.
    nneg_pools = len(pool_log) - npos_pools
    nfalse_pos = int(np.round(false_pos * nneg_pools))
    if nfalse_pos > 0:
        negative_pools = {p for p in pool_log if p not in positive_pools}
        false_pos_pools = sample_from(list(negative_pools), nfalse_pos)
        positive_pools.update(false_pos_pools)
        eprint(f'Adding {nfalse_pos} false-pos. pools: {sorted(false_pos_pools)}')

    # Remove false-negatives only after picking false-positives from it. This
    # prevents re-inserting a pool as "false-positive" that has been removed
    # before as a false negative.
    positive_pools -= false_neg_pools

    return positive_pools, positive_samples


def eprint(*args, **kwargs):
    '''
    Behaves exactly like regular print(), but prints to STDERR.
    Cf. https://stackoverflow.com/a/14981125
    '''
    if opt.verbose:
        print(*args, file=sys.stderr, **kwargs)


def get_false_pos_neg_rates(sample_state, true_pos_samples):
    '''
    Given a dict containing test results (+1 for positive, -1 for negative,
    and 0 for uncertain), and the set of the truly positive samples (ground
    truth), compute false positive and false negative rates / ratios.
    '''
    # Count positives, negatives, false positives, and false negatives.
    npos, nfalse_pos, nneg, nfalse_neg = 0, 0, 0, 0
    for sample, state in sample_state.items():
        if state == +1:
            npos += 1               # samples resolved as positive
            if sample not in true_pos_samples:
                nfalse_pos += 1     # samples *incorrectly* resolved as pos
        elif state == -1:
            nneg += 1               # samples resolved as negative
            if sample in true_pos_samples:
                nfalse_neg += 1     # samples *incorrectly* resolved as neg

    # Calculate rounded false pos/neg rates.
    digits = 3                  # round to that many digits
    false_pos_rate = np.round(nfalse_pos / nneg, digits) if nneg > 0 else 0
    false_neg_rate = np.round(nfalse_neg / npos, digits) if npos > 0 else 0

    # TODO need to weight the FPR / FNR with the fraction of resolved samples,
    # where the unresolved samples have the FPR / FNR of the pool test
    # procedure.

    # TODO aggregate results in something like collections.namedtuple()

    return false_pos_rate, false_neg_rate, npos, nneg


def read_layout_file(layout_file):
    '''
    Read layout / pool results file. Returns the pool--sample map (which
    samples does each pool contain?) as well as the sets of positive pools
    (with state '+') and positive samples (marked with a star '*').
    '''
    pool_log       = []                     # pool: [samples]
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

        pool_log.append( set(samples) )

    return pool_log, pos_pools, pos_samples


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
    for pool, samples in enumerate(pool_log):
        state = '+' if (pool in pos_pools) else '-'
        # Sort samples and add a '*' to positive ones.
        samples_starred = [(str(i)+'*' if i in pos_samples else str(i))
                           for i in sorted(samples)]
        samples_csv     = ",".join(samples_starred)
        layout_file.write(f'{pool}\t{state}\t{samples_csv}\n')


# EOF
