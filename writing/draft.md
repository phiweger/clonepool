## Draft

### TODO

name: poolgraph

```bash
poolgraph layout --prevalence 0.05 --npools 94 --nsamples 500 -o layout.csv
poolgraph resolve -i1 result.round.1.csv -i2 result.round.2.csv -o state.txt
```

refactor code as network problem: remove all nodes in negative pools. then from the remaining ones identify central ones to retest, drop isolates.



endvariable: proben/reaction

kontrollieren für poolgröße

kennzahlen sind wichtig:

ignore pipetting (robot)

x = {poolgröße, preävalence, poolzahl}

2nd: test individually

strategy: start w/ appropriate addresslen for prevalence estimate, e.g. 2 -- if samples unclear, move to next plate and use one more addresslen for them

if a pcr is negative, does not mean much -- does not apply here, bc/ negative is the result were after 

compare 10x pool naive w/ len 2 address and retest of all uncertain samples -- fewer retests? about 10 less

compare address len 3

address len 2 in first round and 3 in second? (aim -- reduce number of reactions per well, w/ 3 would be 20+ probably too much pooling) -- if still no, test, they are very likely positive (indeed calculate probability)




basically retest uncertain -- already here better -- or simply move along into next run (would that work, or would too many positives aggregate?)

### Notes

Nature Methods content type "Brief Communication":

- 3 pages
- Title 10 words or 90 characters
- Abstract 3 sentences 70 words
- Text 1000-1500 words (including abstract)
- max 2 images
- 20 refs
- Methods section heading points to online


TODO: ask Hasenclever to help w/ maths/ stats

- Remember PCR is a doubling process, so a ten fold dilution should be around 3.3 cycles (2^3.3=9.48). -- https://www.researchgate.net/post/what_is_the_Ct_difference_between_the_110_1100_11000_serial_dilution_for_standard_curve_in_qPCR_taqman

-- ct value shift is 2^x=dilution (10, 40, 100 etc.) use wolfram alpha
10 .. 3.3
50 .. 5ish
100 .. 7ish

-- cov ct cycle usually?

- fit lines into each p value (0.1, 0.2 ...) -- no jitter -- rstan?
- number of positive pools for addresslen, p, nsamples
- incentivises screening -- the more negative samples expected, the better
- plot: number of samples per well (dilution at some point of PCR? vacuum centrifugation a solution maybe? what's the typical ct value for covid? bc/ each sample reduces this by 1 right?)
- carry over samples poisson distribution -- how long is it likely that a sample is not resolved? like what's the prob that a sample is carried over 3, 4, 5 times etc. -- at some point direct testing needed
- only 94 wells bc/ pos an dneg control
- pooling always assumes we have time for 2 PCRs
- pooling only makes sense if a large portion negative
- propagating error by doing 2 PCRs (technical replication PCR -- coV? not same as "nasal swab sensitivity only 0.3 -- would still be negative in 2nd test") -- https://www.sciencedirect.com/science/article/pii/S0167779918303421 

Look at it from this angle: If you can't resolve 100 out of 1000, you have resolved 900, ie 10x more than you could w/o pooling.




test pool but resolve individual samples' test status without additional PCR


Adrian Viehweger, Felix Kühnl, Christian Brandt, jemand MBI/ Viro, jemand Senior

### Title

Increasing screening capacity for SARS-CoV-2 RT-PCR using pool addresses

### Abstract

Here we report a protocol for pooling samples that increases the number of samples that can be processed compared to one-sample-per-tube testing by multiples. This is achieved through the newly introduced concept of a _pool address_: Each sample is present in multiple pools, which allows resolution of the testing status even though it has not been tested individually. Target prevalence and the desired pool size determine which address length is optimal. This pooling protocol allows pooling to be effective even at a high target prevalence where previous approaches become ineffective.


### Main text

> Group testing was first described in [5] as a technique for screening United States Army recruits for syphilis.

Screening large sample collections for SARS-CoV-2 enables effective public health response to restrict the spread of the virus. However, in most laboratories the capacity is limited by the number of reactions any laboratory can perform. Thus, it is desirable to maximize the number of samples that can be tested, while minimizing the number of reactions required to do so. 

Pooling samples, i.e. mixing samples and performing a joint RT-PCR reaction on them, is a common technique to maximize sample to reaction ratio [@Sinnott-Armstrong2020-yb; @Eis-Huebinger2020-fo]. 

addresslen = 1 -- Eis-Huebinger2020-fo
addresslen = 2 -- Sinnott-Armstrong2020-yb


If a pool is tested positive, its constituent samples are tested individually.

> When most tests are negative, pooling reduces the total number of tests up to four-fold at 2% prevalence and eight-fold at 0.5% prevalence.

While pooling increases capacity substantially (x.x% in y) this second round of tests is limiting. Many pooling approaches that average across rows/ columns of a testing plate (e.g. 96 well) only a bit more than double capacity (2.6% in x). Here we present a protocol that increases the number of samples that can be analysed by a factor of more than ten compared to one-sample-per-tube testing, surpassing other protocols substantially. Unlike them, it also allows the evaluation of each individual sample without a second PCR, even each sample was only as part of a pool.

This is achieved by distributing each sample across multiple pools, the set of which constitutes that sample's "pool address" (Fig. 1, A). 


![Caption.](main.pdf)


Our protocol assumes low prevalence in the range of 5% and less, which is typical for a screening test. It also assumes limited error in technical replicates. The protocol is further limited by

- number of slots which determine the size of the address space -- __Note that the set is important, ie address A-B = B-A__.
- number of samples per pool (Fig. 1, C)

Simulations suggest ... (Fig. 1, B).

Our protocol can be applied to other screening contexts than SARS-CoV-2019, such as screening for antimicrobial resistance genes.


### References




