from collections import defaultdict
import sys

import click
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor


from clonepool.utils import (
    set_up_pools,
    simulate_pools,
    resolve_samples,
    make_sample_map,
)

import clonepool.globalopts as opt
opt.verbose = False                     # disable printing of status messages


def one_test_run(replicates, pool_size, prevalence):

    pool_count = 94
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


def test_run_loop(i):
    csv_out = list()            # aggregate output here
    for replicates in [1, 2, 3, 4, 5]:
        for pool_size in [3, 5, 10, 20]:
            for prevalence in np.arange(0.01, 0.3, 0.01):
                prevalence = np.round(prevalence, 2)
                effective_samples = one_test_run(
                    replicates, pool_size, prevalence)
                csv_out.append(f'{replicates},{pool_size},{prevalence},'
                               f'{effective_samples}\n')
    return "".join(csv_out)


def test_run_loop_wrap(i):
    print(f'Starting iteration {i}')
    return test_run_loop(i)


##############################################################################
##                                   Main                                   ##
##############################################################################

# do_multiprocess = True
do_multiprocess = False

with open('sim.csv', 'w+') as out:
    out.write('replicates,pool_size,prevalence,effective_samples\n')
    iterations = 100

    if do_multiprocess:
        # Set max_workers to None to auto-detect cpu cores.
        with ProcessPoolExecutor(max_workers=None) as executor:
            print(f'Executing {iterations} simulation iterations ...')
            for csv_output_run in executor.map(
                                        test_run_loop_wrap, range(iterations)):
                out.write(csv_output_run)
    else:
        for i in tqdm(range(iterations)):
            out.write( test_run_loop(i) )

# EOF
