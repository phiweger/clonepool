---
# Officially required params
fontsize: 11pt
geometry: margin=2cm
linestretch: 1.5

# Extensions
fig_caption: yes
table_captions: yes
implicit_figures: no
escaped_line_breaks: yes

fontfamily: palatino
# https://stackoverflow.com/questions/26479047
# mainfont: Arial
urlcolor: magenta
wrap: preserve

# toc: yes
# toc-title: Table of contents
# toc-depth: 3

header-includes:
- \usepackage{setspace}
- \doublespacing
- \usepackage[left]{lineno}
- \linenumbers
---


<!--
pandoc -s --pdf-engine=xelatex -f markdown -t latex -o draft.pdf draft.md --bibliography config/paperpile.bib --csl config/nature.csl --template config/default.tex --filter pandoc-xnos
-->


## Increased PCR screening capacity using pool addresses

Adrian Viehweger $^{1, 4}$ \*, Felix Kühnl $^2$ \*, Christian Brandt $^{3, 4}$, Brigitte König $^1$

\* These authors contributed equally.

$^1$ Medical Microbiology, University Hospital Leipzig

$^2$ Bioinformatics, University Leipzig

$^3$ Infection Medicine, University Hospital Jena

$^4$ nanozoo GmbH, Leipzig


### Abstract

We report a pooling protocol that increases the number of samples that can be processed with PCR by multiples compared to per-sample testing and naive pooling. This is achieved through the newly introduced concept of a _pool address_: A sample is replicated accross multiple pools, which in many cases allows it to be resolved as positive even though it has not been tested individually. Our protocol allows pooling to be effective even at a high target prevalence where common approaches become ineffective. The corresponding software to layout and resolve samples is freely released under a BSD license (https://github.com/phiweger/clonepool).


\newpage

### Main text

Group testing has long been used to screen larger collections of samples, most of which are expected to be negative [@Dorfman1943-eo]. With the current SARS-CoV-2 pandemic, screening large sample collections for the virus enables effective public health response to restrict its spread. However, in most laboratories the capacity is limited by the number of PCR reactions that can be performed in a day. Thus, it is desirable to maximize the number of samples that can be tested, while minimizing the number of reactions required to do so.

Various approaches have been proposed to do this in the context of SARS-CoV-2 RT-PCR testing [@Sinnott-Armstrong2020-yb; @Eis-Huebinger2020-fo]. One problem with the traditional pooling approach, where a number of samples is collected and tested collectively, is that the number of positive pools that require individual retesting increases rapidly with the number of positive samples in the overall population. This renders pooling ineffective. One approach to mitigate this problem is to test samples in replicates and distribute those replicates accross multiple pools. This "pool address" can then be used to resolve samples in one pool given information from the other pools their replicates occur in. While previous studies have taken this approach implicitly [@@Sinnott-Armstrong2020-yb], it has neither been investigated systematically for a larger number of replicates than two, nor is there any software that would generate and resolve the corresponding pooling layout for laboratory use.

We introduce "clonepool", a pooling framework to maximize the effective number of samples $s_{eff}$ per PCR reaction. "Effective" refers to the fact that samples in positive pools whose status cannot be resolved in the pooled run are assumed to be retested individually.

The maximum number of samples for a given pool size $p$, number of pools $n$ and number of replicates $r$ is calculated as

$$s_{max} = \frac{pn}{r}$$

The effective number of samples can then be calculated from the number of unresolved samples $s$ as:

$$s_{eff} = \frac{s_{max}}{p + s}$$

The clonepool algorithm first distributes all sample replicates randomly accross the available pools, with the limitation that a sample's replicates do not co-occur in the same pool. After the pools have been tested, the algorithm tries to resolve the samples' status in two iterations: In a first iteration, all samples that have at least one replicate in a negative pool are marked negative. In the second iteration, samples that only occur in positive pools and where at least one replicate is in a pool where all other samples are negative, are marked positive (red, orange). All other samples cannot be resolved, and need to be retested individually. The longer the set of pools a sample is distributed across, i.e. the longer its "pool address", the more samples can be resolved given a particular prevalence.

![Illustration of the clonepool algorithm. Positive pools (circles) are marked grey, negative ones in white. Samples are depicted as squares, positive ones with a "+". In a first iteration, all samples that have at least one replicate in a negative pool are marked negative (blue, green). In the second iteration, samples that only occur in positive pools and where at least one replicate is in a pool where all other samples are negative, are marked positive (red, orange). All other samples cannot be resolved and have to be retested individually (yellow).](../img/protocol.pdf){#fig:protocol}

In our simulation test of the proposed clonepool algorithm we assume no pipetting errors, which can be achieved e.g. through use of a pipetting robot. We also assume that 94 pools are available, which corresponds to a 96-well plate with two wells reserved for a positive and a negative control. Furthermore, we assume that there are no false positive or false negative PCR reactions.

Two parameters determine which pooling scheme is most effective (Fig. @fig:simulation). If the prevalence and the number of samples per pool are low, using only one "replicate" yields the highest number of samples per reaction. However, if the prevalence increases or more samples are pooled, there is an increased probability for any one pool to become positive, in which case the use of sample replicates helps resolve more samples. In our testing experience, we observe a prevalence of about 5%, but this value is subject to variability e.g. depending on a population's pre-test probability. The number of samples that can be pooled without affecting the PCR sensitivity is limited by the PCR cycle threshold (Ct) for the target, i.e. the cycle at which amplification becomes detectable over background noise. Usually, Ct values above 35 are treated as unspecific amplification. For example, SARS-CoV-2 amplifies at low Ct values due to high viral titers (Ct 18-25 depending on the material and number of days post-infection) [@Wolfel2020-tt; @Holshue2020-mm]. A 20-fold dilution, i.e. pooling 20 samples, would cause the Ct value to increase by about 4.3 cycles ($2^x = d$, where d is the dilution and x the shift in Ct), still comfortably above the detection limit.

<!--
See 8. here:

https://www.ecdc.europa.eu/en/all-topics-z/coronavirus/threats-and-outbreaks/covid-19/laboratory-support/questions
-->

![Simulation results for different percentages of positive samples (x-axis), replicates (colors) and pool sizes (panels). The target metric is the effective number of samples per PCR reaction, which includes the individual retesting of samples that cannot be resolved in the first pooling run. ](../img/sim.pdf){#fig:simulation}

At a prevalence of 5% SARS-CoV-2 positive samples, and for 10 samples per pool and two replicates per sample, we simulate that 2.61 times the number of samples can be processed compared to testing samples individually (SD 0.13). Using two replicates increases the effective number of samples per reaction by 31% compared to pooling without replicates. This is in line with previous estimates using a slightly different version of the 2-replicate scheme [@Sinnott-Armstrong2020-yb]. At 2% prevalence and 20 samples per pool -- a scenario more akin to screening large populations -- 5.01 times the number of samples can be screened compared to individiual testing (SD 0.28), and the increase over no replicate pooling is 193%. These presented values correspond to _in silico_ simulations, and require further testing in the laboratory.

<!--

mean(df[df$pool_size==10 & df$prevalence==0.05 & df$replicates==2,]$effective_samples)

10 pool 0.05 1.310641 31% 2 vs 1 and 2.61 more than single-tube (comparable to paper Sinnott-Armstrong2020-yb)

20 pool 0.025 1.626311 63% 3 vs 1 and 2.35 more than single-tube

-->

In conclusion, our pooling protocol based on sample replicates can substantially increase the number of samples per PCR reaction when screening large populations for a target such as SARS-CoV-2. The protocol can be tuned to local conditions such as pool size and positive sample prevalence. The accompanying software supports the protocol's implementation and routine use. 


\newpage

### References




