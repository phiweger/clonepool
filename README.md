# clonepool

Increasing screening capacity for SARS-CoV-2 RT-PCR using pool addresses

## Abstract

Screening large sample collections for SARS-CoV-2 enables effective public
health response to restrict the spread of the virus. However, in most
laboratories the capacity is limited by the number of reactions any laboratory
can perform. Thus, it is desirable to maximize the number of samples that can
be tested, while minimizing the number of reactions required to do so.

Here we report a protocol for pooling samples that increases the number of
samples that can be processed compared to one-sample-per-tube testing by
multiples. This is achieved through the newly introduced concept of a _pool
address_: Each sample is present in multiple pools, which allows resolution of
the testing status even though it has not been tested individually. Target
prevalence and the desired pool size determine which address length is
optimal. This pooling protocol allows pooling to be effective even at a high
target prevalence where previous approaches become ineffective.

In the figure below this becomes apparent: Compared to the classical
one-by-one approach (horizontal black line) and naive x-samples-per-pool
approach (green), pooled replicates are more efficient at higher target
prevalence. Because at a higher prevalence more pools become positive, many
samples need one-by-one retesting. If a sample is present in multiple pools,
the combinatorics of the pools being positive or negative can inform about the
sample's state. For this, replicates are randomly distributed accross pools.
We simulate the procedure for up to five replicates per sample (color points).
The effective number of processable samples depends the target prevalence
(x-axis) and desired maximum pool size (facets). For example, using two pooled
replicates becomes more effective than putting each sample in only one pool
(of size three) at a prevalence of about 0.15.

## Install and run

```bash
git clone https://github.com/phiweger/clonepool
cd clonepool

conda env create --file conda_env.yml
conda activate clonepool

pip install -e .

clonepool layout -n 470 -P 10 -o test/layout.csv --simulate test/results.csv
```

![](img/sim.png)

