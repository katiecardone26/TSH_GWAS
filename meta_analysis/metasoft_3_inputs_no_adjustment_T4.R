# intialize libaraies 
library(tidyverse)
library(data.table)
library(argparse)

# set up arguments
parser <- ArgumentParser()

parser$add_argument('--aou_input', required=TRUE, help="Path to the AOU GWAS input file")
parser$add_argument('--atlas_input', required=TRUE, help="Path to the ATLAS GWAS input file")
parser$add_argument('--biome_input', required=TRUE, help="Path to the BioMe GWAS input file")
parser$add_argument('--output_prefix', required=TRUE, help="Output prefix")

args <- parser$parse_args()

aou_input=args$aou_input
atlas_input=args$atlas_input
biome_input=args$biome_input
output_prefix=args$output_prefix

# load the data 
aou <- fread(aou_input, sep='\t')
atlas <- fread(atlas_input, sep='\t')
biome <- fread(biome_input, sep='\t')

# Select relevant columns
aou_sub = aou %>%
select(ID, BETA, SE)
atlas_sub = atlas %>%
select(ID, BETA, SE)
biome_sub = biome %>%
select(ID, BETA, SE)

# Rename columns for merging
colnames(aou_sub) <- c("MarkerID", "BETA_AOU", "SE_AOU")
colnames(atlas_sub) <- c("MarkerID", "BETA_ATLAS", "SE_ATLAS")
colnames(biome_sub) <- c("MarkerID", "BETA_BIOME", "SE_BIOME")

# change ID format in ATLAS
atlas_sub=atlas_sub%>%
mutate(MarkerID = paste0('chr', MarkerID))

# Merge datasets
union_df <- full_join(aou_sub, atlas_sub, by = "MarkerID") %>% full_join(biome_sub, by = "MarkerID")

# Reorder columns to fit Metasoft format
union_df <- union_df %>% select(MarkerID, BETA_AOU, SE_AOU, BETA_ATLAS, SE_ATLAS, BETA_BIOME, SE_BIOME)

# Replace missing values with "NA" in union_df
union_df[is.na(union_df)] <- "NA"

# make output file names
union_output_file = paste0(output_prefix, '.union.txt')

# Write to files
write.table(union_df, union_output_file, quote = FALSE, sep = "\t", row.names = FALSE, col.names = FALSE)