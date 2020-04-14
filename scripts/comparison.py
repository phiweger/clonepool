from collections import defaultdict
import sys

import click
import numpy as np
from tqdm import tqdm

from clonepool.utils import (
    set_up_pools,
    simulate_pools,
    resolve_samples,
    make_sample_map,
)


def one_test_run(replicates, pool_size, prevalence):

    pool_count = 50
    false_positives = 0
    false_negatives = 0

    samples = int(np.floor((pool_size * pool_count) / replicates))

    pool_log = set_up_pools(pool_count, samples, pool_size, replicates)
    positive_pools = set()              # none positive


    nsamples = 1 + max(
            [max(pool_samples) for pool_samples in pool_log.values()])

    # Sample new positive pools.
    positive_pools = simulate_pools(
            pool_log, nsamples, prevalence, false_positives, false_negatives)


    # Resolve samples.
    sample_map = make_sample_map(pool_log)

    effective_samples, states = resolve_samples(
        pool_log, sample_map, positive_pools, len(sample_map), len(pool_log))
    
    return effective_samples


with open('sim.csv', 'w+') as out:
    out.write('replicates,pool_size,prevalence,effective_samples\n')

    for _ in tqdm(range(100)):
        for replicates in [1, 2, 3, 4, 5]:
            for pool_size in [3, 5, 10, 20]:
                for prevalence in np.arange(0.01, 0.3, 0.01):
                    effective_samples = one_test_run(
                        replicates, pool_size, prevalence)
                    
                    out.write(f'{replicates},{pool_size},{prevalence},{effective_samples}\n')
    



