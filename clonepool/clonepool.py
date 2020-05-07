# clonepool/clonepool.py

from collections import defaultdict
import sys

import numpy as np
from clonepool.utils import (
    set_up_pools,
    simulate_pools,
    resolve_samples,
    make_sample_map,
    eprint,
    get_false_pos_neg_rates,
    read_layout_file,
    write_layout_file,
)


def layout(pool_size, pool_count, replicates, samples, layout_file):
    # Check if sample count is valid.
    max_sample_support = int(np.floor((pool_size * pool_count) / replicates))
    if not samples:
        samples = max_sample_support
    else:
        if samples > max_sample_support:
            sys.exit( 'ERROR: The chosen parameters support a maximum of '
                     f'{max_sample_support} samples')

    # Generate pool layout and write it to output file.
    pool_log       = set_up_pools(pool_count, samples, replicates)
    write_layout_file(layout_file, pool_log)


def simulate(layout, prevalence, false_positives, false_negatives, out_layout_file):
    # Read existing pool layout, discard old positive pools / samples if any.
    pool_log, _, _ = read_layout_file(layout)

    # Find number of samples
    nsamples = 1 + max(
                [max(pool_samples) for pool_samples in pool_log])

    # Sample new positive pools.
    positive_pools, positive_samples = simulate_pools(
            pool_log, nsamples, prevalence, false_positives, false_negatives)

    # Write layout including new pool results.
    write_layout_file(
            out_layout_file, pool_log, positive_pools, positive_samples)


def resolve(layout, sample_results_file):
    # Read layout file including pool test results and, possibly, a ground
    # truth set of positive samples
    pool_log, pos_pools, true_pos_samples = read_layout_file(layout)

    # Resolve samples.
    sample_map = make_sample_map(pool_log)
    effective_samples, sample_state = resolve_samples(
        pool_log, sample_map, pos_pools, len(sample_map), len(pool_log))
    eprint(f'Effective number of samples / test: {effective_samples}')

    # Evaluate ground truth if available.
    if len(true_pos_samples) > 0:
        false_pos_rate, false_neg_rate, npos, nneg = get_false_pos_neg_rates(
                sample_state, true_pos_samples)
        eprint(f'False-pos. rate resolved: {false_pos_rate} of {nneg} neg. samples')
        eprint(f'False-neg. rate resolved: {false_neg_rate} of {npos} pos. samples')

    # Print / write results.
    sample_results_file.write('sample\tresult\n')
    for sample, state in sorted(sample_state.items()):
        state_symbol = '+' if state == +1 else '-' if state == -1 else 'NA'
        sample_results_file.write(f'{sample}\t{state_symbol}\n')
