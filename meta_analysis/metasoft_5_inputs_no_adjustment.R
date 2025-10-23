# intialize libaraies 
library(tidyverse)
library(data.table)
library(argparse)

# set up arguments
parser <- ArgumentParser()

parser$add_argument('--aou_input', required = TRUE, help = "Path to the AOU GWAS input file")
parser$add_argument('--atlas_input', required = TRUE, help = "Path to the ATLAS GWAS input file")
parser$add_argument('--biome_input', required = TRUE, help = "Path to the BioMe GWAS input file")
parser$add_argument('--pmbb_input', required = TRUE, help = "Path to the PMBB GWAS input file")
parser$add_argument('--biovu_input', required = TRUE, help = "Path to the BioVU GWAS input file")
parser$add_argument('--output_prefix', required = TRUE, help = "Output prefix")

args <- parser$parse_args()

aou_input = args$aou_input
atlas_input = args$atlas_input
biome_input = args$biome_input
pmbb_input = args$pmbb_input
biovu_input = args$biovu_input
output_prefix = args$output_prefix

# load the data 
aou <- fread(aou_input, sep = '\t')
atlas <- fread(atlas_input, sep = '\t')
biome <- fread(biome_input, sep = '\t')
pmbb <- fread(pmbb_input, sep = '\t')
biovu <- fread(biovu_input, sep = '\t')

# change ID format in ATLAS and BioVU
atlas=atlas%>%
mutate(ID = paste0('chr', ID))
biovu=biovu%>%
mutate(ID = paste0('chr', CHR, ':', POS, ':', REF, ':', ALT))

# Select relevant columns
aou_sub = aou %>%
select(ID, BETA, SE)
atlas_sub = atlas %>%
select(ID, BETA, SE)
biome_sub = biome %>%
select(ID, BETA, SE)
pmbb_sub = pmbb %>%
select(ID, BETA, SE)
biovu_sub = biovu %>%
select(ID, BETA, SE)

# Rename columns for merging
colnames(aou_sub) <- c("MarkerID", "BETA_AOU", "SE_AOU")
colnames(atlas_sub) <- c("MarkerID", "BETA_ATLAS", "SE_ATLAS")
colnames(biome_sub) <- c("MarkerID", "BETA_BIOME", "SE_BIOME")
colnames(pmbb_sub) <- c("MarkerID", "BETA_PMBB", "SE_PMBB")
colnames(biovu_sub) <- c("MarkerID", "BETA_BIOVU", "SE_BIOVU")

# Merge datasets
union_df <- full_join(aou_sub, atlas_sub, by = "MarkerID") %>% 
full_join(biome_sub, by = "MarkerID") %>%
full_join(pmbb_sub, by = "MarkerID") %>%
full_join(biovu_sub, by = "MarkerID")

# Reorder columns to fit Metasoft format
union_df <- union_df %>% select(MarkerID, BETA_AOU, SE_AOU, BETA_ATLAS, SE_ATLAS, BETA_BIOME, SE_BIOME, BETA_PMBB, SE_PMBB, BETA_BIOVU, SE_BIOVU)

# Replace missing values with "NA" in union_df
union_df[is.na(union_df)] <- "NA"

# make output file names
union_output_file = paste0(output_prefix, '.union.txt')

# Write to files
write.table(union_df, union_output_file, quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)