#!/usr/bin/env python3

from collections import defaultdict
import numpy as np
from tqdm import tqdm


def poolfn(nsamples, addresslen, npositive):
    samples = np.arange(0, nsamples)
        
    pool_count = 94
    pools = {k: [] for k in np.arange(0, pool_count)}
    # 96 well plate, 1 positive control, 1 negative

    for i in samples:
        address = np.random.choice(
            list(pools.keys()), size=addresslen, replace=False)
        for j in address:
            pools[j].append(i)

    # FK: Improved homogenous distribution of samples to pools.
    # Init all wells with maximum count and decrement for each added sample.
    max_pool_sample_count = np.ceil(addresslen * nsamples / pool_count)
    pool_sample_count \
        = {k: max_pool_sample_count for k in np.arange(0, pool_count)}
    for i in samples:
        address = np.random.choice(
            list(pools_sample_count.keys()), size=addresslen, replace=False)
        for j in address:
            pools[j].append(i)
            pools_sample_count[j] -= 1
            if pools_sample_count[j] == 0:
                del pools_sample_count[j]       # delete well if it is full


    # This follows a binomial distribution. The experiment is: given a single
    # well, for each of n = nsamples = 1000 samples,
    # place the sample in that well with probability
    # p = addresslen / well_count = 2/94 ~= 0.021277 (since we choose 2 out of
    # the 94 wells randomly).
    # Expected value: n*p = 21.3 samples / well
    # Std dev: sqrt( n*p*(1-p) ) ~= sqrt(20.8) ~= 4.6
    # ==> On average, there are 21 samples in a well, and in 96% of the
    # cases, there will be between 12 and 30 samples / well.
    mean_size_pool = round(np.mean([len(i) for i in pools.values()]), 4)
    
    sample_map = defaultdict(list)
    for i in samples:
        for k, v in pools.items():
            if i in v:
                sample_map[i].append(k)    

    positive = set()
    for k, v in pools.items():
        # Samples 0 throuugh 19 are Ccov positive (0.02)
        for i in np.arange(0, npositive):
            if i in v:
                positive.add(k)
    
    uncertain = 0
    for k, v in sample_map.items():
        cnt = 0
        for i in v:
            if i in positive:
                cnt += 1
        if cnt == addresslen:
            uncertain += 1
    return mean_size_pool, uncertain


# nsamples = 1000
addresslen = 2  # 96 * 95 = 9120 addresses -- enough
# p = 0.01
# npositive = np.floor(nsamples * p)ihp

# uncertain = poolfn(nsamples, addresslen, npositive)
# print(f'Cannot resolve state of {uncertain} samples')


with open('pool.csv', 'w+') as out:
    for _ in range(1):
        for nsamples in tqdm(np.arange(100, 1000, 100)):
            for p in np.arange(0.01, 0.5, 0.01):
                npositive = np.floor(nsamples * p)
                mean_size_pool, uncertain = poolfn(
                    nsamples, addresslen, npositive)
                out.write(f'{nsamples},{p},{round(uncertain / nsamples, 4)},{mean_size_pool}\n')



'''
Cannot resolve state of 227 samples

But, just carry them forward, most of them negative. 1000-227 can be resolved! ie 8x increase in capacity!

library(ggplot2)
library(readr)
df <- read_csv('pool.csv', col_names=c('nsamples', 'perc', 'uncertain', 'poolsize'))
ggplot(df, aes(x=nsamples, y=uncertain, color=perc)) + 
    geom_jitter(size=0.5) + 
    scale_color_gradient(low = "yellow", high = "red", na.value = NA) +
    theme_classic()
ggsave('pool.pdf', width=7, height=5, units='cm')
# color=as.factor(perc))

ggplot(df, aes(x=nsamples, y=poolsize)) + 
    geom_line() +
    theme_classic()
ggsave('poolsize.pdf', width=5, height=5, units='cm')
'''




