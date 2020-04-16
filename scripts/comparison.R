#!/usr/bin/env Rscript

library(ggplot2)
library(readr)

df <- read_csv('sim.csv')
# header 'replicates,pool_size,prevalence,effective_samples\n'


ggplot(
    df[(df$prevalence <= 0.1) & (df$replicates <= 4),],
    aes(x=as.factor(prevalence), y=effective_samples, color=as.factor(replicates))) +

    geom_boxplot(outlier.shape=NA, lwd=0.3) +
    scale_color_brewer(palette='Set2') +
    facet_wrap(~pool_size, nrow=2) +
    theme_classic() +
    theme(
        panel.grid.major.x=element_line(size=.1,color='black'),
        axis.text.x=element_text(angle=45, hjust=1)
        ) +
    geom_hline(yintercept=1) +
    ylab('resolved samples per reaction') +
    xlab('prevalence') +
    labs(color='replicates')


ggsave('sim.pdf', width=16, height=12, units='cm')
ggsave('sim.png', width=16, height=12, units='cm')

#facet_wrap(~pool_size, scale='free_y') +
#facet_grid(pool_size ~ replicates) +  
#guides(color=guide_legend(override.aes=list(size=2)))
