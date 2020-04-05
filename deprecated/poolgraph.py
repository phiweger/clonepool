from collections import defaultdict
import numpy as np
from tqdm import tqdm


def poolfn(nsamples, p, addresslen, pool_count=94):
    '''
    96 well plate, 1 positive control, 1 negative
    '''

    nsamples = 500
    p = 0.025
    addresslen = 3
    npositive = int(np.floor(p * nsamples))
    # works well
    # nsamples = 500
    # p = 0.025
    # npositive = np.floor(p * nsamples)
    # addresslen = 3

    samples = np.arange(0, nsamples)
    positive_samples = np.random.choice(
        np.arange(0, nsamples),
        size=npositive,
        replace=False)
    # print(f'{len(positive_samples)} positive samples')

    pools = {k: [] for k in np.arange(0, pool_count)}

    # (A) Distribute samples across pools randomly ...
    # for i in samples:
    #     if addresslen != 'many':
    #         address = np.random.choice(
    #             list(pools.keys()), size=addresslen, replace=False)
    #     else:
    #         address = np.random.choice(
    #             list(pools.keys()), size=np.random.choice([1, 2, 3]), replace=False)

    #     for j in address:
    #         pools[j].append(i)


    # (B) ... and non-random, from Felix (basically fill up pools till full)
    
    if addresslen == 'many':
        max_pool_sample_count = np.ceil(4 * nsamples / pool_count)
    else:
        max_pool_sample_count = np.ceil(addresslen * nsamples / pool_count)
    

    pools_sample_count \
        = {k: max_pool_sample_count for k in np.arange(0, pool_count)}
    
    for i in samples:
        # Adaptive addresslen based on some prior expectation
        if addresslen == 'many':
            if i in positive_samples:
                addresslen = 4
            else:
                addresslen = 2

        try:
            address = np.random.choice(
                list(pools_sample_count.keys()), size=addresslen, replace=False)
            for j in address:
                pools[j].append(i)
                pools_sample_count[j] -= 1
                
                if pools_sample_count[j] == 0:
                    del pools_sample_count[j]       # delete well if it is full

        except ValueError:  
            # Cannot take a larger sample than population when 'replace=False'
            # Then random
            address = np.random.choice(
                list(pools.keys()), size=addresslen, replace=False)
            for j in address:
                pools[j].append(i)


    positive_pools = set()
    for k, v in pools.items():
        # Samples 0 throuugh 19 are Ccov positive (0.02)
        for i in positive_samples:
            if i in v:
                positive_pools.add(k)
    # print(f'{len(positive_pools)} positive pools')


    mean_size_pool = round(np.mean([len(i) for i in pools.values()]), 4)

    sample_map = defaultdict(list)
    for i in samples:
        for k, v in pools.items():
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
    
    # Catch case where all is resolved straight away
    if old == 0:
        return old, mean_size_pool, len(positive_pools)

    # If not all samples are resolved, iterate until they are or the number
    # of unresolved samples converges (does not get smaller)
    while old > 0:

        for sample, _ in state.items():
            sample_pools = sample_map[sample]
            # assert len(sample_pools) == addresslen
            
            for pool in sample_pools:
                s = [state[i] for i in pools[pool]]
                # if sum(s) > 0:
                #     print(s)
                if sum(s) == 1:
                    state[sample] = 0
        new = sum(state.values())
        # print(new)
        if new == old:  # convergence
            # TODO: Export network view of the remaining samples, i.e.
            # two samples share a connection if they are in the same pool.
            return new, mean_size_pool, len(positive_pools)
        else:
            old = new

    # All samples resolved
    return new, mean_size_pool, len(positive_pools)


with open('pool4.csv', 'w+') as out:
    
    for addresslen in ['many', 1, 2, 3, 4]:
        for _ in tqdm(range(1000)):
            # 1 is like pooling e.g. 10 samples in 1 pool
            nsamples = np.random.randint(100, 1000)
            
            for p in np.arange(0, 0.15, 0.025):
                # TODO: enough from 0.01 to 0.1
            
                uncertain, mean_size_pool, npositive_pools = poolfn(
                    nsamples, p, addresslen)
            
                out.write(f'{nsamples},{p},{addresslen},{npositive_pools},{round(uncertain / nsamples, 4)},{mean_size_pool}\n')



'''
library(ggplot2)
library(readr)

df <- read_csv('pool4.csv', col_names=c('nsamples', 'p', 'address', 'npositive_pools', 'uncertain', 'poolsize'))
df <- df[df$p != 0,]

ggplot(df, aes(x=nsamples, y=uncertain, color=p)) + 
    geom_jitter(size=0.5, height=0) + 
    scale_color_gradient(low = "yellow", high = "red", na.value = NA) +
    theme_classic() +
    facet_wrap(~address, nrow=1)
ggsave('pool3a.pdf', width=27, height=5, units='cm')

ggplot(df, aes(x=nsamples, y=uncertain, color=as.factor(address))) + 
    geom_jitter(size=0.3, height=0) + 
    theme_classic() +
    scale_color_brewer(palette='Set2') +
    facet_wrap(~p, nrow=2, scales='free_y')
# scales='free_y'
ggsave('pool4b.pdf', width=22, height=10, units='cm')


ggplot(df, aes(x=nsamples, y=uncertain, color=as.factor(p))) + 
    geom_point(size=0.3) + 
    theme_classic() +
    scale_color_brewer(palette='Set2') +
    facet_wrap(~as.factor(address), nrow=5, scales='free_y')


# select p
ggplot(df[df$p==0.05,], aes(x=nsamples, y=uncertain, color=address)) + 
    geom_point(size=0.3) + 
    theme_classic() +
    scale_color_brewer(palette='Set2') +
    facet_wrap(~as.factor(address), nrow=5)


ggplot(df, aes(x=nsamples, y=poolsize)) + 
    geom_line() +
    theme_classic() +
    facet_wrap(~address, nrow=1)
ggsave('poolsize3.pdf', width=25, height=5, units='cm')
'''




