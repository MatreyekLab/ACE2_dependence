ACE2\_dependence
================
Kenneth Matreyek
1/12/2021

``` r
## Clear existing environment
rm(list = ls())

## Load basic useful packages
library(tidyverse)
```

    ## ── Attaching packages ─────────────────────────────────────── tidyverse 1.3.1 ──

    ## ✓ ggplot2 3.3.5     ✓ purrr   0.3.4
    ## ✓ tibble  3.1.5     ✓ dplyr   1.0.7
    ## ✓ tidyr   1.1.4     ✓ stringr 1.4.0
    ## ✓ readr   2.0.2     ✓ forcats 0.5.1

    ## ── Conflicts ────────────────────────────────────────── tidyverse_conflicts() ──
    ## x dplyr::filter() masks stats::filter()
    ## x dplyr::lag()    masks stats::lag()

``` r
library(ggrepel)
library(ggbeeswarm)
library(reshape)
```

    ## 
    ## Attaching package: 'reshape'

    ## The following object is masked from 'package:dplyr':
    ## 
    ##     rename

    ## The following objects are masked from 'package:tidyr':
    ## 
    ##     expand, smiths

``` r
library(sf)
```

    ## Linking to GEOS 3.8.1, GDAL 3.2.1, PROJ 7.2.1

``` r
library(here)
```

    ## here() starts at /Users/kmatreyek/Box Sync/Github/ACE2_dependence

``` r
library(ggfortify)

## Set the seed for immediate reproducibility
set.seed(1234567)

## Set the base theme to what I like
theme_set(theme_bw())
theme_update(legend.title = element_blank())

## Set up consistent colors
virus_colors <- c("VSV" = "red", "SARS-CoV" = "darkgreen", "SARS-CoV-2" = "blue")
```

``` r
combined_infection <- read.csv(file = "Data/Receptor_dependence_data.csv")

recombined_construct_key <- read.csv(file = "Data/Keys/Construct_label_key.csv", header = T, stringsAsFactors = F)
pseudovirus_label_key <- read.csv(file = "Data/Keys/Pseudovirus_label_key.csv", header = T, stringsAsFactors = F) #%>% filter(sequence_confirmed != "no")
clade_labels_key <- read.csv(file = "Data/Keys/Clade_labels.csv", header = T, stringsAsFactors = F)
clade_labels_key$clade = factor(clade_labels_key$clade, levels = c(1,2,3,4))
```

``` r
# Two-color data
two_color_precombined <- combined_infection %>% filter(expt %in% c("Two_color", "Receptors", "ACE2_TMPRSS2", "Two_color_ACE2_TMPRSS2", "Mixed_cell_infection", "Btky72_ACE2muts", "Bat_ACE2s","LSign_RBD_panel","Clade3_hum_muts","ACE2_muts") & !(is.na(pseudovirus_env) | pseudovirus_env == "None") & live_singlets != "Too few infected")

## Make sure I ignore data where I didn't run enough cells to make a conclusion
two_color_precombined$live_singlets <- as.numeric(two_color_precombined$live_singlets)
two_color_precombined$pct_red  <- as.numeric(two_color_precombined$pct_red)
two_color_precombined$pct_nir <- as.numeric(two_color_precombined$pct_nir)

two_color_precombined$lower_bound_red <- 10^(log10(two_color_precombined$live_singlets * two_color_precombined$pct_red / 100)*-0.99 + 2.64)
two_color_precombined$lower_bound_nir <- 10^(log10(two_color_precombined$live_singlets * two_color_precombined$pct_nir / 100)*-0.99 + 2.64)
two_color_precombined$passes_lower_bound <- "no"
two_color_precombined$passes_upper_bound <- "no"
for(x in 1:nrow(two_color_precombined)){
  if(two_color_precombined$lower_bound_red[x] <= two_color_precombined$pct_grn_gvn_red[x] & two_color_precombined$lower_bound_nir[x] <= two_color_precombined$pct_grn_gvn_nir[x]){two_color_precombined$passes_lower_bound[x] <- "yes"}
  if(two_color_precombined$pct_grn_gvn_red[x] <= 90 & two_color_precombined$pct_grn_gvn_nir[x] <= 90){two_color_precombined$passes_upper_bound[x] <- "yes"}
}
two_color_combined <- merge(two_color_precombined %>% filter(passes_lower_bound == "yes" & passes_upper_bound == "yes"), pseudovirus_label_key, by = "pseudovirus_env", all.x = T) %>% mutate(ratio_nir_mcherry = pct_nir / pct_red)
```

## Seeing how the two color assay performs

``` r
mixed_cell_infection <- two_color_precombined %>% filter(expt == "Mixed_cell_infection" & pseudovirus_env != "BtKY72" & !(pseudovirus_env == "SARS1" & date == "8/10/2021"))
mixed_cell_infection$log10_nir_red_diff <- log10(mixed_cell_infection$moi_gvn_nir) - log10(mixed_cell_infection$moi_gvn_red)
mixed_cell_infection$fold_difference <- 10^mixed_cell_infection$log10_nir_red_diff
mixed_cell_infection$ratio_nir_mcherry <- mixed_cell_infection$pct_nir / mixed_cell_infection$pct_red
mixed_cell_infection <- merge(mixed_cell_infection, pseudovirus_label_key, by = "pseudovirus_env", all.x = T)

unmixed_cell_infection <- two_color_precombined %>% filter(expt == "Mixed_cell_infection" & ((pct_red > 94 & pct_nir < 3) | (pct_red < 3 & pct_nir >88)) & pseudovirus_env != "BtKY72")

unmixed_cell_dataframe <- data.frame(date = rep(unique(unmixed_cell_infection$date), each =length(unique(unmixed_cell_infection$pseudovirus_env))), pseudovirus_env = rep(unique(unmixed_cell_infection$pseudovirus_env), length(unique(unmixed_cell_infection$date))),"fold_difference" = 0)
unmixed_cell_dataframe <- unmixed_cell_dataframe[!(unmixed_cell_dataframe$pseudovirus_env == "SARS2" & unmixed_cell_dataframe$date == "8/10/2021") & !(unmixed_cell_dataframe$pseudovirus_env == "SARS1" & unmixed_cell_dataframe$date == "8/10/2021") & !(unmixed_cell_dataframe$pseudovirus_env == "VSVG" & unmixed_cell_dataframe$date == "8/12/2021"),]

for(x in 1:nrow(unmixed_cell_dataframe)){
  temp_date <- unmixed_cell_dataframe$date[x]
  temp_virus <- unmixed_cell_dataframe$pseudovirus_env[x]
  temp_data <- unmixed_cell_infection %>% filter(date == temp_date, pseudovirus_env == temp_virus)
  
  unmixed_cell_dataframe$fold_difference[x] <- temp_data[temp_data$pct_nir > 80 & temp_data$pseudovirus_env == temp_virus,"moi_gvn_nir"] / temp_data[temp_data$pct_red > 80 & temp_data$pseudovirus_env == temp_virus,"moi_gvn_red"]
}

unmixed_cell_dataframe <- merge(unmixed_cell_dataframe, pseudovirus_label_key, by = "pseudovirus_env", all.x = T)
unmixed_cell_dataframe_summary <- unmixed_cell_dataframe %>% group_by(pseudovirus_env) %>% summarize(fold_diff = mean(fold_difference))

mixed_cell_infection$ratio_nir_mcherry_plotting <- mixed_cell_infection$ratio_nir_mcherry
for(x in 1:nrow(mixed_cell_infection)){
  if(mixed_cell_infection$ratio_nir_mcherry[x] <= 0.1){mixed_cell_infection$ratio_nir_mcherry_plotting[x] <- NA}
  if(mixed_cell_infection$ratio_nir_mcherry[x] >= 90){mixed_cell_infection$ratio_nir_mcherry_plotting[x] <- NA}
}
```

``` r
mixed_cell_infection_summary <- mixed_cell_infection %>% filter(!(pct_nir %in% c(0,100)) & !(fold_difference == "Inf") & !(fold_difference == 0)) %>% mutate(count = 1, log10_fold_diff = log10(fold_difference)) %>% group_by(pseudovirus_env, pct_nir) %>% 
  summarize(log10_mean = mean(log10_fold_diff), log10_sd = sd(log10_fold_diff), n = sum(count), .groups = "drop") %>% 
  mutate(log10_upper_conf = log10_mean + log10_sd/sqrt(n-1) * qt(p=0.05/2, df=n-1,lower.tail=F),
         log10_lower_conf = log10_mean - log10_sd/sqrt(n-1) * qt(p=0.05/2, df=n-1,lower.tail=F),
         mean = 10^log10_mean,
         upper_conf = 10^log10_upper_conf,
         lower_conf = 10^log10_lower_conf)

mixed_cell_infection_summary2 <- merge(mixed_cell_infection_summary, pseudovirus_label_key, by = "pseudovirus_env")

unmixed_cell_dataframe_summary <- unmixed_cell_dataframe %>% mutate(count = 1, log10_fold_diff = log10(fold_difference)) %>% group_by(pseudovirus_env) %>% 
  summarize(log10_mean = mean(log10_fold_diff), log10_sd = sd(log10_fold_diff), n = sum(count), .groups = "drop") %>% 
  mutate(log10_upper_conf = log10_mean + log10_sd/sqrt(n-1) * qt(p=0.05/2, df=n-1,lower.tail=F),
         log10_lower_conf = log10_mean - log10_sd/sqrt(n-1) * qt(p=0.05/2, df=n-1,lower.tail=F),
         mean = 10^log10_mean,
         upper_conf = 10^log10_upper_conf,
         lower_conf = 10^log10_lower_conf)

unmixed_cell_dataframe_summary2 <- merge(unmixed_cell_dataframe_summary, pseudovirus_label_key, by = "pseudovirus_env")

## Setting the factor levels for the plot
unmixed_cell_dataframe$virus_label <- factor(unmixed_cell_dataframe$virus_label, levels = c("VSV","SARS-CoV","SARS-CoV-2"))
unmixed_cell_dataframe_summary2$virus_label <- factor(unmixed_cell_dataframe_summary2$virus_label, levels = c("VSV","SARS-CoV","SARS-CoV-2"))
mixed_cell_infection$virus_label <- factor(mixed_cell_infection$virus_label, levels = c("VSV","SARS-CoV","SARS-CoV-2"))
mixed_cell_infection_summary2$virus_label <- factor(mixed_cell_infection_summary2$virus_label, levels = c("VSV","SARS-CoV","SARS-CoV-2"))

Mixed_cell_fold_ACE2_dependence <- ggplot() + theme_bw() + theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(), legend.position = "none") + 
  labs(x = "% ACE2 cells in well", y = "Fold ACE2-dependent\ninfection") +
  scale_x_continuous(limits = c(-10,100), expand = c(0,0), breaks = c(10,20,40,60,80,90)) + #scale_x_log10(breaks = c(0.3,1,3,10,30), limits = c(0.08,10)) + 
  scale_y_log10(limits = c(3e-1, 3e2), breaks = c(1e-1,1,1e1,1e2,1e3), expand = c(0,0)) + scale_color_manual(values = virus_colors) +  
  geom_vline(xintercept = 0) + geom_hline(yintercept = 1, alpha = 0.5) +
  geom_point(data = subset(mixed_cell_infection, !(pct_nir %in% c(0,100)) & fold_difference > 0 & fold_difference < 100), aes(x = pct_nir, y = fold_difference, color = virus_label),
             position = position_dodge(width = 7.5), alpha = 0.5) +
  geom_point(data = subset(mixed_cell_infection_summary2, !is.na(upper_conf)), aes(x = pct_nir, y = mean, color = virus_label),
             position = position_dodge(width = 7.5), shape = 95, size = 7) +
  geom_errorbar(data = subset(mixed_cell_infection_summary2, !is.na(upper_conf)), aes(x = pct_nir, ymin = lower_conf, ymax = upper_conf, color = virus_label), position = position_dodge(width = 7.5), width = 4) +
  geom_point(data = unmixed_cell_dataframe, aes(x = -5, y = fold_difference, color = virus_label), position = position_dodge(width = 7.5), alpha = 0.5) +
  geom_point(data = unmixed_cell_dataframe_summary2, aes(x = -5, y = mean, color = virus_label), position = position_dodge(width = 7.5), shape = 95, size = 7) +
  geom_errorbar(data = unmixed_cell_dataframe_summary2, aes(x = -5, ymin = lower_conf, ymax = upper_conf, color = virus_label), position = position_dodge(width = 7.5), width = 4)
Mixed_cell_fold_ACE2_dependence
```

![](ACE2_dependence_files/figure-gfm/Plotting%20out%20the%20mixed%20vs%20unmixed%20cell%20infection%20data-1.png)<!-- -->

``` r
ggsave(file = "Plots/Mixed_cell_fold_ACE2_dependence.pdf", Mixed_cell_fold_ACE2_dependence, height = 1.75, width = 4)


## Figure out the coefficient of variation
unmixed_cell_dataframe_summary2$cv <- 10^(unmixed_cell_dataframe_summary2$log10_sd)/10^(unmixed_cell_dataframe_summary2$log10_mean)
mixed_cell_infection_summary2$cv <- 10^(mixed_cell_infection_summary2$log10_sd)/10^(mixed_cell_infection_summary2$log10_mean)

Mixed_cell_cv <- ggplot() + theme_bw() + theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(), legend.position = "none") + 
  labs(x = "% ACE2 cells in well", y = "CV") +
  scale_x_continuous(limits = c(-10,100), expand = c(0,0), breaks = c(10,20,40,60,80,90)) + #scale_x_log10(breaks = c(0.3,1,3,10,30), limits = c(0.08,10)) + 
  scale_y_log10() + scale_color_manual(values = virus_colors) +  
  geom_vline(xintercept = 0) + geom_hline(yintercept = 1, alpha = 0.5) +
  geom_point(data = subset(mixed_cell_infection_summary2, !is.na(upper_conf)), aes(x = pct_nir, y = cv, color = virus_label), position = position_dodge(width = 7.5)) +
  geom_point(data = unmixed_cell_dataframe_summary2, aes(x = -5, y = cv, color = virus_label), position = position_dodge(width = 7.5))
Mixed_cell_cv
```

![](ACE2_dependence_files/figure-gfm/Plotting%20out%20the%20mixed%20vs%20unmixed%20cell%20infection%20data-2.png)<!-- -->

``` r
ggsave(file = "Plots/Mixed_cell_cv.pdf", Mixed_cell_cv, height = 1, width = 4)
```

## Seeing which receptors or proposed receptors actually enhance SARS-CoV-2 pseudovirus entry when overexpressed in HEK cells

``` r
receptors <- two_color_combined %>% filter(expt == "Receptors" & recombined_construct != "CD209")
receptors$log10_nir_red_diff <- log10(receptors$moi_gvn_nir) - log10(receptors$moi_gvn_red)

## Collapsing all proteins to a single group, regardless of the tag
receptors$receptor_grouped <- NA
for(x in 1:nrow(receptors)){receptors$receptor_grouped[x] <- toupper(gsub("\\[HA]","",receptors$recombined_construct[x]))}

## Group by receptor, regardless of tag
receptors_grouped <- receptors %>% group_by(date, receptor_grouped, virus_label) %>% 
  summarize(log10_nir_red_diff = mean(log10_nir_red_diff), pct_grn_gvn_red = mean(pct_grn_gvn_red), pct_grn_gvn_nir = mean(pct_grn_gvn_nir), ratio_nir_mcherry = mean(ratio_nir_mcherry), .groups = "drop") %>% 
  mutate(n = 1, ace2dep_infection = 10^log10_nir_red_diff)

receptors_grouped_summary <- receptors_grouped %>% group_by(receptor_grouped, virus_label) %>% 
  summarize(mean_log10_nir_red_diff = mean(log10_nir_red_diff), sd_log10_nir_red_diff = sd(log10_nir_red_diff), n = sum(n), .groups = "drop") %>% 
  mutate(se_log10_nir_red_diff = sd_log10_nir_red_diff / sqrt(n), geomean = 10^mean_log10_nir_red_diff, lower_ci = 10^(mean_log10_nir_red_diff - se_log10_nir_red_diff * qt(p=0.05/2, df=n-1,lower.tail=F)), upper_ci = 10^(mean_log10_nir_red_diff + se_log10_nir_red_diff * qt(p=0.05/2, df=n-1,lower.tail=F)))
```

    ## Warning in qt(p = 0.05/2, df = n - 1, lower.tail = F): NaNs produced

    ## Warning in qt(p = 0.05/2, df = n - 1, lower.tail = F): NaNs produced

``` r
receptors_virus_label_levels <- c("VSV", "SARS-CoV", "SARS-CoV-2")
receptors_grouped <- receptors_grouped %>% filter(virus_label %in% receptors_virus_label_levels)
receptors_grouped$virus_label <- factor(receptors_grouped$virus_label, receptors_virus_label_levels)
receptors_grouped_summary <- receptors_grouped_summary %>% filter(virus_label %in% receptors_virus_label_levels)
receptors_grouped_summary$virus_label <- factor(receptors_grouped_summary$virus_label, receptors_virus_label_levels)


## Keep the differentially tagged constructs separated
receptors_ungrouped <- receptors %>% filter(virus_label != "BtKY72 RBD") %>% group_by(date, recombined_construct, virus_label) %>% 
  summarize(log10_nir_red_diff = mean(log10_nir_red_diff), pct_grn_gvn_red = mean(pct_grn_gvn_red), pct_grn_gvn_nir = mean(pct_grn_gvn_nir), .groups = "drop") %>% 
  mutate(n = 1, ace2dep_infection = 10^log10_nir_red_diff)

receptors_ungrouped_summary <- receptors_ungrouped %>% group_by(recombined_construct, virus_label) %>% 
  summarize(mean_log10_nir_red_diff = mean(log10_nir_red_diff), sd_log10_nir_red_diff = sd(log10_nir_red_diff), n = sum(n), .groups = "drop") %>% 
  mutate(se_log10_nir_red_diff = sd_log10_nir_red_diff / sqrt(n), geomean = 10^mean_log10_nir_red_diff, lower_ci = 10^(mean_log10_nir_red_diff - se_log10_nir_red_diff * 1.96), upper_ci = 10^(mean_log10_nir_red_diff + se_log10_nir_red_diff * 1.96))

receptors_ungrouped_summary$envelope <- factor(receptors_ungrouped_summary$virus_label, receptors_virus_label_levels)

## Now make a dataframe so I can do a comparative scatterplot
tagged_vs_untagged_receptors_dataframe <- 
  data.frame("gene" = c(rep("BSG",3),rep("NRP1",3),rep("NRP2",3),rep("CLEC4M",3),rep("ACE2",3)),
             "virus" = c(receptors_ungrouped_summary[1:15,"virus_label"]),
             "tagged" = c(subset(receptors_ungrouped_summary, recombined_construct == "[HA]BSG")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "Nrp1[HA]")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "Nrp2[HA]")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "[HA]CLEC4M")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "ACE2[HA]")$geomean),
             "untagged" = c(subset(receptors_ungrouped_summary, recombined_construct == "BSG")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "Nrp1")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "NRP2")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "CLEC4M")$geomean,
                          subset(receptors_ungrouped_summary, recombined_construct == "ACE2")$geomean))

Receptors_scatterplot <- ggplot() + theme_bw() + theme(panel.grid.minor = element_blank()) + 
  scale_color_manual(values = virus_colors) +
  geom_abline(slope = 1, intercept = 0, alpha = 0.2, size = 4) +
  scale_x_log10() + scale_y_log10() + labs(x = "Untagged protein", y = "Tagged protein") +
  geom_point(data = tagged_vs_untagged_receptors_dataframe, aes(x = untagged, y = tagged, color = virus_label, shape = gene), size = 3, alpha = 0.5)
Receptors_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Comparing%20the%20HA-tagged%20and%20untagged%20formats-1.png)<!-- -->

``` r
ggsave(file = "Plots/Receptors_scatterplot.pdf", Receptors_scatterplot, height = 2, width = 4)
ggsave(file = "Plots/Receptors_scatterplot.png", Receptors_scatterplot, height = 2, width = 4)


paste("The Pearson's r^2 of the untagged and tagged protein infection data is:",round(cor(tagged_vs_untagged_receptors_dataframe$tagged, tagged_vs_untagged_receptors_dataframe$untagged, method = "pearson")^2,2))
```

    ## [1] "The Pearson's r^2 of the untagged and tagged protein infection data is: 0.98"

``` r
### Make the statistical test to see which proteins reproducibly increase infectivity
full_variant_t_test <- data.frame("cell_label" = rep(unique(receptors_grouped_summary$receptor_grouped),each = length(unique(receptors_grouped_summary$virus_label))),
                                          "virus_label" =  rep(unique(receptors_grouped_summary$virus_label),length(unique(receptors_grouped_summary$receptor_grouped))),
                                          "p_value" = NA,"significant" = NA)

for(x in 1:nrow(full_variant_t_test)){
  temp_cell_label <- full_variant_t_test$cell_label[x]
  temp_pseudovirus_env <- full_variant_t_test$virus_label[x]
  temp_subset <- receptors_grouped %>% filter(receptor_grouped == temp_cell_label & virus_label == temp_pseudovirus_env)
  temp_p_value <- round(t.test(temp_subset$ace2dep_infection,rep(1,nrow(temp_subset)), alternative = "two.sided")$p.value,4)
  full_variant_t_test$p_value[x] <- temp_p_value
}
full_variant_t_test$corrected_p_value <- p.adjust(full_variant_t_test$p_value, method = 'BH')

full_variant_t_test[full_variant_t_test$corrected_p_value < 0.01,"significant"] <- "yes"


## Now plotting the data with indicators of the statistical test

receptors_panel <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), legend.position = "right") +
  scale_y_log10(limits = c(0.3,4e2)) + 
  labs(x = element_blank(), y = "Fold increase\nto infection") +
  scale_color_manual(values = virus_colors) +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_point(data = receptors_grouped, aes(x = receptor_grouped, y = ace2dep_infection, color = virus_label), position = position_jitterdodge(jitter.height = 0, dodge.width = 0.6), alpha = 0.2, size = 1) +
  geom_errorbar(data = receptors_grouped_summary, aes(x = receptor_grouped, ymin = lower_ci, ymax = upper_ci, color = virus_label), position = position_dodge(width = 0.6), alpha = 0.6, width = 0.4) +
  geom_point(data = receptors_grouped_summary, aes(x = receptor_grouped, y = geomean, color = virus_label), position = position_dodge(width = 0.6), size = 8, shape = 95) +
  geom_point(data = full_variant_t_test %>% filter(significant == "yes"), aes(x = cell_label, y = 300, color = virus_label), position = position_dodge(width = 0.5), size = 1.5, shape = 8) +
  NULL
receptors_panel
```

![](ACE2_dependence_files/figure-gfm/Comparing%20the%20HA-tagged%20and%20untagged%20formats-2.png)<!-- -->

``` r
ggsave(file = "Plots/Receptors_panel.pdf", receptors_panel, height = 1.5, width = 4.8)
ggsave(file = "Plots/Receptors_panel.png", receptors_panel, height = 1.5, width = 4.8)



paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "ACE2" & virus_label == "SARS-CoV")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 9.9"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "ACE2" & virus_label == "SARS-CoV-2")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 12"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "ACE2" & virus_label == "VSV")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 1"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "CLEC4M" & virus_label == "SARS-CoV-2")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 2.8"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "CLEC4M" & virus_label == "SARS-CoV")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 1.7"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "NRP1" & virus_label == "SARS-CoV-2")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 1.5"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "NRP2" & virus_label == "SARS-CoV-2")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 1.5"

``` r
paste("ACE2 increased SARS-CoV pseudovirus infection roughly:",round(subset(receptors_grouped_summary, receptor_grouped == "NRP2" & virus_label == "VSV")$geomean,1))
```

    ## [1] "ACE2 increased SARS-CoV pseudovirus infection roughly: 1.5"

## Allright, so now we can focus on ACE2

``` r
two_color_ace2_dep <- two_color_combined %>% filter(expt == "Two_color" & pseudovirus_env != "none" & recombined_construct %in% c("G752A/G758A","G752A","G758A/G852C"))
two_color_ace2_dep$index <- seq(1,nrow(two_color_ace2_dep))
two_color_ace2_dep$log10_nir_red_diff <- log10(two_color_ace2_dep$moi_gvn_nir) - log10(two_color_ace2_dep$moi_gvn_red)

two_color_ace2_dep2 <- two_color_ace2_dep %>% group_by(date, virus_label) %>% 
  summarize(log10_nir_red_diff = mean(log10_nir_red_diff), pct_grn_gvn_red = mean(pct_grn_gvn_red), pct_grn_gvn_nir = mean(pct_grn_gvn_nir), ratio_nir_mcherry = mean(ratio_nir_mcherry), .groups = "drop") %>% 
  mutate(n = 1, ace2dep_infection = 10^log10_nir_red_diff)

two_color_ace2_dep_summary <- two_color_ace2_dep2 %>% group_by(virus_label) %>% 
  summarize(mean_log10_nir_red_diff = mean(log10_nir_red_diff), sd_log10_nir_red_diff = sd(log10_nir_red_diff), n = sum(n), .groups = "drop") %>%
  mutate(se_log10_nir_red_diff = sd_log10_nir_red_diff / sqrt(n), geomean = 10^mean_log10_nir_red_diff, lower_ci = 10^(mean_log10_nir_red_diff - se_log10_nir_red_diff * 1.96), upper_ci = 10^(mean_log10_nir_red_diff + se_log10_nir_red_diff * 1.96), cells = "ACE2")

two_color_ace2_dep_raw <- data.frame("virus_label" = c(two_color_ace2_dep2$virus_label,two_color_ace2_dep2$virus_label),
                                  "variable" = c(rep("nir",nrow(two_color_ace2_dep2)),rep("mCherry",nrow(two_color_ace2_dep2))),
                                  "value" = c(two_color_ace2_dep2$pct_grn_gvn_nir,two_color_ace2_dep2$pct_grn_gvn_red))
```

``` r
diverse_virus_labels <- c("VSV", "Ebolavirus Zaire","Marburgvirus","Lassa fever virus","LCMV","Junin virus","MERS-CoV", "SARS-CoV", "WIV1-CoV", "SARS-CoV-2")

## Show the raw infectivities first
diverse_virus_subset_raw <- two_color_ace2_dep_raw %>% filter(virus_label %in% diverse_virus_labels)
diverse_virus_subset_raw$virus_label <- factor(diverse_virus_subset_raw$virus_label, levels = diverse_virus_labels)

Diverse_virus_subset_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), legend.position = "none") +
  scale_y_log10() + #limits = c(1e-1,2e3)) + 
  scale_color_manual(values = c("red","black")) +
  labs(x = element_blank(), y = "Percent GFP positive cells") +
  geom_jitter(data = diverse_virus_subset_raw, aes(x = virus_label, y = value, color = variable), position = position_dodge(width = 0.4), alpha = 0.4) +
  geom_hline(yintercept = 0.005, linetype = 2)
Diverse_virus_subset_plot
```

![](ACE2_dependence_files/figure-gfm/Testing%20a%20diverse%20panel%20of%20viral%20envelopes-1.png)<!-- -->

``` r
ggsave(file = "Plots/Diverse_virus_subset_plot.pdf", Diverse_virus_subset_plot, height = 3, width = 4.5)
ggsave(file = "Plots/Diverse_virus_subset_plot.png", Diverse_virus_subset_plot, height = 3, width = 4.5)

### Now look at the ACE2 dependent infection of each
diverse_virus_subset <- two_color_ace2_dep2 %>% filter(virus_label %in% diverse_virus_labels)
diverse_virus_subset$virus_label <- factor(diverse_virus_subset$virus_label, levels = diverse_virus_labels)
diverse_virus_subset_summary <- two_color_ace2_dep_summary %>% filter(virus_label %in% diverse_virus_labels)
diverse_virus_subset_summary$virus_label <- factor(diverse_virus_subset_summary$virus_label, levels = diverse_virus_labels)

## Incorporate a statistical test here as well
diverse_virus_panel_t_test <- data.frame("virus_label" =  rep(unique(diverse_virus_subset$virus_label)), "mean_value" = NA,"p_value" = NA, "significant" = NA)
for(x in 1:nrow(diverse_virus_panel_t_test)){
  temp_pseudovirus_env <- diverse_virus_panel_t_test$virus_label[x]
  temp_subset <- diverse_virus_subset %>% filter(virus_label == temp_pseudovirus_env)
  diverse_virus_panel_t_test$mean_value[x] <- mean(temp_subset$ace2dep_infection)
  temp_p_value <- round(t.test(temp_subset$ace2dep_infection,rep(1,nrow(temp_subset)), alternative = "two.sided")$p.value,4)
  diverse_virus_panel_t_test$p_value[x] <- temp_p_value
}
diverse_virus_panel_t_test$corrected_p_value <- p.adjust(diverse_virus_panel_t_test$p_value, method = 'BH')
diverse_virus_panel_t_test[diverse_virus_panel_t_test$corrected_p_value < 0.05 & diverse_virus_panel_t_test$mean_value > 1,"significant"] <- "yes"

## Now plot the data
Two_color_ACE2_dep_panel <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), panel.grid.minor.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) +
  scale_y_log10(limits = c(3e-1,2e3), expand = c(0,0), breaks = c(1,100)) + 
  labs(x = element_blank(), y = "Ratio of iRFP670 to\nmCherry infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_quasirandom(data = diverse_virus_subset, aes(x = virus_label, y = ace2dep_infection), position = position_jitter(width = 0.1), alpha = 0.2, size = 1) +
  geom_errorbar(data = diverse_virus_subset_summary, aes(x = virus_label, ymin = lower_ci, ymax = upper_ci), alpha = 0.6, width = 0.4) +
  geom_point(data = diverse_virus_subset_summary, aes(x = virus_label, y = geomean), size = 8, shape = 95) +
  #geom_point(data = diverse_virus_panel_t_test %>% filter(significant == "yes"), aes(x = virus_label, y = 1200), size = 1, shape = 8) +
  NULL
Two_color_ACE2_dep_panel
```

![](ACE2_dependence_files/figure-gfm/Testing%20a%20diverse%20panel%20of%20viral%20envelopes-2.png)<!-- -->

``` r
ggsave(file = "Plots/Two_color_ACE2_dep_panel.pdf", Two_color_ACE2_dep_panel, height = 1.3, width = 3)
ggsave(file = "Plots/Two_color_ACE2_dep_panel.png", Two_color_ACE2_dep_panel, height = 1.3, width = 3)
```

``` r
rbd_parsed_df <- read.delim(file = "Data/Alignment/211208_RBD_main_fig/RBDs_aligned_identity_matrix_items.tsv", header = F, stringsAsFactors = F, sep = "\t")
rbd_dist_matrix <- read.delim(file = "Data/Alignment/211208_RBD_main_fig/RBDs_aligned_identity_matrix.csv", header = F, stringsAsFactors = F, sep = ",")

colnames(rbd_dist_matrix) <- rbd_parsed_df$V1 #paste("c_",rbd_parsed_df$V1,sep="")
rownames(rbd_dist_matrix) <- rbd_parsed_df$V1 #paste("r_",rbd_parsed_df$V1,sep="")

rbd_dist_matrix_hclust <- hclust(as.dist(rbd_dist_matrix, diag = TRUE))

rbd_dist_matrix2 <- rbd_dist_matrix
rbd_dist_matrix2$species <- rownames(rbd_dist_matrix2)

rbd_dist_melted <- melt(rbd_dist_matrix2, id = "species")
rbd_dist_melted$variable <- as.character(rbd_dist_melted$variable)

rbd_dist_melted$species <- factor(rbd_dist_melted$species, levels = rbd_dist_matrix_hclust$labels)
rbd_dist_melted$variable <- factor(rbd_dist_melted$variable, levels = rbd_dist_matrix_hclust$labels)

rbd_identity_matrix_plot <- ggplot() + theme_bw() +
  theme(axis.text = element_text(size = 8), axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) +
  labs(x = NULL, y = NULL, fill = NULL) +
  scale_fill_continuous(low = "white", high = "black") +
  geom_tile(data = rbd_dist_melted, aes(x = species, y = variable, fill = value)) +
  geom_text(data = rbd_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value <= 40), aes(x = species, y = variable, label = value), size = 2) +
  geom_text(data = rbd_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value >= 40), aes(x = species, y = variable, label = value), size = 2, color = "grey70") +
  NULL
ggsave(file = "Plots/RBD_identity_matrix_plot.pdf", rbd_identity_matrix_plot, height = 5.1, width = 6)
rbd_identity_matrix_plot
```

![](ACE2_dependence_files/figure-gfm/Initial%20RBD%20identity%20matrix-1.png)<!-- -->

``` r
rbd_parsed_df <- read.delim(file = "Data/Alignment/211207_All_RBDs/All_RBDs_aligned_identity_matrix_items.tsv", header = F, stringsAsFactors = F, sep = "\t")
rbd_dist_matrix <- read.delim(file = "Data/Alignment/211207_All_RBDs/All_RBDs_aligned_identity_matrix.csv", header = F, stringsAsFactors = F, sep = ",")

colnames(rbd_dist_matrix) <- rbd_parsed_df$V1 #paste("c_",rbd_parsed_df$V1,sep="")
rownames(rbd_dist_matrix) <- rbd_parsed_df$V1 #paste("r_",rbd_parsed_df$V1,sep="")

rbd_dist_matrix_hclust <- hclust(as.dist(rbd_dist_matrix, diag = TRUE))

rbd_dist_matrix2 <- rbd_dist_matrix
rbd_dist_matrix2$species <- rownames(rbd_dist_matrix2)

rbd_dist_melted <- melt(rbd_dist_matrix2, id = "species")
rbd_dist_melted$variable <- as.character(rbd_dist_melted$variable)

rbd_dist_melted$species <- factor(rbd_dist_melted$species, levels = rbd_dist_matrix_hclust$labels)
rbd_dist_melted$variable <- factor(rbd_dist_melted$variable, levels = rbd_dist_matrix_hclust$labels)

rbd_identity_matrix_plot <- ggplot() + theme_bw() +
  theme(axis.text = element_text(size = 8), axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) +
  labs(x = NULL, y = NULL, fill = NULL) +
  scale_fill_continuous(low = "white", high = "black") +
  geom_tile(data = rbd_dist_melted, aes(x = species, y = variable, fill = value)) +
  geom_text(data = rbd_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value <= 40), aes(x = species, y = variable, label = value), size = 2) +
  geom_text(data = rbd_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value >= 40), aes(x = species, y = variable, label = value), size = 2, color = "grey70") +
  NULL
#rbd_identity_matrix_plot
ggsave(file = "Plots/All_RBD_identity_matrix_plot.pdf", rbd_identity_matrix_plot, height = 5.3*2, width = 6*2)


clade_frame <- data.frame("species" = c("Yunnan2011__C.plicata","Rf4092__Rhinolophus_ferrumequium","ZXC21__Rhinolophus_sinicus","279-2005_R.macrotis","Rs4237__Rhinolophus_sinicus","Rp3__Rhinolophus_pearsonii","JL2012__Rhinolophus_ferrumequinum","73-2005__Rhinolophus_ferrumequium","Rf1__Rhinolophus_ferrumequium","HeB2013__Rhinolophus_ferrumequium","HuB2013__Rhinolophus_sinicus","Rs806/2006__Rhinolophus_sinicus","tRI-SC2018__Rhinolophus","Shaanxi2011__Rhinolophus_pusillus","Rs4081__Rhinolophus_sinicus","Rs4237__Rhinolophus_sinicus",
"YN2013__Rhinolophus_sinicus","ZC45__R.sinicus","SARS_CoV-2__Homo_sapiens","RaTG13__Rhinolophus_affinis",
"Rs4084__Rhinolophus_sinicus","Rs4231__Rhinolophus_sinicus","RsSHC014__Rhinolophus_sinicus","SARS_CoV__Homo_sapiens",
"RaTG15__Rhinolophus_affinis","LYRa11__Rhinolophus_affinis","Rs7327__Rhinolophus_sinicus","WIV1__Rhinolophus_sinicus",
"RhGB01__Rhinolophus_hipposideros","Khosta2__Rhinolophus_hipposideros","BtKY72__Rhinolophus","Khosta1__Rhinolophus_ferrumequinum",
"BB9904__Rhinolophus_euryale","BM48-31__Rhinolophus_blasii","PRD-2386__Rhinolophus","PRD-0038__Rhinolophus"), "clade_species" = c(2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3))
clade_frame$variable <- clade_frame$species
clade_frame$clade_variable <- clade_frame$clade_species

rbd_dist_melted2 <- merge(rbd_dist_melted, clade_frame[,c("species","clade_species")], by = "species")
rbd_dist_melted3 <- merge(rbd_dist_melted2, clade_frame[,c("variable","clade_variable")], by = "variable")

Clade_difference_plot <- ggplot() + theme(panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank()) + 
  labs(x = "Clade", y = "Amino acid\ndifferences") +
  scale_y_continuous(breaks = c(0,50,100), limits = c(0,100)) +
  geom_quasirandom(data = rbd_dist_melted3, aes(x = clade_species, y = value), alpha = 0.1, size = 0.25) + facet_grid(cols = vars(clade_variable))
ggsave(file = "Plots/Clade_difference_plot.pdf", Clade_difference_plot, height = 1.2, width = 2.5)
Clade_difference_plot
```

![](ACE2_dependence_files/figure-gfm/Clade-wise%20differences%20in%20RBD%20sequences-1.png)<!-- -->

## Now looking at infection data with the panel of RBDs

``` r
rbd_label_levels <- c("WIV1 RBD", "SARS-CoV-2 RBD", "Rp3 RBD", "Rs4237 RBD", "YN2013 RBD","BtKY72 RBD", "BM48-31 RBD", "BB9904 RBD")

rbd_subset_raw <- two_color_ace2_dep_raw %>% filter(virus_label %in% rbd_label_levels)
rbd_subset_raw$virus_label <- factor(rbd_subset_raw$virus_label, levels = rbd_label_levels)

Rbd_subset_raw_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), legend.position = "none") +
  scale_y_log10() + #limits = c(1e-1,2e3)) + 
  scale_color_manual(values = c("red","black")) +
  labs(x = element_blank(), y = "Percent GFP positive cells") +
  geom_jitter(data = rbd_subset_raw, aes(x = virus_label, y = value, color = variable), position = position_dodge(width = 0.4), alpha = 0.4) +
  geom_hline(yintercept = 0.005, linetype = 2)
Rbd_subset_raw_plot
```

![](ACE2_dependence_files/figure-gfm/RBD%20panel%20with%20ACE2-1.png)<!-- -->

``` r
ggsave(file = "Plots/Rbd_subset_raw_plot.pdf", Rbd_subset_raw_plot, height = 3, width = 4.5)

rbd_subset2 <- two_color_ace2_dep2 %>% filter(virus_label %in% rbd_label_levels)
rbd_subset2$virus_label <- factor(rbd_subset2$virus_label, levels = rbd_label_levels)

rbd_subset_summary <- two_color_ace2_dep_summary %>% filter(virus_label %in% rbd_label_levels)
rbd_subset_summary$virus_label <- factor(rbd_subset_summary$virus_label, levels = rbd_label_levels)


## Incorporate a statistical test here as well
rbd_panel_t_test <- data.frame("virus_label" =  rep(unique(rbd_subset2$virus_label)), "mean_value" = NA,"p_value" = NA, "significant" = NA)
for(x in 1:nrow(rbd_panel_t_test)){
  temp_pseudovirus_env <- rbd_panel_t_test$virus_label[x]
  temp_subset <- rbd_subset2 %>% filter(virus_label == temp_pseudovirus_env)
  rbd_panel_t_test$mean_value[x] <- mean(temp_subset$ace2dep_infection)
  temp_p_value <- round(t.test(temp_subset$ace2dep_infection,rep(1,nrow(temp_subset)), alternative = "two.sided")$p.value,4)
  rbd_panel_t_test$p_value[x] <- temp_p_value
}
rbd_panel_t_test$corrected_p_value <- p.adjust(rbd_panel_t_test$p_value, method = 'BH')
rbd_panel_t_test[rbd_panel_t_test$corrected_p_value < 0.05 & rbd_panel_t_test$mean_value > 2,"significant"] <- "yes"


## Plotting the RBD data
Rbd_subset_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) +
  scale_y_log10(limits = c(3e-1,5e3), expand = c(0,0)) + 
  labs(x = element_blank(), y = "Fold human ACE2\n-dependent infection") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_quasirandom(data = rbd_subset2, aes(x = virus_label, y = ace2dep_infection), position = position_jitter(width = 0.1), alpha = 0.2, size = 1) +
  geom_errorbar(data = rbd_subset_summary, aes(x = virus_label, ymin = lower_ci, ymax = upper_ci), alpha = 0.6, width = 0.4) +
  geom_point(data = rbd_subset_summary, aes(x = virus_label, y = geomean), size = 8, shape = 95) +
  geom_point(data = rbd_panel_t_test %>% filter(significant == "yes"), aes(x = virus_label, y = 3000), size = 1.5, shape = 8) +
  NULL
Rbd_subset_plot
```

![](ACE2_dependence_files/figure-gfm/RBD%20panel%20with%20ACE2-2.png)<!-- -->

``` r
ggsave(file = "Plots/RBD_subset_plot.pdf", Rbd_subset_plot, height = 1.75, width = 2.5)
ggsave(file = "Plots/RBD_subset_plot.png", Rbd_subset_plot, height = 1.75, width = 2.5)

rbd_subset2$cells <- "ACE2"
rbd_subset2$dep_infection <- rbd_subset2$ace2dep_infection

rbd_subset_summary$cells <- "ACE2"
```

## OK, so maybe we can increase our sensitivity by adding TMPRSS2 into the mix

``` r
two_color_ace2_tmprss2_dep <- two_color_combined %>% filter(expt == "Two_color_ACE2_TMPRSS2" & pseudovirus_env != "none")
two_color_ace2_tmprss2_dep$index <- seq(1,nrow(two_color_ace2_tmprss2_dep))
two_color_ace2_tmprss2_dep$log10_nir_red_diff <- log10(two_color_ace2_tmprss2_dep$moi_gvn_nir) - log10(two_color_ace2_tmprss2_dep$moi_gvn_red)

two_color_ace2_tmprss2_dep2 <- two_color_ace2_tmprss2_dep %>% group_by(date, virus_label) %>% 
  summarize(log10_nir_red_diff = mean(log10_nir_red_diff), pct_grn_gvn_red = mean(pct_grn_gvn_red), pct_grn_gvn_nir = mean(pct_grn_gvn_nir), .groups = "drop") %>% 
  mutate(ace2_tmprss2_dep_infection = 10^log10_nir_red_diff, n = 1)

two_color_ace2_tmprss2_dep_summary <- two_color_ace2_tmprss2_dep2 %>% group_by(virus_label) %>% 
  summarize(mean_log10_nir_red_diff = mean(log10_nir_red_diff), sd_log10_nir_red_diff = sd(log10_nir_red_diff), n = sum(n), .groups = "drop") %>%
  mutate(se_log10_nir_red_diff = sd_log10_nir_red_diff / sqrt(n), geomean = 10^mean_log10_nir_red_diff, lower_ci = 10^(mean_log10_nir_red_diff - se_log10_nir_red_diff * 1.96), upper_ci = 10^(mean_log10_nir_red_diff + se_log10_nir_red_diff * 1.96), cells = "ACE2")

## Compare the control viruses with ACE2 dependent enhancement or ACE2 + TMPRSS2 dependent enhancement
two_color_ace2_dep_summary_controls <- two_color_ace2_dep_summary %>% filter(virus_label %in% c("Junin virus", "SARS-CoV", "SARS[SARS-CoV-2 RBD]"))
two_color_ace2_tmprss2_dep_summary_controls <- two_color_ace2_tmprss2_dep_summary %>% filter(virus_label %in% c("Junin virus", "SARS-CoV", "SARS[SARS-CoV-2 RBD]"))
ace2_with_tmprss2_controls <- merge(two_color_ace2_dep_summary_controls[,c("virus_label","geomean")], two_color_ace2_tmprss2_dep_summary_controls[,c("virus_label","geomean")], by = "virus_label")
colnames(ace2_with_tmprss2_controls) <- c("virus_label","ace2","ace2tmprss2")

## Weird. Maybe the values were maxed out or something?
```

``` r
two_color_ace2_tmprss2_dep2_rbds <- two_color_ace2_tmprss2_dep2 %>% filter(virus_label %in% rbd_label_levels)
two_color_ace2_tmprss2_dep2_rbds$virus_label <- factor(two_color_ace2_tmprss2_dep2_rbds$virus_label, levels = rbd_label_levels)

two_color_ace2_tmprss2_dep_summary_rbds<- two_color_ace2_tmprss2_dep_summary %>% filter(virus_label %in% rbd_label_levels)
two_color_ace2_tmprss2_dep_summary_rbds$virus_label <- factor(two_color_ace2_tmprss2_dep_summary_rbds$virus_label, levels = rbd_label_levels)

ACE2_TMPRSS2_RBDs_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) +
  scale_y_log10(limits = c(3e-1,1e3)) + 
  labs(x = element_blank(), y = "Ratio of mCherry to iRFP670 infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_quasirandom(data = two_color_ace2_tmprss2_dep2_rbds, aes(x = virus_label, y = ace2_tmprss2_dep_infection), position = position_jitter(width = 0.1), alpha = 0.4) +
  geom_errorbar(data = two_color_ace2_tmprss2_dep_summary_rbds, aes(x = virus_label, ymin = lower_ci, ymax = upper_ci), alpha = 0.6, width = 0.4) +
  geom_point(data = two_color_ace2_tmprss2_dep_summary_rbds, aes(x = virus_label, y = geomean), size = 8, shape = 95)
ACE2_TMPRSS2_RBDs_plot
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20the%20RBD%20panel%20with%20ACE2%20and%20TMPRSS2-1.png)<!-- -->

``` r
ggsave(file = "Plots/ACE2_TMPRSS2_RBDs_plot.pdf", ACE2_TMPRSS2_RBDs_plot, height = 2, width = 4.5)
ggsave(file = "Plots/ACE2_TMPRSS2_RBDs_plot.png", ACE2_TMPRSS2_RBDs_plot, height = 2, width = 4.5)

two_color_ace2_tmprss2_dep2_rbds$cells <- "ACE2-2A-TMPRSS2"
two_color_ace2_tmprss2_dep2_rbds$dep_infection <- two_color_ace2_tmprss2_dep2_rbds$ace2_tmprss2_dep_infection

two_color_ace2_tmprss2_dep_summary_rbds$cells <- "ACE2-2A-TMPRSS2"
```

``` r
rbds_both_dataset <- rbind(rbd_subset2[,c("virus_label","cells","dep_infection")], two_color_ace2_tmprss2_dep2_rbds[,c("virus_label","cells","dep_infection")])

rbds_both_dataset_summary <- rbind(rbd_subset_summary[,c("virus_label","cells","geomean","lower_ci","upper_ci")], two_color_ace2_tmprss2_dep_summary_rbds[,c("virus_label","cells","geomean","lower_ci","upper_ci")])

ACE2_ACE2TMPRSS2_bothplot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), legend.position = "none", panel.grid.minor = element_blank()) +
  scale_y_log10(limits = c(3e-1,1e3)) + 
  labs(x = element_blank(), y = "Ratio of mCherry to iRFP670 infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_jitter(data = rbds_both_dataset, aes(x = virus_label, y = dep_infection, color = cells), alpha = 0.4, position = position_dodge(width = 0.8)) +
  geom_errorbar(data = rbds_both_dataset_summary, aes(x = virus_label, ymin = lower_ci, ymax = upper_ci, color = cells), alpha = 0.4, width = 0.2, position = position_dodge(width = 0.8)) +
  geom_point(data = rbds_both_dataset_summary, aes(x = virus_label, y = geomean, color = cells), size = 8, shape = 95, position = position_dodge(width = 0.8))
ACE2_ACE2TMPRSS2_bothplot
```

![](ACE2_dependence_files/figure-gfm/Comparing%20the%20RBD%20panel%20data%20with%20ACE2%20only%20or%20ACE2%20and%20TMPRSS2-1.png)<!-- -->

``` r
ggsave(file = "Plots/ACE2_ACE2TMPRSS2_bothplot.pdf", ACE2_ACE2TMPRSS2_bothplot, height = 2, width = 4)
ggsave(file = "Plots/ACE2_ACE2TMPRSS2_bothplot.png", ACE2_ACE2TMPRSS2_bothplot, height = 2, width = 4)


two_color_ace2_dep_summary_rbds <- two_color_ace2_dep_summary %>% filter(virus_label %in% c("Junin virus", "SARS-CoV","WIV1 RBD", "SARS-CoV-2 RBD", "Rp3 RBD", "YN2013 RBD", "BM48-31 RBD", "BB9904 RBD", "Rs4237 RBD", "BtKY72 RBD"))
two_color_ace2_tmprss2_dep_summary_rbds <- two_color_ace2_tmprss2_dep_summary %>% filter(virus_label %in% c("Junin virus", "SARS-CoV","WIV1 RBD", "SARS-CoV-2 RBD", "Rp3 RBD", "YN2013 RBD","BM48-31 RBD", "BB9904 RBD", "Rs4237 RBD", "BtKY72 RBD"))
ace2_with_tmprss2_rbds <- merge(two_color_ace2_dep_summary_rbds[,c("virus_label","geomean")], two_color_ace2_tmprss2_dep_summary_rbds[,c("virus_label","geomean")], by = "virus_label")
colnames(ace2_with_tmprss2_rbds) <- c("virus_label","ace2","ace2tmprss2")

ACE2_ACE2TMPRSS2_scatterplot <- ggplot() + theme_bw() + 
  scale_x_log10(limits = c(0.3,300), breaks = c(1,10,100)) + 
  scale_y_log10(limits = c(0.3,100), breaks = c(1,10,100)) +
  geom_abline(slope = 1, intercept = 0, alpha = 0.2, size = 4) +
  geom_text_repel(data = ace2_with_tmprss2_rbds, aes(x = ace2, y = ace2tmprss2, label = virus_label), color = "red", segment.color = "orange", size = 2) +
  geom_point(data = ace2_with_tmprss2_rbds, aes(x = ace2, y = ace2tmprss2), alpha = 0.5)
ACE2_ACE2TMPRSS2_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Comparing%20the%20RBD%20panel%20data%20with%20ACE2%20only%20or%20ACE2%20and%20TMPRSS2-2.png)<!-- -->

``` r
ggsave(file = "Plots/ACE2_ACE2TMPRSS2_scatterplot.pdf", ACE2_ACE2TMPRSS2_scatterplot, height = 1.5, width = 2)
```

    ## Warning: ggrepel: 6 unlabeled data points (too many overlaps). Consider
    ## increasing max.overlaps

``` r
ggsave(file = "Plots/ACE2_ACE2TMPRSS2_scatterplot.png", ACE2_ACE2TMPRSS2_scatterplot, height = 1.5, width = 2)
```

    ## Warning: ggrepel: 6 unlabeled data points (too many overlaps). Consider
    ## increasing max.overlaps

``` r
btky72_fold_increase <- as.numeric(rbds_both_dataset_summary[rbds_both_dataset_summary$virus_label == "BtKY72 RBD" & rbds_both_dataset_summary$cells == "ACE2-2A-TMPRSS2","geomean"])
```

``` r
btky72_label_levels <- c("Junin virus", "BtKY72 RBD", "BtKY72 1-539", "BtKY72 1-888", "BtKY72 1-955")

btky72_subset_raw <- two_color_ace2_dep_raw %>% filter(virus_label %in% btky72_label_levels)
btky72_subset_raw$virus_label <- factor(btky72_subset_raw$virus_label, levels = btky72_label_levels)

btky72_subset_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), legend.position = "none", panel.grid.minor = element_blank()) +
  scale_y_log10() + #limits = c(1e-1,2e3)) + 
  scale_color_manual(values = c("red","black")) +
  labs(x = element_blank(), y = "Percent GFP positive cells") +
  geom_jitter(data = btky72_subset_raw, aes(x = virus_label, y = value, color = variable), position = position_dodge(width = 0.4), alpha = 0.4) +
  geom_hline(yintercept = 0.005, linetype = 2)
btky72_subset_plot
```

![](ACE2_dependence_files/figure-gfm/Honing%20in%20on%20the%20BtKY72-1.png)<!-- -->

``` r
ggsave(file = "Plots/btky72_subset_plot.pdf", btky72_subset_plot, height = 3, width = 4.5)

btky72_subset <- two_color_ace2_dep2 %>% filter(virus_label %in% btky72_label_levels)
btky72_subset$virus_label <- factor(btky72_subset$virus_label, levels = btky72_label_levels)

btky72_subset_summary <- two_color_ace2_dep_summary %>% filter(virus_label %in% btky72_label_levels)
btky72_subset_summary$virus_label <- factor(btky72_subset_summary$virus_label, levels = btky72_label_levels)

Ace2_btky72_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), panel.grid.minor = element_blank()) +
  scale_y_log10(limits = c(0.3,100), breaks = c(1,10,100)) + 
  labs(x = element_blank(), y = "Ratio of iRFP670 to mCherry infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  #geom_hline(yintercept = btky72_fold_increase, linetype = 2, alpha = 0.4, color = "red") +
  geom_quasirandom(data = btky72_subset, aes(x = virus_label, y = ace2dep_infection), position = position_jitter(width = 0.1), alpha = 0.4) +
  geom_errorbar(data = btky72_subset_summary, aes(x = virus_label, ymin = lower_ci, ymax = upper_ci), alpha = 0.4, width = 0.2) +
  geom_point(data = btky72_subset_summary, aes(x = virus_label, y = geomean), size = 8, shape = 95)
Ace2_btky72_plot
```

![](ACE2_dependence_files/figure-gfm/Honing%20in%20on%20the%20BtKY72-2.png)<!-- -->

``` r
ggsave(file = "Plots/Ace2_btky72_plot.pdf", Ace2_btky72_plot, height = 1.75, width = 4)
ggsave(file = "Plots/Ace2_btky72_plot.png", Ace2_btky72_plot, height = 1.75, width = 4)
```

``` r
btky72_label_levels2 <- c("Junin virus", "BtKY72 RBD", "BtKY72 RBD [Y488H]", "BtKY72 RBD [T499E]", "BtKY72 1-539", "BtKY72 1-888", "BtKY72 1-955", "BtKY72 1-120;329-539", "BtKY72 112-206;329-539", "BtKY72 214-328;329-539")

two_color_ace2_tmprss2_dep2_btky72 <- two_color_ace2_tmprss2_dep2 %>% filter(virus_label %in% btky72_label_levels2) 
two_color_ace2_tmprss2_dep2_btky72$virus_label <- factor(two_color_ace2_tmprss2_dep2_btky72$virus_label, levels = btky72_label_levels2)

two_color_ace2_tmprss2_dep_summary_btky72 <- two_color_ace2_tmprss2_dep_summary %>% filter(virus_label %in% btky72_label_levels2) 
two_color_ace2_tmprss2_dep_summary_btky72$virus_label <- factor(two_color_ace2_tmprss2_dep_summary_btky72$virus_label, levels = btky72_label_levels2)

ACE2_TMPRSS2_btky72_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1), panel.grid.minor.x = element_blank()) +
  scale_y_log10(limits = c(3e-1,1e2)) + 
  labs(x = element_blank(), y = "Ratio of mCherry to iRFP670 infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_quasirandom(data = two_color_ace2_tmprss2_dep2_btky72, aes(x = virus_label, y = ace2_tmprss2_dep_infection), position = position_jitter(width = 0.1), alpha = 0.4) +
  geom_errorbar(data = two_color_ace2_tmprss2_dep_summary_btky72, aes(x = virus_label, ymin = lower_ci, ymax = upper_ci), alpha = 0.4, width = 0.2) +
  geom_point(data = two_color_ace2_tmprss2_dep_summary_btky72, aes(x = virus_label, y = geomean), size = 12, shape = 95)
ACE2_TMPRSS2_btky72_plot
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20the%20BtKY72%20panel%20with%20ACE2%20and%20TMPRSS2-1.png)<!-- -->

``` r
ggsave(file = "Plots/ACE2_TMPRSS2_btky72_plot.pdf", ACE2_TMPRSS2_btky72_plot, height = 2, width = 4)
ggsave(file = "Plots/ACE2_TMPRSS2_btky72_plot.png", ACE2_TMPRSS2_btky72_plot, height = 2, width = 4)

two_color_ace2_dep_summary_btky72_segments <- two_color_ace2_dep_summary %>% filter(virus_label %in% c("Junin virus", "BtKY72 RBD", "BtKY72 1-539", "BtKY72 1-888", "BtKY72 1-955","BtKY72 1-539", "BtKY72 1-888", "BtKY72 1-955", "BtKY72 1-120;329-539", "BtKY72 112-206;329-539", "BtKY72 214-328;329-539"))
two_color_ace2_tmprss2_dep_summary_btky72_segments <- two_color_ace2_tmprss2_dep_summary %>% filter(virus_label %in% c("Junin virus", "BtKY72 RBD", "BtKY72 1-539", "BtKY72 1-888", "BtKY72 1-955","BtKY72 1-539", "BtKY72 1-888", "BtKY72 1-955", "BtKY72 1-120;329-539", "BtKY72 112-206;329-539", "BtKY72 214-328;329-539"))
ace2_with_tmprss2_btky72_segments <- merge(two_color_ace2_dep_summary_btky72_segments[,c("virus_label","geomean")], two_color_ace2_tmprss2_dep_summary_btky72_segments[,c("virus_label","geomean")], by = "virus_label")
colnames(ace2_with_tmprss2_btky72_segments) <- c("virus_label","ace2","ace2tmprss2")

ACE2_ACE2TMPRSS2_BtKY72_subpanel_scatterplot <- ggplot() + theme_bw() + scale_x_log10() + scale_y_log10() +
  geom_abline(slope = 1, intercept = 0, alpha = 0.2, size = 4) +
  geom_text_repel(data = ace2_with_tmprss2_btky72_segments, aes(x = ace2, y = ace2tmprss2, label = virus_label), color = "red", segment.color = "orange") +
  geom_point(data = ace2_with_tmprss2_btky72_segments, aes(x = ace2, y = ace2tmprss2))
ggsave(file = "Plots/ACE2_ACE2TMPRSS2_BtKY72_subpanel_scatterplot.pdf", ACE2_ACE2TMPRSS2_BtKY72_subpanel_scatterplot, height = 4, width = 4)
ggsave(file = "Plots/ACE2_ACE2TMPRSS2_BtKY72_subpanel_scatterplot.png", ACE2_ACE2TMPRSS2_BtKY72_subpanel_scatterplot, height = 4, width = 4)
ACE2_ACE2TMPRSS2_BtKY72_subpanel_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20the%20BtKY72%20panel%20with%20ACE2%20and%20TMPRSS2-2.png)<!-- -->

``` r
ACE2_TMPRSS2_btky72_mut_plot <- ggplot() + 
 theme_bw() + theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) +
  scale_y_log10(limits = c(3e-1,2e3)) + 
  labs(x = element_blank(), y = "Ratio of mCherry to iRFP670 infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_quasirandom(data = two_color_ace2_tmprss2_dep2_btky72 %>% filter(virus_label %in% c("BtKY72 RBD", "BtKY72 RBD [Y488H]", "BtKY72 RBD [T499E]")), aes(x = virus_label, y = ace2_tmprss2_dep_infection), position = position_jitter(width = 0.1), alpha = 0.2, size = 1) +
  geom_errorbar(data = two_color_ace2_tmprss2_dep_summary_btky72 %>% filter(virus_label %in% c("BtKY72 RBD", "BtKY72 RBD [Y488H]", "BtKY72 RBD [T499E]")), aes(x = virus_label, ymin = lower_ci, ymax = upper_ci), alpha = 0.6, width = 0.4) +
  geom_point(data = two_color_ace2_tmprss2_dep_summary_btky72 %>% filter(virus_label %in% c("BtKY72 RBD", "BtKY72 RBD [Y488H]", "BtKY72 RBD [T499E]")), aes(x = virus_label, y = geomean), size = 12, shape = 95)
ACE2_TMPRSS2_btky72_mut_plot
```

![](ACE2_dependence_files/figure-gfm/Just%20the%20BtkY72%20variants-1.png)<!-- -->

``` r
ggsave(file = "Plots/ACE2_TMPRSS2_btky72_mut_plot.pdf", ACE2_TMPRSS2_btky72_mut_plot, height = 1.85, width = 1.3)
ggsave(file = "Plots/ACE2_TMPRSS2_btky72_mut_plot.png", ACE2_TMPRSS2_btky72_mut_plot, height = 1.85, width = 1.3)
```

``` r
ace2_parsed_df <- read.delim(file = "Data/Alignment/Bat_ACE2_aligned_identity_matrix_items.tsv", header = F, stringsAsFactors = F, sep = "\t")
ace2_dist_matrix <- read.delim(file = "Data/Alignment/Bat_ACE2_aligned_identity_matrix.csv", header = F, stringsAsFactors = F, sep = ",")

colnames(ace2_dist_matrix) <- ace2_parsed_df$V1 #paste("c_",ace2_parsed_df$V1,sep="")
rownames(ace2_dist_matrix) <- ace2_parsed_df$V1 #paste("r_",ace2_parsed_df$V1,sep="")

ace2_dist_matrix_hclust <- hclust(as.dist(ace2_dist_matrix, diag = TRUE))

ace2_dist_matrix2 <- ace2_dist_matrix
ace2_dist_matrix2$species <- rownames(ace2_dist_matrix2)

ace2_dist_melted <- melt(ace2_dist_matrix2, id = "species")
ace2_dist_melted$variable <- as.character(ace2_dist_melted$variable)

ace2_dist_melted$species <- factor(ace2_dist_melted$species, levels = ace2_dist_matrix_hclust$labels)
ace2_dist_melted$variable <- factor(ace2_dist_melted$variable, levels = ace2_dist_matrix_hclust$labels)

ACE2_identity_matrix_plot <- ggplot() + theme_bw() +
  theme(axis.text = element_text(size = 8), axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) +
  labs(x = NULL, y = NULL, fill = NULL) +
  scale_fill_continuous(low = "white", high = "black") +
  geom_tile(data = ace2_dist_melted, aes(x = species, y = variable, fill = value)) +
  geom_text(data = ace2_dist_melted %>% filter(variable != "H.sapiens" & value <= 40), aes(x = species, y = variable, label = value), size = 2) +
  geom_text(data = ace2_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value >= 40), aes(x = species, y = variable, label = value), size = 2, color = "grey90") +
  geom_text(data = ace2_dist_melted %>% filter(species == "H.sapiens" & value >= 40), aes(x = species, y = variable, label = value), size = 1.5, color = "grey90") +   geom_text(data = ace2_dist_melted %>% filter(variable == "H.sapiens" & value >= 40), aes(x = species, y = variable, label = value), size = 1.5, color = "grey90") +
  NULL
ggsave(file = "Plots/ACE2_identity_matrix_plot.pdf", ACE2_identity_matrix_plot, height = 2.3, width = 3.2)
ACE2_identity_matrix_plot
```

![](ACE2_dependence_files/figure-gfm/Making%20the%20identity%20matrix%20of%20the%20ACE2%20orthologs%20we%20were%20able%20to%20make-1.png)<!-- -->

``` r
ace2_length <- nchar(ace2_parsed_df$V2[1])
ace2_allele_num <- nrow(ace2_parsed_df)

amino_acid_matrix = matrix(nrow = ace2_length, ncol = ace2_allele_num)

for(x in 1:ace2_length){
  for(y in 1:ace2_allele_num){
    amino_acid_matrix[x,y] <- substr(ace2_parsed_df$V2[y],x,x)
  }
}

df_amino_acid_matrix <- data.frame(amino_acid_matrix)
colnames(df_amino_acid_matrix) <- ace2_parsed_df$V1

df_amino_acid_matrix$unique_residue <- "X"

for(x in 1:nrow(df_amino_acid_matrix)){df_amino_acid_matrix$unique_residue[x] <- gsub("[^A-Z]","",toString(unique(unlist(df_amino_acid_matrix[x,2:9]))))}
df_amino_acid_matrix$amino_acids <- nchar(df_amino_acid_matrix$unique_residue)
df_amino_acid_matrix$differences <- nchar(df_amino_acid_matrix$unique_residue) -1
df_amino_acid_matrix$position <- as.numeric(rownames(df_amino_acid_matrix))

Ace2_differences_linear_seq_plot <- ggplot() + theme_bw() + theme(panel.grid.minor.y = element_blank()) + 
  scale_x_continuous(expand = c(0,0)) + scale_y_continuous(breaks = c(1,2,3), limits = c(0,4), expand = c(0,0)) +
  labs(x = "Position along ACE2", y = "Number of\ndifferences") +
  geom_point(data = df_amino_acid_matrix %>% filter(differences >= 1), aes(x = position, y = differences), alpha = 0.4, size = 2) +
  geom_segment(aes(x = 1, xend = 595, y = 0, yend = 0), size = 3) +
  geom_segment(aes(x = 596, xend = 804, y = 0, yend = 0), size = 3, color = "red")
ggsave(file = "Plots/Ace2_differences_linear_seq_plot.pdf", Ace2_differences_linear_seq_plot, height = 1, width = 1.75)
Ace2_differences_linear_seq_plot
```

![](ACE2_dependence_files/figure-gfm/See%20which%20parts%20of%20the%20ACE2%20linear%20sequence%20is%20more%20diverse-1.png)<!-- -->

``` r
subset(df_amino_acid_matrix, amino_acids >= 4)
```

    ##     H.sapiens R.ferrumequinum R.alcyone R.landeri R.sinicus_472 R.sinicus_215
    ## 24          Q               L         L         L             E             R
    ## 31          K               D         N         D             K             E
    ## 34          H               S         S         S             T             S
    ## 568         L               S         S         S             E             K
    ## 667         E               E         E         E             A             A
    ##     R.sinicus_200 R.affinis R.pearsonii unique_residue amino_acids differences
    ## 24              L         R           Q           LERQ           4           3
    ## 31              E         N           K           DNKE           4           3
    ## 34              F         R           R           STFR           4           3
    ## 568             K         V           V           SEKV           4           3
    ## 667             A         V           D           EAVD           4           3
    ##     position
    ## 24        24
    ## 31        31
    ## 34        34
    ## 568      568
    ## 667      667

``` r
subset(df_amino_acid_matrix, amino_acids >= 3 & position < 400)
```

    ##     H.sapiens R.ferrumequinum R.alcyone R.landeri R.sinicus_472 R.sinicus_215
    ## 24          Q               L         L         L             E             R
    ## 27          T               K         I         T             I             T
    ## 31          K               D         N         D             K             E
    ## 34          H               S         S         S             T             S
    ## 35          E               E         E         A             K             E
    ## 38          D               N         N         N             D             N
    ## 75          E               K         T         T             E             E
    ## 91          L               D         D         D             V             V
    ## 215         Y               L         L         L             P             P
    ## 223         I               I         T         T             M             M
    ## 301         A               N         T         T             G             G
    ## 305         Q               K         K         K             D             D
    ##     R.sinicus_200 R.affinis R.pearsonii unique_residue amino_acids differences
    ## 24              L         R           Q           LERQ           4           3
    ## 27              I         I           I            KIT           3           2
    ## 31              E         N           K           DNKE           4           3
    ## 34              F         R           R           STFR           4           3
    ## 35              E         E           E            EAK           3           2
    ## 38              N         E           D            NDE           3           2
    ## 75              E         E           E            KTE           3           2
    ## 91              V         V           S            DVS           3           2
    ## 215             P         S           P            LPS           3           2
    ## 223             M         M           M            ITM           3           2
    ## 301             G         G           G            NTG           3           2
    ## 305             D         N           N            KDN           3           2
    ##     position
    ## 24        24
    ## 27        27
    ## 31        31
    ## 34        34
    ## 35        35
    ## 38        38
    ## 75        75
    ## 91        91
    ## 215      215
    ## 223      223
    ## 301      301
    ## 305      305

``` r
## Figure out which positions differ between alcyone and landeri
alcyone_landeri_frame <- df_amino_acid_matrix[,c("R.alcyone","R.landeri")]
for(x in 1:nrow(alcyone_landeri_frame)){alcyone_landeri_frame$unique_residue[x] <- gsub("[^A-Z]","",toString(unique(unlist(alcyone_landeri_frame[x,1:2]))))}
alcyone_landeri_frame$amino_acids <- nchar(alcyone_landeri_frame$unique_residue)
alcyone_landeri_frame$differences <- nchar(alcyone_landeri_frame$unique_residue) -1
alcyone_landeri_frame$position <- as.numeric(rownames(alcyone_landeri_frame))

alcyone_landeri_frame_diff <- alcyone_landeri_frame %>% filter(differences > 0)
alcyone_landeri_frame_diff
```

    ##    R.alcyone R.landeri unique_residue amino_acids differences position
    ## 1          A         T             AT           2           1       15
    ## 2          I         T             IT           2           1       27
    ## 3          N         D             ND           2           1       31
    ## 4          E         A             EA           2           1       35
    ## 5          H         Y             HY           2           1       41
    ## 6          T         A             TA           2           1      246
    ## 7          A         G             AG           2           1      286
    ## 8          Y         H             YH           2           1      613
    ## 9          L         S             LS           2           1      656
    ## 10         N         D             ND           2           1      720

``` r
paste("select alcyone_diffs, modeller_alcyone and resi",gsub(", ","+",toString(unlist(alcyone_landeri_frame_diff$position))))
```

    ## [1] "select alcyone_diffs, modeller_alcyone and resi 15+27+31+35+41+246+286+613+656+720"

``` r
ace2_tested_parsed_df <- read.delim(file = "Data/Alignment/Bat_tested_ACE2_aligned_identity_matrix_items.tsv", header = F, stringsAsFactors = F, sep = "\t")
ace2_tested_dist_matrix <- read.delim(file = "Data/Alignment/Bat_tested_ACE2_aligned_identity_matrix.csv", header = F, stringsAsFactors = F, sep = ",")

colnames(ace2_tested_dist_matrix) <- ace2_tested_parsed_df$V1 #paste("c_",ace2_tested_parsed_df$V1,sep="")
rownames(ace2_tested_dist_matrix) <- ace2_tested_parsed_df$V1 #paste("r_",ace2_tested_parsed_df$V1,sep="")

ace2_tested_dist_matrix_hclust <- hclust(as.dist(ace2_tested_dist_matrix, diag = TRUE))

ace2_tested_dist_matrix2 <- ace2_tested_dist_matrix
ace2_tested_dist_matrix2$species <- rownames(ace2_tested_dist_matrix2)

ace2_tested_dist_melted <- melt(ace2_tested_dist_matrix2, id = "species")
ace2_tested_dist_melted$variable <- as.character(ace2_tested_dist_melted$variable)

ace2_tested_dist_melted$species <- factor(ace2_tested_dist_melted$species, levels = ace2_tested_dist_matrix_hclust$labels)
ace2_tested_dist_melted$variable <- factor(ace2_tested_dist_melted$variable, levels = ace2_tested_dist_matrix_hclust$labels)

ACE2_tested_identity_matrix_plot <- ggplot() + theme_bw() +
  theme(axis.text = element_text(size = 8), axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) +
  labs(x = NULL, y = NULL, fill = NULL) +
  scale_fill_continuous(low = "white", high = "black") +
  geom_tile(data = ace2_tested_dist_melted, aes(x = species, y = variable, fill = value)) +
  geom_text(data = ace2_tested_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens"), aes(x = species, y = variable, label = value)) +
  NULL
ggsave(file = "Plots/ACE2_tested_identity_matrix_plot.pdf", ACE2_tested_identity_matrix_plot, height = 2.3*2, width = 2.8*2)
ACE2_tested_identity_matrix_plot
```

![](ACE2_dependence_files/figure-gfm/Of%20the%20ones%20we%20were%20able%20to%20make%20now%20looking%20at%20the%20actual%20sequences%20we%20tested-1.png)<!-- -->

``` r
all_ace2_parsed_df <- read.delim(file = "Data/Alignment/211020_All_ACE2/All_Bat_ACE2_aligned_identity_matrix_items.tsv", header = F, stringsAsFactors = F, sep = "\t")
all_ace2_dist_matrix <- read.delim(file = "Data/Alignment/211020_All_ACE2/All_Bat_ACE2_aligned_identity_matrix.csv", header = F, stringsAsFactors = F, sep = ",")

colnames(all_ace2_dist_matrix) <- all_ace2_parsed_df$V1 #paste("c_",all_ace2_parsed_df$V1,sep="")
rownames(all_ace2_dist_matrix) <- all_ace2_parsed_df$V1 #paste("r_",all_ace2_parsed_df$V1,sep="")

all_ace2_dist_matrix_hclust <- hclust(as.dist(all_ace2_dist_matrix, diag = TRUE))

all_ace2_dist_matrix2 <- all_ace2_dist_matrix
all_ace2_dist_matrix2$species <- rownames(all_ace2_dist_matrix2)

all_ace2_dist_melted <- melt(all_ace2_dist_matrix2, id = "species")
all_ace2_dist_melted$variable <- as.character(all_ace2_dist_melted$variable)

all_ace2_dist_melted$species <- factor(all_ace2_dist_melted$species, levels = all_ace2_dist_matrix_hclust$labels)
all_ace2_dist_melted$variable <- factor(all_ace2_dist_melted$variable, levels = all_ace2_dist_matrix_hclust$labels)

all_ace2_identity_matrix_plot <- ggplot() + theme_bw() +
  theme(axis.text = element_text(size = 8), axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) +
  labs(x = NULL, y = NULL, fill = NULL) +
  scale_fill_continuous(low = "white", high = "black") +
  geom_tile(data = all_ace2_dist_melted, aes(x = species, y = variable, fill = value)) +
  geom_text(data = all_ace2_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value <= 80), aes(x = species, y = variable, label = value), size = 2) +
  geom_text(data = all_ace2_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value >= 80), aes(x = species, y = variable, label = value), size = 2, color = "grey70") +
  NULL
ggsave(file = "Plots/all_ace2_identity_matrix_plot.pdf", all_ace2_identity_matrix_plot, height = 6, width = 7)
all_ace2_identity_matrix_plot
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20all%20of%20the%20bat%20ACE2s%20in%20NCBI-1.png)<!-- -->

``` r
all_ace2_identity_matrix_plot <- ggplot() + theme_bw() +
  theme(axis.text = element_text(size = 8), axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) +
  labs(x = NULL, y = NULL, fill = NULL) +
  scale_fill_continuous(low = "white", high = "black") +
  geom_tile(data = all_ace2_dist_melted, aes(x = species, y = variable, fill = value)) +
  #geom_text(data = all_ace2_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value <= 80), aes(x = species, y = variable, label = value), size = 2) +
  #geom_text(data = all_ace2_dist_melted %>% filter(species != "H.sapiens" & variable != "H.sapiens" & value >= 80), aes(x = species, y = variable, label = value), size = 2, color = "grey70") +
  NULL
ggsave(file = "Plots/all_ace2_identity_matrix_plot_no_numbers_for_presentation.pdf", all_ace2_identity_matrix_plot, height = 6, width = 7)
#all_ace2_identity_matrix_plot
```

## See if I can plot where the most changes in sequence are

``` r
ace2_length <- nchar(all_ace2_parsed_df$V2[1])
ace2_allele_num <- nrow(all_ace2_parsed_df)

amino_acid_matrix = matrix(nrow = ace2_length, ncol = ace2_allele_num)

for(x in 1:ace2_length){
  for(y in 1:ace2_allele_num){
    amino_acid_matrix[x,y] <- substr(all_ace2_parsed_df$V2[y],x,x)
  }
}

df_amino_acid_matrix <- data.frame(amino_acid_matrix)
colnames(df_amino_acid_matrix) <- all_ace2_parsed_df$V1

df_amino_acid_matrix$unique_residue <- "X"

for(x in 1:nrow(df_amino_acid_matrix)){df_amino_acid_matrix$unique_residue[x] <- gsub("[^A-Z]","",toString(unique(unlist(df_amino_acid_matrix[x,2:38]))))}
df_amino_acid_matrix$amino_acids <- nchar(df_amino_acid_matrix$unique_residue)
df_amino_acid_matrix$differences <- nchar(df_amino_acid_matrix$unique_residue) -1
df_amino_acid_matrix$position <- as.numeric(rownames(df_amino_acid_matrix))

annot_line_1_height = -3
annot_line_2_height = -5

Ace2_differences_linear_seq_plot <- ggplot() + theme_bw() + theme(panel.grid.minor.y = element_blank()) + 
  scale_x_continuous(expand = c(0,0)) + scale_y_continuous(breaks = seq(0,6,2), limits = c(-6,6), expand = c(0,0)) +
  labs(x = "Position along ACE2", y = "Number of\ndifferences") +
  geom_vline(xintercept = c(31,37,41,353,355,357), alpha = 0.2, color = "red") + 
  geom_hline(yintercept = 0) +
  geom_point(data = df_amino_acid_matrix %>% filter(differences >= 1), aes(x = position, y = differences), alpha = 0.2, size = 1) +
  geom_segment(aes(x = 1, xend = 595, y = annot_line_1_height, yend = annot_line_1_height), size = 3, color = "tan4") +
  geom_segment(aes(x = 596, xend = 804, y = annot_line_1_height, yend = annot_line_1_height), size = 3, color = "#FB4F14") +
  geom_segment(aes(x = 1, xend = 740, y = annot_line_2_height, yend = annot_line_2_height), size = 3, color = "red") +
  geom_segment(aes(x = 741, xend = 761, y = annot_line_2_height, yend = annot_line_2_height), size = 3, color = "green") +
  geom_segment(aes(x = 761, xend = 804, y = annot_line_2_height, yend = annot_line_2_height), size = 3, color = "blue")
Ace2_differences_linear_seq_plot
```

![](ACE2_dependence_files/figure-gfm/Figuring%20out%20the%20most%20variable%20positions%20in%20rhinolophid%20ACE2-1.png)<!-- -->

``` r
ggsave(file = "Plots/Ace2_differences_linear_seq_plot.pdf", Ace2_differences_linear_seq_plot, height = 1.5, width = 2.25)
ggsave(file = "Plots/Ace2_differences_linear_seq_plot_for_presentation.pdf", Ace2_differences_linear_seq_plot, height = 2, width = 5)


paste("select ace2_most_variants, ace2 and resi",gsub(", ","+",toString(subset(df_amino_acid_matrix, differences >= 4)$position)))
```

    ## [1] "select ace2_most_variants, ace2 and resi 24+27+31+34"

``` r
five_changed_positions <- df_amino_acid_matrix %>% filter(differences == 5)
paste("select five_differences, ace2 and resi",gsub(", ","+",toString(unlist(five_changed_positions$position))))
```

    ## [1] "select five_differences, ace2 and resi 34"

``` r
paste("color forest, five_differences")
```

    ## [1] "color forest, five_differences"

``` r
four_changed_positions <- df_amino_acid_matrix %>% filter(differences == 4)
paste("select four_differences, ace2 and resi",gsub(", ","+",toString(unlist(four_changed_positions$position))))
```

    ## [1] "select four_differences, ace2 and resi 24+27+31"

``` r
paste("color orange, four_differences")
```

    ## [1] "color orange, four_differences"

``` r
three_changed_positions <- df_amino_acid_matrix %>% filter(differences == 3)
paste("select three_differences, ace2 and resi",gsub(", ","+",toString(unlist(three_changed_positions$position))))
```

    ## [1] "select three_differences, ace2 and resi 429+568+667+771"

``` r
paste("color yellow, three_differences")
```

    ## [1] "color yellow, three_differences"

``` r
## Figure out which positions differ between alcyone and landeri

alcyone_landeri_frame <- df_amino_acid_matrix[,c("R.alcyone","R.landeri")]
for(x in 1:nrow(alcyone_landeri_frame)){alcyone_landeri_frame$unique_residue[x] <- gsub("[^A-Z]","",toString(unique(unlist(alcyone_landeri_frame[x,1:2]))))}
alcyone_landeri_frame$amino_acids <- nchar(alcyone_landeri_frame$unique_residue)
alcyone_landeri_frame$differences <- nchar(alcyone_landeri_frame$unique_residue) -1
alcyone_landeri_frame$position <- as.numeric(rownames(alcyone_landeri_frame))

alcyone_landeri_frame_diff <- alcyone_landeri_frame %>% filter(differences > 0)
alcyone_landeri_frame_diff
```

    ##    R.alcyone R.landeri unique_residue amino_acids differences position
    ## 1          A         T             AT           2           1       15
    ## 2          I         T             IT           2           1       27
    ## 3          N         D             ND           2           1       31
    ## 4          E         A             EA           2           1       35
    ## 5          H         Y             HY           2           1       41
    ## 6          T         A             TA           2           1      246
    ## 7          A         G             AG           2           1      286
    ## 8          Y         H             YH           2           1      613
    ## 9          L         S             LS           2           1      656
    ## 10         N         D             ND           2           1      720

``` r
paste("select alcyone_diffs, obj_human and resi",gsub(", ","+",toString(unlist(alcyone_landeri_frame_diff$position))))
```

    ## [1] "select alcyone_diffs, obj_human and resi 15+27+31+35+41+246+286+613+656+720"

For Pymol, this is the original view I was taking: set\_view (  
-0.749005258, 0.309185177, 0.585980117,  
0.508651137, -0.298377454, 0.807608724,  
0.424550295, 0.902970016, 0.066217214,  
-0.000023350, -0.004991800, -140.967224121,  
170.430801392, 103.793731689, 248.385269165,  
21.847066879, 256.336883545, -20.000000000 )

But perhaps it will be good to use this other view for looking at the
interaction surface set\_view (  
-0.721982539, -0.174140140, 0.669620097,  
0.527815580, -0.764368415, 0.370321423,  
0.447354764, 0.620808363, 0.643779159,  
0.000628673, -0.003673134, -141.278152466,  
168.149459839, 108.284217834, 245.709442139,  
21.847066879, 256.336883545, -20.000000000 )

``` r
rbd_label_levels2 <- c("VSV","YN2013 RBD", "Rs4237 RBD", "Rp3 RBD", "SARS-CoV-2","SARS-CoV-2 RBD", "SARS-CoV", "WIV1 RBD", "RhGB01 RBD", "BB9904 RBD", "BM48-31 RBD", "Khosta2 RBD", "Khosta1 RBD", "BtKY72 RBD")
bat_ace2_levels <- c("H.sapiens","NULL (fs)","R.ferrumequinum","R.alcyone","R.landeri","R.sinicus472","R.sinicus215","R.sinicus200","R.affinis","R.pearsonii")

bat_ace2s <- two_color_precombined %>% filter(expt == "Bat_ACE2s" & !(recombined_construct %in% c("G1080J/G758A"))) %>% filter(moi_gvn_red != 0) %>% filter(!(pseudovirus_env %in%c("SARS1_OLD","SARS2"))) #%>% filter(date %in% c("8/26/2021", "9/22/2021")) #two_color_precombined

bat_ace2s_2 <- merge(bat_ace2s, pseudovirus_label_key, by = "pseudovirus_env")
bat_ace2s_2 <- merge(bat_ace2s_2, recombined_construct_key, by = "recombined_construct")
bat_ace2s_2$log10_nir_red_diff <- log10(bat_ace2s_2$moi_gvn_nir) - log10(bat_ace2s_2$moi_gvn_red)
bat_ace2s_2$fold_ace2_dep_infection <- 10^bat_ace2s_2$log10_nir_red_diff
bat_ace2s_2 <- bat_ace2s_2 %>% filter(log10_nir_red_diff != "Inf" & log10_nir_red_diff != "-Inf")

bat_ace2s_2$virus_label <- factor(bat_ace2s_2$virus_label, levels = rbd_label_levels2)

bat_ace2s_2_summary <- bat_ace2s_2 %>% group_by(virus_label, cell_label) %>% summarize(mean_log10 = mean(log10_nir_red_diff, na.rm = T), sd_log10 = sd(log10_nir_red_diff, na.rm = T), .groups = "drop") %>% mutate(geomean = 10^mean_log10, upper_conf = 10^(mean_log10 + 1.96*sd_log10), lower_conf = 10^(mean_log10 - 1.96*sd_log10))

bat_ace2s_2$virus_label <- factor(bat_ace2s_2$virus_label, levels = rev(rbd_label_levels2))
bat_ace2s_2_summary$virus_label <- factor(bat_ace2s_2_summary$virus_label, levels = rev(rbd_label_levels2))


### Make the statistical test to see which proteins reproducibly increase infectivity
full_variant_t_test <- data.frame("cell_label" = rep(unique(bat_ace2s_2$cell_label),each = length(unique(bat_ace2s_2$virus_label))),
                                          "virus_label" =  rep(unique(bat_ace2s_2$virus_label),length(unique(bat_ace2s_2$cell_label))),
                                          "mean_ace2dep_infection" = NA,"p_value" = NA,"significant" = NA)

for(x in 1:nrow(full_variant_t_test)){
  temp_cell_label <- full_variant_t_test$cell_label[x]
  temp_pseudovirus_env <- full_variant_t_test$virus_label[x]
  temp_subset <- bat_ace2s_2 %>% filter(cell_label == temp_cell_label & virus_label == temp_pseudovirus_env)
  if(nrow(temp_subset) > 1){
    full_variant_t_test$mean_ace2dep_infection[x] <- mean(temp_subset$fold_ace2_dep_infection)
    temp_p_value <- round(t.test(temp_subset$fold_ace2_dep_infection,rep(1,nrow(temp_subset)), alternative = "two.sided")$p.value,4)
    full_variant_t_test$p_value[x] <- temp_p_value
  }
}
full_variant_t_test$corrected_p_value <- p.adjust(full_variant_t_test$p_value, method = 'BH')
full_variant_t_test[is.na(full_variant_t_test$corrected_p_value),"corrected_p_value"] <- 1
full_variant_t_test[full_variant_t_test$corrected_p_value < 0.05 & full_variant_t_test$mean_ace2dep_infection > 2,"significant"] <- "yes"

Faceted_bar_chart_flow <- 
ggplot() + theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0),
                 panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank()) + 
  labs(x = NULL, y = "Fold ACE2-dependent entry") +
  scale_y_log10(breaks = c(1,100)) + 
  geom_hline(yintercept = 1, alpha = 0.5) +
  geom_point(data = bat_ace2s_2_summary, aes(x = virus_label, y = geomean), shape = 95, size = 8) +
  geom_quasirandom(data = bat_ace2s_2, aes(x = virus_label, y = fold_ace2_dep_infection), alpha = 0.4) + 
  #geom_point(data = subset(bat_ace2s_2, fold_ace2_dep_infection > 10), aes(x = virus_label, y = fold_ace2_dep_infection), color = "red") +
  facet_grid(rows = vars(cell_label))
Faceted_bar_chart_flow
```

![](ACE2_dependence_files/figure-gfm/Matrix%20of%20bat%20ACE2%20ortholog%20cells%20infected%20by%20various%20SARS-like%20CoV%20RBDs%20using%20flow%20cytometry-1.png)<!-- -->

``` r
ggsave(file = "Plots/Faceted_bar_chart_flow.pdf", Faceted_bar_chart_flow, height = 6, width = 4)

##### R.sinicus200 and SARS[Khosta1 RBD] combo making NaN so throw it out until I get more data
bat_ace2s_2_summary_for_plotting <- bat_ace2s_2_summary %>% filter(!(virus_label == "SARS[Khosta1 RBD]" & cell_label == "R.sinicus200"))
bat_ace2s_2_summary_for_plotting[bat_ace2s_2_summary_for_plotting$geomean >= 100,"geomean"] <- 100
bat_ace2s_2_summary_for_plotting$virus_label <- factor(bat_ace2s_2_summary_for_plotting$virus_label, levels = rev(rbd_label_levels2))
bat_ace2s_2_summary_for_plotting$cell_label <- factor(bat_ace2s_2_summary_for_plotting$cell_label, levels = bat_ace2_levels)


my_breaks <- c("1,10,100")
host_virus_paired <- read.csv(file = "Data/Keys/host_virus_pairs_for_sequenced_sample.csv", header = T, stringsAsFactors = F)

Bat_ACE2_heatmap <- ggplot() + theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) + 
  labs(x = NULL, y = NULL, fill = "Fold") +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0.3,  na.value = "grey50", trans = "log10", limits = c(0.1,100)) + 
  geom_tile(data = bat_ace2s_2_summary_for_plotting, aes(x = cell_label, y = virus_label, fill = geomean)) +
  geom_text(data = bat_ace2s_2_summary_for_plotting, aes(x = cell_label, y = virus_label, label = round(geomean,1)), size = 1.8) +
  geom_tile(data = host_virus_paired, aes(x = cell_label, y = virus_label), color = "black", fill = NA, size = 0.25) +
  NULL
Bat_ACE2_heatmap
```

![](ACE2_dependence_files/figure-gfm/Matrix%20of%20bat%20ACE2%20ortholog%20cells%20infected%20by%20various%20SARS-like%20CoV%20RBDs%20using%20flow%20cytometry-2.png)<!-- -->

``` r
ggsave(file = "Plots/Bat_ACE2_heatmap.pdf", Bat_ACE2_heatmap, height = 3.5, width = 4.67)
ggsave(file = "Plots/Bat_ACE2_heatmap.png", Bat_ACE2_heatmap, height = 3.5, width = 4.67)

## What values am I getting for Rp3 and YN2013 and Pearsonii
clade2_pearsonii <- bat_ace2s_2 %>% filter(cell_label == "R.pearsonii" & virus_label %in% c("SARS[YN2013 RBD]","SARS[Rp3 RBD]","SARS[Rs4237 RBD]"))
clade2_affinis <- bat_ace2s_2 %>% filter(cell_label == "R.affinis" & virus_label %in% c("SARS[YN2013 RBD]","SARS[Rp3 RBD]","SARS[Rs4237 RBD]"))
clade2_landeri <- bat_ace2s_2 %>% filter(cell_label == "R.landeri" & virus_label %in% c("SARS[YN2013 RBD]","SARS[Rp3 RBD]","SARS[Rs4237 RBD]"))
```

``` r
microscopy <- read.csv(file = "Data/Infection_microscopy_scores.csv", header = T, stringsAsFactors = F) %>% filter(!(label_envelope %in%c("SARS1_OLD","SARS2")))
microscopy2 <- merge(microscopy, recombined_construct_key[,c("recombined_construct","cell_label")], by = "recombined_construct")
microscopy3 <- merge(microscopy2, pseudovirus_label_key[,c("pseudovirus_env","virus_label","sarbecovirus_clade")], by = "pseudovirus_env")

rbd_levels <- rev(c("VSV","YN2013 RBD", "Rs4237 RBD", "Rp3 RBD", "SARS-CoV-2","SARS-CoV-2 RBD", "SARS-CoV","WIV1 RBD", "RhGB01 RBD", "BB9904 RBD", "BM48-31 RBD", "Khosta2 RBD", "Khosta1 RBD", "BtKY72 RBD"))
bat_ace2_levels <- c("H.sapiens","NULL (fs)","R.ferrumequinum","R.alcyone","R.landeri","R.sinicus472","R.sinicus215","R.sinicus200","R.affinis","R.pearsonii")

microscopy_batace2_summary <- microscopy3 %>% filter(expt == "Bat_ACE2s") %>% group_by(cell_label, virus_label) %>% summarize(ratio = mean(nir_mcherry_overlap_ratio), .groups = "drop")

microscopy_batace2_summary$cell_label <- factor(microscopy_batace2_summary$cell_label, levels = bat_ace2_levels)
microscopy_batace2_summary$virus_label <- factor(microscopy_batace2_summary$virus_label, levels = (rbd_levels))

microscopy3_batace2 <- microscopy3 %>% filter(expt == "Bat_ACE2s")

Faceted_bar_chart_microscopy <- 
ggplot() + theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0),
                 panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank()) + 
  labs(x = NULL, y = "Fold ACE2-dependent entry") +
  scale_y_log10(breaks = c(1,10)) + 
  geom_hline(yintercept = 1, alpha = 0.5) +
  geom_point(data = microscopy_batace2_summary, aes(x = virus_label, y = ratio), shape = 95, size = 8) +
  geom_quasirandom(data = microscopy3_batace2, aes(x = virus_label, y = nir_mcherry_overlap_ratio), alpha = 0.4) + 
  #geom_point(data = subset(microscopy3_batace2, fold_ace2_dep_infection > 10), aes(x = virus_label, y = fold_ace2_dep_infection), color = "red") +
  facet_grid(rows = vars(cell_label))
Faceted_bar_chart_microscopy
```

![](ACE2_dependence_files/figure-gfm/Matrix%20of%20bat%20ACE2%20ortholog%20cells%20infected%20by%20various%20SARS-like%20CoV%20RBDs%20using%20microscopy-1.png)<!-- -->

``` r
ggsave(file = "Plots/Faceted_bar_chart_microscopy.pdf", Faceted_bar_chart_microscopy, height = 6, width = 4)

Microscopy_heatmap <- ggplot() + theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) + 
  labs(x = NULL, y = NULL, fill = "Fold") +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0.1,  na.value = "grey50", trans = "log10", limits = c(0.5,10)) + 
  geom_tile(data = microscopy_batace2_summary, aes(x = cell_label, y = virus_label, fill = ratio)) +
  geom_text(data = microscopy_batace2_summary, aes(x = cell_label, y = virus_label, label = round(ratio,1)), size = 1.8) +
  geom_tile(data = host_virus_paired, aes(x = cell_label, y = virus_label), color = "black", fill = NA, size = 0.25) +
  NULL

ggsave(file = "Plots/Microscopy_heatmap.pdf", Microscopy_heatmap, height = 3.5, width = 4.5)
ggsave(file = "Plots/Microscopy_heatmap.png", Microscopy_heatmap, height = 3.5, width = 4.5)
Microscopy_heatmap
```

![](ACE2_dependence_files/figure-gfm/Matrix%20of%20bat%20ACE2%20ortholog%20cells%20infected%20by%20various%20SARS-like%20CoV%20RBDs%20using%20microscopy-2.png)<!-- -->

``` r
flow_summary <- bat_ace2s_2_summary_for_plotting %>% filter(cell_label != "NULL (fs)") %>% group_by(virus_label) %>% summarize(mean_flow = mean(geomean))
microscope_summary <- microscopy_batace2_summary %>% filter(cell_label != "NULL (fs)") %>% group_by(virus_label) %>% summarize(mean_micro = mean(ratio))

flow_micro_summary <- merge(flow_summary, microscope_summary, by = "virus_label")

grouped_by_virus_plot <- ggplot() + theme(panel.grid.minor = element_blank()) + 
  scale_x_log10(limits = c(0.4,30)) + scale_y_log10(limits = c(0.8,4.2)) + 
  labs(x = "Flow cytometry", y = "Microscopy") + 
  geom_text_repel(data = flow_micro_summary, aes(x = mean_flow, y = mean_micro, label = virus_label), color = "red", size = 2, segment.color = "orange", segment.alpha = 0.4) +
  geom_point(data = flow_micro_summary, aes(x = mean_flow, y = mean_micro), alpha = 0.5)
ggsave(file = "Plots/Grouped_by_virus_plot.pdf", grouped_by_virus_plot, height = 2, width = 2.75)

flow_summary2 <- bat_ace2s_2_summary_for_plotting %>% filter(cell_label != "NULL (fs)" & virus_label != "VSV") %>% group_by(cell_label) %>% summarize(mean_flow = mean(geomean))
microscope_summary2 <- microscopy_batace2_summary %>% filter(cell_label != "NULL (fs)" & virus_label != "VSV") %>% group_by(cell_label) %>% summarize(mean_micro = mean(ratio))

flow_micro_summary2 <- merge(flow_summary2, microscope_summary2, by = "cell_label")

grouped_by_cell_plot <- ggplot() + theme(panel.grid.minor = element_blank()) + 
  scale_x_log10(limits = c(0.4,30)) + scale_y_log10(limits = c(0.8,4.2)) + 
  labs(x = "Flow cytometry", y = "Microscopy") + 
  geom_text_repel(data = flow_micro_summary2, aes(x = mean_flow, y = mean_micro, label = cell_label), color = "red", size = 2, segment.color = "orange", segment.alpha = 0.4) +
  geom_point(data = flow_micro_summary2, aes(x = mean_flow, y = mean_micro), alpha = 0.5)
ggsave(file = "Plots/Grouped_by_cell_plot.pdf", grouped_by_cell_plot, height = 2, width = 2.75)
```

``` r
flow_vs_microscopy <- merge(bat_ace2s_2_summary_for_plotting[,c("virus_label","cell_label","geomean")], microscopy_batace2_summary, by = c("virus_label","cell_label"))

ggplot() + 
  scale_x_log10(limits = c(0.3,100)) + scale_y_log10(limits = c(0.8,10)) + 
  scale_shape_manual(values = c(21, 22, 23, 24, 25, 3, 4, 7, 8, 13)) +
  geom_hline(yintercept = 1, alpha = 0.4) + geom_vline(xintercept = 1, alpha = 0.4) +
  geom_point(data = flow_vs_microscopy, aes(x = geomean, y = ratio, color = virus_label, shape = cell_label))
```

![](ACE2_dependence_files/figure-gfm/Directly%20compare%20the%20microscopy%20and%20flow%20data%20for%20the%20Bat%20ACE2%20orthologs%20and-1.png)<!-- -->

``` r
flow_micro_clade1 <- flow_vs_microscopy %>% filter(virus_label %in% c("VSV", "WIV1 RBD", "SARS-CoV-2 RBD"))
Clade1_scatterplot <- ggplot() + theme(panel.grid.minor = element_blank(), legend.position = "top") + 
  labs(x = "Fold ACE2-dependent infection (Flow)", y = "Fold ACE2-dependent infection (Image)") +
  scale_x_log10(limits = c(0.3,100), expand = c(0,0)) + scale_y_log10(limits = c(0.8,13), expand = c(0,0)) + 
  scale_shape_manual(values = c(16, 8, 0, 1, 2, 9, 10, 12, 5, 6)) +
  geom_hline(yintercept = 1, alpha = 0.4) + geom_vline(xintercept = 1, alpha = 0.4) +
  geom_point(data = flow_micro_clade1, aes(x = geomean, y = ratio, color = virus_label, shape = cell_label), alpha = 0.5)
ggsave("Plots/Clade1_scatterplot.pdf", Clade1_scatterplot, height = 2.1, width = 2.7)
Clade1_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Directly%20compare%20the%20microscopy%20and%20flow%20data%20for%20the%20Bat%20ACE2%20orthologs%20and-2.png)<!-- -->

``` r
flow_micro_clade2 <- flow_vs_microscopy %>% filter(virus_label %in% c("YN2013 RBD", "Rs4237 RBD", "Rp3 RBD"))
Clade2_scatterplot <- ggplot() + theme(panel.grid.minor = element_blank(), legend.position = "top") + 
  labs(x = "Fold ACE2-dependent infection (Flow)", y = "Fold ACE2-dependent infection (Image)") +
  scale_x_log10(limits = c(0.3,100), expand = c(0,0)) + scale_y_log10(limits = c(0.8,13), expand = c(0,0)) + 
  scale_shape_manual(values = c(16, 8, 0, 1, 2, 9, 10, 12, 5, 6)) +
  geom_hline(yintercept = 1, alpha = 0.4) + geom_vline(xintercept = 1, alpha = 0.4) +
  geom_point(data = flow_micro_clade2, aes(x = geomean, y = ratio, color = virus_label, shape = cell_label), alpha = 0.5)
ggsave("Plots/Clade2_scatterplot.pdf", Clade2_scatterplot, height = 2.1, width = 2.7)
Clade2_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Directly%20compare%20the%20microscopy%20and%20flow%20data%20for%20the%20Bat%20ACE2%20orthologs%20and-3.png)<!-- -->

``` r
flow_micro_clade3 <- flow_vs_microscopy %>% filter(virus_label %in% c("RhGB01 RBD", "BB9904 RBD", "BM48-31 RBD", "Khosta2 RBD", "Khosta1 RBD", "BtKY72 RBD"))
Clade3_scatterplot <- ggplot() + theme(panel.grid.minor = element_blank(), legend.position = "top") + 
  labs(x = "Fold ACE2-dependent infection (Flow)", y = "Fold ACE2-dependent infection (Image)") +
  scale_x_log10(limits = c(0.3,100), expand = c(0,0)) + scale_y_log10(limits = c(0.8,13), expand = c(0,0)) + 
  scale_shape_manual(values = c(16, 8, 0, 1, 2, 9, 10, 12, 5, 6)) +
  geom_hline(yintercept = 1, alpha = 0.4) + geom_vline(xintercept = 1, alpha = 0.4) +
  geom_point(data = flow_micro_clade3, aes(x = geomean, y = ratio, color = virus_label, shape = cell_label))
ggsave("Plots/Clade3_scatterplot.pdf", Clade3_scatterplot, height = 2.1, width = 2.7)
Clade3_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Directly%20compare%20the%20microscopy%20and%20flow%20data%20for%20the%20Bat%20ACE2%20orthologs%20and-4.png)<!-- -->

``` r
ace2_muts <- two_color_combined %>% filter(expt == "Btky72_ACE2muts" & !(recombined_construct == "Q42R"))# | pseudovirus_env == "G778B" 

ace2_muts$index <- seq(1,nrow(ace2_muts))
ace2_muts$log10_nir_red_diff <- log10(ace2_muts$moi_gvn_red) - log10(ace2_muts$moi_gvn_nir)

ace2_muts2 <- ace2_muts %>% group_by(date, virus_label, recombined_construct) %>% 
  summarize(log10_nir_red_diff = mean(log10_nir_red_diff), pct_grn_gvn_nir = mean(pct_grn_gvn_nir), ratio_nir_mcherry = mean(ratio_nir_mcherry), .groups = "drop") %>% mutate(n = 1, geomean = 10^log10_nir_red_diff)

two_color_ace2_muts_summary <- ace2_muts2 %>% group_by(virus_label, recombined_construct) %>% 
  summarize(mean_log10_nir_red_diff = mean(log10_nir_red_diff), sd_log10_nir_red_diff = sd(log10_nir_red_diff), n = sum(n), .groups = "drop") %>%
  mutate(se_log10_nir_red_diff = sd_log10_nir_red_diff / sqrt(n), geomean = 10^mean_log10_nir_red_diff, lower_ci = 10^(mean_log10_nir_red_diff - se_log10_nir_red_diff * 1.96), upper_ci = 10^(mean_log10_nir_red_diff + se_log10_nir_red_diff * 1.96), cells = "ACE2")

ace2_variant_levels <- c("WT","I21N","T27A","K31D","E37K","Q38H","Y41A","K353D","D355N","R357A","R357T")
ace2_muts2$recombined_construct <- factor(ace2_muts2$recombined_construct, levels = ace2_variant_levels)
two_color_ace2_muts_summary$recombined_construct <- factor(two_color_ace2_muts_summary$recombined_construct, levels = ace2_variant_levels)

## Set up consistent colors
virus_colors2 <- c("VSV" = "red", "SARS-CoV" = "darkgreen", "SARS-CoV-2" = "blue", "SARS-CoV-2 RBD" = "blue", "BtKY72 RBD" = "purple", "Khosta2 RBD" = "cyan", "WIV1 RBD" = "green")
##

Two_color_ACE2_muts_panel_plot <- ggplot() + 
  theme_bw() + theme(panel.grid.major.x = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) +
  scale_color_manual(values = virus_colors2) +
  scale_y_log10(limits = c(3e-1,1e1), expand = c(0,0)) + 
  labs(x = element_blank(), y = "Ratio of iRFP670 to\nmCherry infected cells") +
  geom_hline(yintercept = 1, linetype = 2, alpha = 0.4) +
  geom_point(data = ace2_muts2, aes(x = recombined_construct, y = geomean, color = virus_label), position = position_dodge(width = 0.8), alpha = 0.4) +
  geom_errorbar(data = two_color_ace2_muts_summary, aes(x = recombined_construct, ymin = lower_ci, ymax = upper_ci, color = virus_label), position = position_dodge(width = 0.8), alpha = 0.4, width = 0.2) +
  geom_point(data = two_color_ace2_muts_summary, aes(x = recombined_construct, y = geomean, color = virus_label), position = position_dodge(width = 0.8), size = 8, shape = 95) +
  facet_grid(rows = vars(virus_label))
Two_color_ACE2_muts_panel_plot
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20human%20ACE2%20variant%20dependences%20of%20BtKY72%20vs%20the%20others,%20in%20the%20low%20ACE2%20context%20we%20previously%20tested-1.png)<!-- -->

``` r
ggsave(file = "Plots/Two_color_ACE2_muts_panel_plot.pdf", Two_color_ACE2_muts_panel_plot, height = 2.5, width = 4.5)
ggsave(file = "Plots/Two_color_ACE2_muts_panel_plot.png", Two_color_ACE2_muts_panel_plot, height = 2.5, width = 4.5)

### Hmmm, BtKY72 didn't do much here. Probably since this is all suboptimal Kozak ACE2 cells, which isn't enough to allow BtKY72 infection.
```

``` r
original_mutant_data <- read.delim(file = "Data/Shukla_supplementary_table_2.tsv", sep = "\t", header = T) %>% filter(expt == "ACE2_mut_panel")
original_mutant_data2 <- merge(original_mutant_data, pseudovirus_label_key, by = "pseudovirus_env")

original_mutant_data_summary <<- original_mutant_data2 %>% group_by(cell_label, virus_label) %>% summarize(geomean = 10^mean(log_scaled_infection))
```

    ## `summarise()` has grouped output by 'cell_label'. You can override using the `.groups` argument.

``` r
original_mutant_data_summary$recombined_construct <- ""
original_mutant_data_summary$geomean.decto_scaled <- 0
cntrl_frame <- original_mutant_data_summary %>% filter(cell_label == "ACE2(dEcto)")

for(x in 1:nrow(original_mutant_data_summary)){
  temp_virus <- original_mutant_data_summary$virus_label[x]
  original_mutant_data_summary$recombined_construct[x] <- substr(original_mutant_data_summary$cell_label[x],11,20)
  original_mutant_data_summary$geomean.decto_scaled[x] <- original_mutant_data_summary$geomean[x] / cntrl_frame[cntrl_frame$virus_label == temp_virus,"geomean"]
}

singleplex_duplex_ace2_data <- merge(original_mutant_data_summary, two_color_ace2_muts_summary, by = c("recombined_construct","virus_label"))
singleplex_duplex_ace2_data$geomean.decto_scaled <- as.numeric(singleplex_duplex_ace2_data$geomean.decto_scaled)

singleplex_duplex_ace2_ace2_muts_plot <- ggplot() + theme(panel.grid.minor = element_blank()) + 
  labs(x = "Singleplex assay", y = "Duplex assay") +
  scale_color_manual(values = virus_colors2) +
  scale_x_log10() + scale_y_log10() + 
  geom_point(data = singleplex_duplex_ace2_data, aes(x = geomean.decto_scaled, y = geomean.y, color = virus_label), alpha = 0.5) +
  geom_text_repel(data = singleplex_duplex_ace2_data %>% filter(virus_label != "VSV"), aes(x = geomean.decto_scaled, y = geomean.y, label = recombined_construct), size = 2)
ggsave(file = "Plots/singleplex_duplex_ace2_ace2_muts_plot.pdf", singleplex_duplex_ace2_ace2_muts_plot, height = 2.5, width = 4)
ggsave(file = "Plots/singleplex_duplex_ace2_ace2_muts_plot.png", singleplex_duplex_ace2_ace2_muts_plot, height = 2.5, width = 4)

singleplex_duplex_ace2_ace2_muts_plot
```

![](ACE2_dependence_files/figure-gfm/Comparing%20the%20low%20ACE2%20singleplex%20and%20duplex%20readout%20results-1.png)<!-- -->

``` r
cor(singleplex_duplex_ace2_data$geomean.y, singleplex_duplex_ace2_data$geomean.decto_scaled, method = "pearson")
```

    ## [1] 0.9472555

``` r
flow_ace2_muts <- two_color_precombined %>% filter(expt %in% c("Clade3_hum_muts","ACE2_muts") & moi_gvn_red != 0)
flow_ace2_muts2 <- flow_ace2_muts
flow_ace2_muts3 <- merge(flow_ace2_muts2, recombined_construct_key[,c("recombined_construct","cell_label")], by = "recombined_construct")
flow_ace2_muts4 <- merge(flow_ace2_muts3, pseudovirus_label_key[,c("pseudovirus_env","virus_label","sarbecovirus_clade")], by = "pseudovirus_env")

flow_ace2_muts4$log10_nir_red_diff <- log10(flow_ace2_muts4$moi_gvn_nir) - log10(flow_ace2_muts4$moi_gvn_red)
flow_ace2_muts4$fold_ace2_dep_infection <- 10^flow_ace2_muts4$log10_nir_red_diff
flow_ace2_muts4 <- flow_ace2_muts4 %>% filter(log10_nir_red_diff != "Inf" & log10_nir_red_diff != "-Inf")

flow_ace2_muts4$cell_label <- factor(flow_ace2_muts4$cell_label, levels = c("H.sapiens", "K31D","Y41A","K353D","D355N","R357T"))
flow_ace2_muts4$virus_label <- factor(flow_ace2_muts4$virus_label, levels = c("VSV","SARS-CoV-2 RBD", "SARS-CoV", "WIV1 RBD", "Khosta2 RBD","BtKY72 RBD"))

flow_ace2_muts_summary <- flow_ace2_muts4 %>% group_by(cell_label, virus_label) %>% summarize(ratio = 10^mean(log10(fold_ace2_dep_infection)), .groups = "drop")

flow_ace2_muts_summary$cell_label <- factor(flow_ace2_muts_summary$cell_label, levels = c("H.sapiens", "K31D","Y41A","K353D","D355N","R357T"))
flow_ace2_muts_summary$virus_label <- factor(flow_ace2_muts_summary$virus_label, levels = rev(c("VSV","SARS-CoV-2 RBD", "SARS-CoV", "WIV1 RBD", "Khosta2 RBD","BtKY72 RBD")))

Flow_ace2muts_faceted <- ggplot() + theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) + 
  labs(x = NULL, y = "Fold ACE2-depednent infection") +
  scale_color_manual(values = virus_colors2) +
  scale_y_log10() + 
  geom_quasirandom(data = flow_ace2_muts4, aes(x = cell_label, y = fold_ace2_dep_infection, color = virus_label), alpha = 0.5) +
  geom_point(data= flow_ace2_muts_summary, aes(x = cell_label, y = ratio), shape = 95, size = 8) +
  facet_grid(rows = vars(virus_label))
Flow_ace2muts_faceted
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20human%20ACE2%20variant%20dependences%20of%20BtKY72%20and%20Khosta-2,%20in%20the%20high%20ACE2%20context%20using%20a%20flow%20cytometry%20readout-1.png)<!-- -->

``` r
ggsave(file = "Plots/Flow_ace2muts_faceted.pdf", Flow_ace2muts_faceted, height = 2.75, width = 3.8)
ggsave(file = "Plots/Flow_ace2muts_faceted.png", Flow_ace2muts_faceted, height = 2.75, width = 3.8)

Flow_ace2muts_heatmap <- ggplot() + theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) + 
  labs(x = NULL, y = NULL, fill = "Fold") +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0.1,  na.value = "grey50", trans = "log10") + 
  geom_tile(data = flow_ace2_muts_summary, aes(x = cell_label, y = virus_label, fill = ratio)) +
  geom_text(data = flow_ace2_muts_summary, aes(x = cell_label, y = virus_label, label = round(ratio,1)), size = 2) +
  NULL
ggsave(file = "Plots/Flow_ace2muts_heatmap.pdf", Flow_ace2muts_heatmap, height = 2, width = 3.5)
ggsave(file = "Plots/Flow_ace2muts_heatmap.png", Flow_ace2muts_heatmap, height = 2, width = 3.5)
Flow_ace2muts_heatmap
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20human%20ACE2%20variant%20dependences%20of%20BtKY72%20and%20Khosta-2,%20in%20the%20high%20ACE2%20context%20using%20a%20flow%20cytometry%20readout-2.png)<!-- -->

``` r
microscopy_ace2muts <- microscopy3 %>% filter(expt == "Human_ACE2_muts") 
microscopy_ace2muts_summary <- microscopy_ace2muts %>% group_by(cell_label, virus_label) %>% summarize(ratio = 10^mean(log10(nir_mcherry_overlap_ratio)), .groups = "drop")
microscopy_ace2muts_summary$cell_label <- factor(microscopy_ace2muts_summary$cell_label, levels = c("H.sapiens", "K31D","Y41A","K353D","D355N","R357T"))
microscopy_ace2muts_summary$virus_label <- factor(microscopy_ace2muts_summary$virus_label, levels = rev(c("VSV","SARS-CoV-2 RBD", "SARS-CoV", "WIV1 RBD", "Khosta2 RBD","BtKY72 RBD")))

Microscopy_ace2muts_heatmap <- ggplot() + theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5)) + 
  labs(x = NULL, y = NULL, fill = "Fold") +
  scale_fill_gradient2(low = "blue", mid = "white", high = "red", midpoint = 0.1,  na.value = "grey50", trans = "log10", limits = c(0.5,10)) + 
  geom_tile(data = microscopy_ace2muts_summary, aes(x = cell_label, y = virus_label, fill = ratio)) +
  geom_text(data = microscopy_ace2muts_summary, aes(x = cell_label, y = virus_label, label = round(ratio,1)), size = 1.8) +
  NULL
Microscopy_ace2muts_heatmap
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20human%20ACE2%20variant%20dependences%20of%20BtKY72%20and%20Khosta-2,%20in%20the%20high%20ACE2%20context%20using%20a%20microscopy%20readout-1.png)<!-- -->

``` r
ggsave(file = "Plots/Microscopy_ace2muts_heatmap.pdf", Microscopy_ace2muts_heatmap, height = 1.75, width = 3.25)
ggsave(file = "Plots/Microscopy_ace2muts_heatmap.png", Microscopy_ace2muts_heatmap, height = 1.75, width = 3.25)

microscopy_ace2muts$cell_label <- factor(microscopy_ace2muts$cell_label, levels = c("H.sapiens", "K31D","Y41A","K353D","D355N","R357T"))
microscopy_ace2muts$virus_label <- factor(microscopy_ace2muts$virus_label, levels = c("VSV","SARS-CoV-2 RBD", "SARS-CoV", "WIV1 RBD", "Khosta2 RBD","BtKY72 RBD"))

Microscopy_ace2muts_faceted <- ggplot() + theme(panel.grid.major.x = element_blank(), panel.grid.minor = element_blank(), axis.text.x = element_text(angle = 45, hjust = 1, vjust = 1)) + 
  labs(x = NULL, y = "Fold ACE2-depednent infection") +
  scale_color_manual(values = virus_colors2) +
  scale_y_log10() + 
  geom_quasirandom(data = microscopy_ace2muts, aes(x = cell_label, y = nir_mcherry_overlap_ratio, color = virus_label), alpha = 0.5) +
  geom_point(data= microscopy_ace2muts_summary, aes(x = cell_label, y = ratio), shape = 95, size = 8) +
  facet_grid(rows = vars(virus_label))
Microscopy_ace2muts_faceted
```

![](ACE2_dependence_files/figure-gfm/Looking%20at%20human%20ACE2%20variant%20dependences%20of%20BtKY72%20and%20Khosta-2,%20in%20the%20high%20ACE2%20context%20using%20a%20microscopy%20readout-2.png)<!-- -->

``` r
ggsave(file = "Plots/Microscopy_ace2muts_faceted.pdf", Microscopy_ace2muts_faceted, height = 2.75, width = 3.8)
ggsave(file = "Plots/Microscopy_ace2muts_faceted.png", Microscopy_ace2muts_faceted, height = 2.75, width = 3.8)
```

``` r
flow_vs_microscopy_ace2muts <- merge(flow_ace2_muts_summary[,c("virus_label","cell_label","ratio")], microscopy_ace2muts_summary, by = c("virus_label","cell_label"))

flow_vs_microscopy_ace2muts_scatterplot <- ggplot() + theme(panel.grid.minor = element_blank()) + 
  labs(x = "Fold ACE2 dependence by flow cytometry", y = "Fold ACE2 dependence by microscopy") +
  scale_x_log10(limits = c(0.5,30), breaks = c(1,3,10,30)) + scale_y_log10(limits = c(0.9,7), breaks = c(1,3,10), expand = c(0,0)) + 
  scale_shape_manual(values = c(3, 21, 22, 23, 24, 25)) +
  scale_color_manual(values = virus_colors2) +
  geom_hline(yintercept = 1, alpha = 0.4) + geom_vline(xintercept = 1, alpha = 0.4) +
  geom_point(data = flow_vs_microscopy_ace2muts, aes(x = ratio.x, y = ratio.y, color = virus_label, shape = cell_label))
flow_vs_microscopy_ace2muts_scatterplot
```

![](ACE2_dependence_files/figure-gfm/Making%20a%20scatterplot%20of%20the%20flow%20and%20microscopy%20data%20for%20the%20high%20human%20ACE2%20mutants-1.png)<!-- -->

``` r
ggsave(file = "Plots/flow_vs_microscopy_ace2muts_scatterplot.pdf", flow_vs_microscopy_ace2muts_scatterplot, height = 1.5, width = 3.5)
ggsave(file = "Plots/flow_vs_microscopy_ace2muts_scatterplot.png", flow_vs_microscopy_ace2muts_scatterplot, height = 1.5, width = 3.5)
```

### Trying to incorporate the bat species range data

``` r
## https://r-spatial.github.io/sf/reference/st_read.html
## https://www.r-graph-gallery.com/168-load-a-shape-file-into-r.html
## https://cfss.uchicago.edu/notes/simple-features/
## https://ggplot2.tidyverse.org/reference/ggsf.html
## https://datascience.blog.wzb.eu/2019/04/30/zooming-in-on-maps-with-sf-and-ggplot2/

#install.packages("Rcpp")
#library(Rcpp)
#install.packages("sf")
#library(sf)
#install.packages("here")
#library(here)
#install.packages("broom")
#library(broom)

world_shape <- here("Data/Maps/TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp") %>% st_read()
```

    ## Reading layer `TM_WORLD_BORDERS-0.3' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/TM_WORLD_BORDERS-0.3/TM_WORLD_BORDERS-0.3.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 246 features and 11 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -180 ymin: -90 xmax: 180 ymax: 83.6236
    ## Geodetic CRS:  WGS 84

``` r
base_world_map_ggplot <- ggplot() + theme_bw() + 
  theme(axis.text = element_blank(), panel.grid.major = element_blank(), axis.ticks = element_blank()) +
  labs(x = NULL, y = NULL) +
  geom_sf(data = world_shape, fill="grey95", color="black",size = 0.1) +
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T) +
  NULL
ggsave(file = "Plots/Base_world_map_ggplot.pdf", base_world_map_ggplot, height = 1.5, width = 4)
base_world_map_ggplot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-1.png)<!-- -->

``` r
ferrum_shape <- here("Data/Maps/ferrumequinum_redlist_species_data_8e16dc36-7b4b-44b9-9840-799c4a0f6a53/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/ferrumequinum_redlist_species_data_8e16dc36-7b4b-44b9-9840-799c4a0f6a53/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 18 features and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -9.495943 ymin: 22.61465 xmax: 144.0388 ymax: 52.63987
    ## Geodetic CRS:  WGS 84

``` r
ferrum_map_plot <- base_world_map_ggplot + geom_sf(data = ferrum_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Ferrum_map_plot.pdf", ferrum_map_plot, height = 2, width = 4)
ferrum_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-2.png)<!-- -->

``` r
affinis_shape <- here("Data/Maps/affinis_redlist_species_data_e5cea578-fa93-46b4-bcd1-72db305e97de/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/affinis_redlist_species_data_e5cea578-fa93-46b4-bcd1-72db305e97de/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 22 features and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: 77.6688 ymin: -10.32216 xmax: 123.1624 ymax: 33.41214
    ## Geodetic CRS:  WGS 84

``` r
affinis_map_plot <- base_world_map_ggplot + geom_sf(data = affinis_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Affinis_map_plot.pdf", affinis_map_plot, height = 2, width = 4)
affinis_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-3.png)<!-- -->

``` r
hippo_shape <- here("Data/Maps/hipposideros_redlist_species_data_81732104-6de7-456f-9dec-2f1fcd484c6f/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/hipposideros_redlist_species_data_81732104-6de7-456f-9dec-2f1fcd484c6f/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 17 features and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -10.53219 ymin: 17.01716 xmax: 79.43162 ymax: 54.54312
    ## Geodetic CRS:  WGS 84

``` r
hippo_map_plot <- base_world_map_ggplot + geom_sf(data = hippo_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Hippo_map_plot.pdf", hippo_map_plot, height = 2, width = 4)
hippo_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-4.png)<!-- -->

``` r
alcyone_shape <- here("Data/Maps/alcyone_redlist_species_data_ee5660d2-1774-4c77-8970-9a473e1c66a5/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/alcyone_redlist_species_data_ee5660d2-1774-4c77-8970-9a473e1c66a5/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 3 features and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -13.74239 ymin: -5.45619 xmax: 31.73008 ymax: 13.37119
    ## Geodetic CRS:  WGS 84

``` r
alcyone_map_plot <- base_world_map_ggplot + geom_sf(data = alcyone_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Alcyone_map_plot.pdf", alcyone_map_plot, height = 2, width = 4)
alcyone_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-5.png)<!-- -->

``` r
landeri_shape <- here("Data/Maps/landeri_redlist_species_data_87e5a8c2-0fd6-4f3d-8f4b-fcf34c2e89f3/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/landeri_redlist_species_data_87e5a8c2-0fd6-4f3d-8f4b-fcf34c2e89f3/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 3 features and 15 fields
    ## Geometry type: POLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -17.53524 ymin: -30.63702 xmax: 43.9498 ymax: 15.21187
    ## Geodetic CRS:  WGS 84

``` r
landeri_map_plot <- base_world_map_ggplot + geom_sf(data = landeri_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Landeri_map_plot.pdf", landeri_map_plot, height = 2, width = 4)
landeri_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-6.png)<!-- -->

``` r
pearsonii_shape <- here("Data/Maps/pearsonii_redlist_species_data_a96e1d46-d9a0-40f7-b3a5-1ad1b91e2431/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/pearsonii_redlist_species_data_a96e1d46-d9a0-40f7-b3a5-1ad1b91e2431/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 1 feature and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: 77.5213 ymin: 6.630936 xmax: 122.3372 ymax: 33.56774
    ## Geodetic CRS:  WGS 84

``` r
pearsonii_map_plot <- base_world_map_ggplot + geom_sf(data = pearsonii_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Pearsonii_map_plot.pdf", affinis_map_plot, height = 2, width = 4)
pearsonii_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-7.png)<!-- -->

``` r
sinicus_shape <- here("Data/Maps/sinicus_redlist_species_data_c0256091-31d3-4426-b8d6-791db2f0e7d6/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/sinicus_redlist_species_data_c0256091-31d3-4426-b8d6-791db2f0e7d6/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 1 feature and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: 76.7799 ymin: 14.14004 xmax: 122.937 ymax: 33.91734
    ## Geodetic CRS:  WGS 84

``` r
sinicus_map_plot <- base_world_map_ggplot + geom_sf(data = sinicus_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Sinicus_map_plot.pdf", sinicus_map_plot, height = 2, width = 4)
sinicus_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-8.png)<!-- -->

``` r
blasii_shape <- here("Data/Maps/blasii_redlist_species_data_cea535e3-2ee3-4223-aad2-d2a071e66a6d/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/blasii_redlist_species_data_cea535e3-2ee3-4223-aad2-d2a071e66a6d/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 3 features and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -8.945001 ymin: -29.70939 xmax: 74.66737 ymax: 46.35565
    ## Geodetic CRS:  WGS 84

``` r
blasii_map_plot <- base_world_map_ggplot + geom_sf(data = blasii_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Blasii_map_plot.pdf", blasii_map_plot, height = 2, width = 4)
blasii_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-9.png)<!-- -->

``` r
euryale_shape <- here("Data/Maps/euryale_redlist_species_data_4dbfc03e-ae50-4d4c-ac73-53a0757f19ec/data_0.shp") %>% st_read()
```

    ## Reading layer `data_0' from data source 
    ##   `/Users/kmatreyek/Box Sync/Github/ACE2_dependence/Data/Maps/euryale_redlist_species_data_4dbfc03e-ae50-4d4c-ac73-53a0757f19ec/data_0.shp' 
    ##   using driver `ESRI Shapefile'
    ## Simple feature collection with 7 features and 15 fields
    ## Geometry type: MULTIPOLYGON
    ## Dimension:     XY
    ## Bounding box:  xmin: -9.894488 ymin: 28.25488 xmax: 61.00445 ymax: 48.94192
    ## Geodetic CRS:  WGS 84

``` r
euryale_map_plot <- base_world_map_ggplot + geom_sf(data = euryale_shape, fill="red", alpha = 0.4, size = 0.2) + 
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Euryale_map_plot.pdf", euryale_map_plot, height = 2, width = 4)
euryale_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-10.png)<!-- -->

``` r
Clade3_map_plot <- base_world_map_ggplot + 
  geom_sf(data = euryale_shape, fill="yellow", alpha = 0.4, size = 0.1) + 
  geom_sf(data = blasii_shape, fill="cyan", alpha = 0.4, size = 0.1) + 
  geom_sf(data = hippo_shape, fill="orange", alpha = 0.4, size = 0.1) + 
  geom_sf(data = ferrum_shape, fill="green", alpha = 0.4, size = 0.1) + 
  geom_point(data = NULL, aes(x = 39.7439, y = 43.5691), size = 1.5, shape = 19) +  ## Sochi national park for Khosta-1 and Khosta-2
  geom_point(data = NULL, aes(x = 27.608611, y = 42.0125), size = 1.5, shape = 19) +  ## Strandzha nature park for BM48-31
  geom_point(data = NULL, aes(x = 36.8219, y = -1.2921), size = 1.5, shape = 19) +  ## Nairobi Kenya as proxy for BtKY72 location
  geom_point(data = NULL, aes(x = 29.63, y = -1.50), size = 1.5, shape = 19) +  ## PRD-0038 location https://www.ncbi.nlm.nih.gov/protein/1867217113
  geom_point(data = NULL, aes(x = 29.71, y = -1.11), size = 1.5, shape = 19) +  ## PDF-2370, PDF-2386 location https://www.ncbi.nlm.nih.gov/protein/QRW38681.1
  geom_point(data = NULL, aes(x = -3.0750174, y = 51.343452), size = 1.5, shape = 19) +  ## Weston-super-Mare UK as proxy for RhGB01 +
  geom_point(data = NULL, aes(x = 39.7439, y = 43.5691), size = 0.5, shape = 19, color = "yellow") +  ## Sochi national park for Khosta-1 and Khosta-2
  geom_point(data = NULL, aes(x = 27.608611, y = 42.0125), size = 0.5, shape = 19, color = "yellow") +  ## Strandzha nature park for BM48-31
  geom_point(data = NULL, aes(x = 36.8219, y = -1.2921), size = 0.5, shape = 19, color = "yellow") +  ## Nairobi Kenya as proxy for BtKY72 location
  geom_point(data = NULL, aes(x = 29.63, y = -1.50), size = 0.5, shape = 19, color = "yellow") +  ## PRD-0038 location https://www.ncbi.nlm.nih.gov/protein/1867217113
  geom_point(data = NULL, aes(x = 29.71, y = -1.11), size = 0.5, shape = 19, color = "yellow") +  ## PDF-2370, PDF-2386 location https://www.ncbi.nlm.nih.gov/protein/QRW38681.1
  geom_point(data = NULL, aes(x = -3.0750174, y = 51.343452), size = 0.5, shape = 19, color = "yellow") +  ## Weston-super-Mare UK as proxy for RhGB01
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Clade3_map_plot.pdf", Clade3_map_plot, height = 1.5, width = 4)
ggsave(file = "Plots/Clade3_map_plot.png", Clade3_map_plot, height = 1.5, width = 4)
Clade3_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-11.png)<!-- -->

``` r
ACE2_clade3_map_plot <- base_world_map_ggplot + 
  geom_sf(data = affinis_shape, fill="magenta", alpha = 0.4, size = 0.1) + 
  geom_sf(data = ferrum_shape, fill="green", alpha = 0.4, size = 0.1) + 
  geom_sf(data = alcyone_shape, fill="red", alpha = 0.4, size = 0.1) + 
  geom_sf(data = landeri_shape, fill="blue", alpha = 0.4, size = 0.1) + 
  geom_sf(data = sinicus_shape, fill="purple", alpha = 0.4, size = 0.1) + 
  geom_point(data = NULL, aes(x = 39.7439, y = 43.5691), size = 1.5, shape = 19) +  ## Sochi national park for Khosta-1 and Khosta-2
  geom_point(data = NULL, aes(x = 27.608611, y = 42.0125), size = 1.5, shape = 19) +  ## Strandzha nature park for BM48-31
  geom_point(data = NULL, aes(x = 36.8219, y = -1.2921), size = 1.5, shape = 19) +  ## Nairobi Kenya as proxy for BtKY72 location
  geom_point(data = NULL, aes(x = 29.63, y = -1.50), size = 1.5, shape = 19) +  ## PRD-0038 location https://www.ncbi.nlm.nih.gov/protein/1867217113
  geom_point(data = NULL, aes(x = 29.71, y = -1.11), size = 1.5, shape = 19) +  ## PDF-2370, PDF-2386 location https://www.ncbi.nlm.nih.gov/protein/QRW38681.1
  geom_point(data = NULL, aes(x = -3.0750174, y = 51.343452), size = 1.5, shape = 19) +  ## Weston-super-Mare UK as proxy for RhGB01 +
  geom_point(data = NULL, aes(x = 39.7439, y = 43.5691), size = 0.5, shape = 19, color = "yellow") +  ## Sochi national park for Khosta-1 and Khosta-2
  geom_point(data = NULL, aes(x = 27.608611, y = 42.0125), size = 0.5, shape = 19, color = "yellow") +  ## Strandzha nature park for BM48-31
  geom_point(data = NULL, aes(x = 36.8219, y = -1.2921), size = 0.5, shape = 19, color = "yellow") +  ## Nairobi Kenya as proxy for BtKY72 location
  geom_point(data = NULL, aes(x = 29.63, y = -1.50), size = 0.5, shape = 19, color = "yellow") +  ## PRD-0038 location https://www.ncbi.nlm.nih.gov/protein/1867217113
  geom_point(data = NULL, aes(x = 29.71, y = -1.11), size = 0.5, shape = 19, color = "yellow") +  ## PDF-2370, PDF-2386 location https://www.ncbi.nlm.nih.gov/protein/QRW38681.1
  geom_point(data = NULL, aes(x = -3.0750174, y = 51.343452), size = 0.5, shape = 19, color = "yellow") +  ## Weston-super-Mare UK as proxy for RhGB01
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/ACE2_clade3_map_plot.pdf", ACE2_clade3_map_plot, height = 1.5, width = 4)
ggsave(file = "Plots/ACE2_clade3_map_plot.png", ACE2_clade3_map_plot, height = 1.5, width = 4)
ACE2_clade3_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-12.png)<!-- -->

``` r
Clade3_combined_map_plot <- base_world_map_ggplot + 
  geom_sf(data = euryale_shape, fill="yellow", alpha = 0.4, size = 0.1) + 
  geom_sf(data = blasii_shape, fill="cyan", alpha = 0.4, size = 0.1) + 
  geom_sf(data = hippo_shape, fill="orange", alpha = 0.4, size = 0.1) + 
  geom_sf(data = ferrum_shape, fill="green", alpha = 0.4, size = 0.1) + 
  geom_sf(data = alcyone_shape, fill="red", alpha = 0.4, size = 0.1) + 
  geom_sf(data = landeri_shape, fill="blue", alpha = 0.4, size = 0.1) + 
  geom_point(data = NULL, aes(x = 39.7439, y = 43.5691), size = 0.5) +  ## Sochi national park for Khosta-1 and Khosta-2
  geom_point(data = NULL, aes(x = 27.608611, y = 42.0125), size = 0.5) +  ## Strandzha nature park for BM48-31
  geom_point(data = NULL, aes(x = 36.8219, y = -1.2921), size = 0.5) +  ## Nairobi Kenya as proxy for BtKY72 location
  geom_point(data = NULL, aes(x = 30.0619, y = -1.9441), size = 0.5) +  ## Kigali Rwanda as proxy for PRD-0038 location
  geom_point(data = NULL, aes(x = 32.5825, y = 0.3476), size = 0.5) +  ## Kampala Uganda as proxy for PRD-2370, PRD-2386 location +
  geom_point(data = NULL, aes(x = -3.0750174, y = 51.343452), size = 0.5) +  ## Weston-super-Mare UK as proxy for RhGB01
  coord_sf(xlim = c(-12, 145), ylim = c(-19, 60), expand = T)
```

    ## Coordinate system already present. Adding new coordinate system, which will replace the existing one.

``` r
ggsave(file = "Plots/Clade3_combined_map_plot.pdf", Clade3_combined_map_plot, height = 1.5, width = 4)
ggsave(file = "Plots/Clade3_combined_map_plot.png", Clade3_combined_map_plot, height = 1.5, width = 4)
Clade3_combined_map_plot
```

![](ACE2_dependence_files/figure-gfm/Incorporating%20the%20bat%20species%20range%20data-13.png)<!-- -->

``` r
## Flow data first

flow_btky72 <- bat_ace2s_2 %>% filter(virus_label == "BtKY72 RBD")
flow_btky72_summary <- bat_ace2s_2_summary %>% filter(virus_label == "BtKY72 RBD")

flow_btky72$cell_label <- factor(flow_btky72$cell_label, levels = bat_ace2_levels)
flow_btky72_summary$cell_label <- factor(flow_btky72_summary$cell_label, levels = bat_ace2_levels)

Bar_chart_flow_btky72 <- ggplot() + labs(x = NULL, y = NULL) + 
  theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0), panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(), panel.grid.minor = element_blank()) + 
  scale_y_log10(breaks = c(1,10,100)) + geom_hline(yintercept = 1, alpha = 0.5) + 
  geom_quasirandom(data = flow_btky72, aes(x = cell_label, y = fold_ace2_dep_infection), alpha = 0.2) +
  geom_point(data = flow_btky72_summary, aes(x = cell_label, y = geomean), shape = 95, size = 10)
Bar_chart_flow_btky72
```

![](ACE2_dependence_files/figure-gfm/Make%20a%20barchart%20of%20infectivity%20for%20BtKY72%20across%20alleles-1.png)<!-- -->

``` r
ggsave(file = "Plots/Bar_chart_flow_btky72.pdf", Bar_chart_flow_btky72, height = 1.5, width = 2.5)


## Microscopy next

microscopy_btky72 <- microscopy3_batace2 %>% filter(virus_label == "BtKY72 RBD")
microscopy_btky72_summary <- microscopy_batace2_summary %>% filter(virus_label == "BtKY72 RBD")

microscopy_btky72$cell_label <- factor(microscopy_btky72$cell_label, levels = bat_ace2_levels)
microscopy_btky72_summary$cell_label <- factor(microscopy_btky72_summary$cell_label, levels = bat_ace2_levels)

Bar_chart_microscopy_btky72 <- ggplot() + labs(x = NULL, y = NULL) + 
  theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0), panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(), panel.grid.minor = element_blank()) + 
  scale_y_log10(breaks = c(1,3,10)) + geom_hline(yintercept = 1, alpha = 0.5) + 
  geom_quasirandom(data = microscopy_btky72, aes(x = cell_label, y = nir_mcherry_overlap_ratio), alpha = 0.2) +
  geom_point(data = microscopy_btky72_summary, aes(x = cell_label, y = ratio), shape = 95, size = 10)
Bar_chart_microscopy_btky72
```

![](ACE2_dependence_files/figure-gfm/Make%20a%20barchart%20of%20infectivity%20for%20BtKY72%20across%20alleles-2.png)<!-- -->

``` r
ggsave(file = "Plots/Bar_chart_microscopy_btky72.pdf", Bar_chart_microscopy_btky72, height = 1.5, width = 2.43)


## Flow again for the relevant variants now

flowmuts_btky72 <- flow_ace2_muts4 %>% filter(virus_label == "BtKY72 RBD" & cell_label %in% c("H.sapiens", "K31D"))
flowmuts_btky72_summary <- flow_ace2_muts_summary %>% filter(virus_label == "BtKY72 RBD" & cell_label %in% c("H.sapiens", "K31D"))

Bar_chart_flowmuts_btky72 <- ggplot() + labs(x = NULL, y = NULL) + 
  theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0), panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(), panel.grid.minor = element_blank()) + 
  scale_y_log10(breaks = c(1,10,100)) + geom_hline(yintercept = 1, alpha = 0.5) + 
  geom_quasirandom(data = flowmuts_btky72, aes(x = cell_label, y = fold_ace2_dep_infection), alpha = 0.2) +
  geom_point(data = flowmuts_btky72_summary, aes(x = cell_label, y = ratio), shape = 95, size = 10)
Bar_chart_flowmuts_btky72
```

![](ACE2_dependence_files/figure-gfm/Make%20a%20barchart%20of%20infectivity%20for%20BtKY72%20across%20alleles-3.png)<!-- -->

``` r
ggsave(file = "Plots/Bar_chart_flowmuts_btky72.pdf", Bar_chart_flowmuts_btky72, height = 1.1, width = 0.85)


## Microscopy again for the relevant variants

micromuts_btky72 <- microscopy_ace2muts %>% filter(virus_label == "BtKY72 RBD" & cell_label %in% c("H.sapiens", "K31D"))
micromuts_btky72_summary <- microscopy_ace2muts_summary %>% filter(virus_label == "BtKY72 RBD" & cell_label %in% c("H.sapiens", "K31D"))

Bar_chart_micromuts_btky72 <- ggplot() + labs(x = NULL, y = NULL) + 
  theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0), panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(), panel.grid.minor = element_blank()) + 
  scale_y_log10(breaks = c(1,3,10)) + geom_hline(yintercept = 1, alpha = 0.5) + 
  geom_quasirandom(data = micromuts_btky72, aes(x = cell_label, y = nir_mcherry_overlap_ratio), alpha = 0.2) +
  geom_point(data = micromuts_btky72_summary, aes(x = cell_label, y = ratio), shape = 95, size = 10)
Bar_chart_micromuts_btky72
```

![](ACE2_dependence_files/figure-gfm/Make%20a%20barchart%20of%20infectivity%20for%20BtKY72%20across%20alleles-4.png)<!-- -->

``` r
ggsave(file = "Plots/Bar_chart_micromuts_btky72.pdf", Bar_chart_micromuts_btky72, height = 1.1, width = 0.78)


## Flow for Khosta-1

flow_khosta1 <- bat_ace2s_2 %>% filter(virus_label == "Khosta1 RBD")
flow_khosta1_summary <- bat_ace2s_2_summary %>% filter(virus_label == "Khosta1 RBD")

flow_khosta1$cell_label <- factor(flow_khosta1$cell_label, levels = bat_ace2_levels)
flow_khosta1_summary$cell_label <- factor(flow_khosta1_summary$cell_label, levels = bat_ace2_levels)

Bar_chart_flow_khosta1 <- ggplot() + labs(x = NULL, y = NULL) + 
  theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0), panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(), panel.grid.minor = element_blank()) + 
  scale_y_log10(breaks = c(1,10,100)) + geom_hline(yintercept = 1, alpha = 0.5) + 
  geom_quasirandom(data = flow_khosta1, aes(x = cell_label, y = fold_ace2_dep_infection), alpha = 0.2) +
  geom_point(data = flow_khosta1_summary, aes(x = cell_label, y = geomean), shape = 95, size = 10)
Bar_chart_flow_khosta1
```

![](ACE2_dependence_files/figure-gfm/Make%20a%20barchart%20of%20infectivity%20for%20BtKY72%20across%20alleles-5.png)<!-- -->

``` r
ggsave(file = "Plots/Bar_chart_flow_khosta1.pdf", Bar_chart_flow_khosta1, height = 1.5, width = 2.5)

## Microscopy for Khosta-1

microscopy_khosta1 <- microscopy3_batace2 %>% filter(virus_label == "Khosta1 RBD")
microscopy_khosta1_summary <- microscopy_batace2_summary %>% filter(virus_label == "Khosta1 RBD")

microscopy_khosta1$cell_label <- factor(microscopy_khosta1$cell_label, levels = bat_ace2_levels)
microscopy_khosta1_summary$cell_label <- factor(microscopy_khosta1_summary$cell_label, levels = bat_ace2_levels)

Bar_chart_microscopy_khosta1 <- ggplot() + labs(x = NULL, y = NULL) + 
  theme(axis.text.x = element_text(angle = -90, hjust = 0, vjust = 0.5), strip.text.y = element_text(angle = 0), panel.grid.minor.x = element_blank(), panel.grid.major.x = element_blank(), panel.grid.minor = element_blank()) + 
  scale_y_log10(breaks = c(1,3,10)) + geom_hline(yintercept = 1, alpha = 0.5) + 
  geom_quasirandom(data = microscopy_khosta1, aes(x = cell_label, y = nir_mcherry_overlap_ratio), alpha = 0.2) +
  geom_point(data = microscopy_khosta1_summary, aes(x = cell_label, y = ratio), shape = 95, size = 10)
Bar_chart_microscopy_khosta1
```

![](ACE2_dependence_files/figure-gfm/Make%20a%20barchart%20of%20infectivity%20for%20BtKY72%20across%20alleles-6.png)<!-- -->

``` r
ggsave(file = "Plots/Bar_chart_microscopy_khosta1.pdf", Bar_chart_microscopy_khosta1, height = 1.5, width = 2.43)
```

``` r
# https://rpubs.com/sinhrks/plot_mds

rbd_dist_matrix3 <- rbd_dist_matrix
for(x in 1:nrow(rbd_dist_matrix3)){rownames(rbd_dist_matrix3)[x] <- strsplit(rownames(rbd_dist_matrix3)[x], "__",1)[[1]][1]}

mds_plotting_frame <- data.frame(cmdscale(rbd_dist_matrix3, eig = TRUE)$points)
mds_plotting_frame$name <- row.names(mds_plotting_frame)

mds_plotting_frame2 <- merge(mds_plotting_frame, clade_labels_key, by = "name")


ACE2_receptor_usage_by_sequence_matrix <- 
ggplot() + #scale_x_continuous(limits = c(-50, 50)) + scale_y_continuous(limits = c(-30, 50)) + 
  theme(panel.grid.minor = element_blank(), panel.grid.major = element_blank()) + 
  labs(x = "Scaled dimension 1", y = "Scaled dimension 2") +
  #geom_hline(yintercept = 0, alpha = 0.2) + geom_vline(xintercept = 0, alpha = 0.2) +
  geom_point(data = mds_plotting_frame2, aes(x = X1, y = X2, color = clade), alpha = 0.4) +
  geom_text_repel(data = mds_plotting_frame2 %>% filter(name %in% c("BtKY72","SARS_CoV-2","SARS_CoV","YN2013","RaTG15","Khosta2","Khosta1","BB9904")), aes(x = X1, y = X2, label = name),force_pull = -0.04, segment.color = "orange", segment.alpha = 0.5, size = 2)
ACE2_receptor_usage_by_sequence_matrix
```

![](ACE2_dependence_files/figure-gfm/Use%20multi-dimensional%20scaling%20to%20visualize%20the%20sequence%20data%20for%20the%20conclusion%20slide-1.png)<!-- -->

``` r
ggsave(file = "Plots/ACE2_receptor_usage_by_sequence_matrix.pdf", ACE2_receptor_usage_by_sequence_matrix, height = 1.7, width = 3.7)
```

``` r
supptable <- read.csv(file = "Data/ACE2_dependence_tables - Table1_sequences_used.csv") %>% filter(cys != 1 & clade != 5)

#supptable2 <- merge(supptable[,c("name","cys")], clade_labels_key, by = "name")

clade_cys_table <- data.frame(table(supptable[,c("cys","clade")]))

clade_cys_table$cys = factor(clade_cys_table$cys, levels = c(2,0))

Cysteine_plot <- ggplot() + labs(x = "Clade", y = "Cysteines") +
  scale_fill_gradient(low = "white", high = "red") + 
  geom_tile(data = clade_cys_table, aes(x = clade, y = cys, fill = Freq)) +
  geom_text(data = clade_cys_table, aes(x = clade, y = cys, label = Freq))
Cysteine_plot
```

![](ACE2_dependence_files/figure-gfm/Disulfides-1.png)<!-- -->

``` r
ggsave(file = "Plots/Cysteine_plot.pdf", Cysteine_plot, height = 0.9, width = 2)
```
