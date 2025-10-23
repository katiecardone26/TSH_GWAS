# load packages
import pandas as pd
import argparse as ap
from datetime import datetime
import sys
import numpy as np

# define arguments
def make_arg_parser():
    parser = ap.ArgumentParser(description = '.')

    parser.add_argument('--vep', required = True, help = 'vep output file')

    parser.add_argument('--coords', required = True, help = 'gene coordinate file')

    parser.add_argument('--known', required = True, help = 'known genes file')

    parser.add_argument('--output_prefix', required = True, help = 'output prefix')

    return parser

args = make_arg_parser().parse_args()

# convert args to variables
vep_filepath = args.vep
coords_filepath = args.coords
known_filepath = args.known
output_prefix = args.output_prefix

# read in input files
vep = pd.read_csv(vep_filepath, sep = '\t', comment = '#', header = None)
gene_coord = pd.read_csv(coords_filepath, sep = '\t', usecols = ['ENS_ID', 'START', 'STOP'])
known = pd.read_csv(known_filepath, header = None)

# clean known genes file
## rename column
known.rename(columns = {0 : 'gene'}, inplace = True)

## remove extra genes with upstream, downstream, or /
known = known[~known['gene'].str.contains('upstream|downstream|/')]

## split rows that contain '-', except genes that actually contain them (excluded)
exclude = known[known['gene'].str.contains('AS1|HLA|CRHR1|CD302')]
include = known[~known['gene'].str.contains('AS1|HLA|CRHR1|CD302')].reset_index(drop = True)
include_split = include.assign(gene = include['gene'].str.split('-').explode('gene'))
known = pd.concat([include_split, exclude], axis = 0)
known = known.drop_duplicates().sort_values(by = 'gene').reset_index(drop = True)

## add upstream and downstream columns
known['upstream'] = 'upstream_' + known['gene']
known['downstream'] = 'downstream_' + known['gene']

## create known gene list
known_gene_list = known[['gene', 'upstream', 'downstream']].values.flatten()

# rename columns in gene coords file
gene_coord = gene_coord.rename(columns = {'ENS_ID' : 'ENSEMBL_ID'})

# create chromosome and position columns
print(vep)
vep[['CHR', 'POS']] = vep[1].str.split(':', 1, expand = True)

# subset columns
vep_sub = vep[[0, 'CHR', 'POS', 2, 3, 4, 6]]

# change columns dtype
vep_sub['POS'] = vep_sub['POS'].astype('Int64')

# rename columns
vep_sub.rename(columns={0 : 'ID',
                            2 : 'ALLELE',
                            3 : 'GENE',
                            4 : 'ENSEMBL_ID',
                            6 : 'RSID'}, inplace = True)

# replace '-' with missing in Allele and RSID columns
vep_sub['ALLELE'] = vep_sub['ALLELE'].replace('-', np.nan)
vep_sub['RSID'] = vep_sub['RSID'].replace('-', np.nan)

# remove non-rsids from column
vep_sub['RSID'] = vep_sub['RSID'].str.replace(',.*', '', regex = True)

# identify variants w and w/o gene annotations
vep_gene = vep_sub[~vep_sub['GENE'].isin(['-'])]
vep_no_gene = vep_sub[vep_sub['GENE'].isin(['-'])]

# merge vep file with gene coords file
vep_gene_coord = vep_gene.merge(gene_coord, on = 'ENSEMBL_ID', how = 'inner')

# genes that are within start/stop coordinates
## filter to these genes based on position
within_gene = vep_gene_coord[(vep_gene_coord['POS'] >= vep_gene_coord['START']) & (vep_gene_coord['POS'] <= vep_gene_coord['STOP'])]

## drop ensembl ID and then drop duplicates
within_gene = within_gene.drop(columns = ['ENSEMBL_ID', 'START', 'STOP']).drop_duplicates()

## identify dups
within_gene_dups = within_gene[within_gene['ID'].duplicated(keep = False)]
within_gene_no_dups = within_gene[~within_gene['ID'].isin(within_gene_dups['ID'])]

## filter to known genes to prioritize labeling of them
within_gene_dups_known = within_gene_dups[within_gene_dups['GENE'].isin(known_gene_list)]

## check to see if there are still dups after filtering to known genes, and if so, aggregate them
if len(within_gene_dups_known[within_gene_dups_known['ID'].duplicated(keep = False)].index) != 0:
    within_gene_dups_known = within_gene_dups_known.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'GENE': lambda x: '/'.join(sorted(set(x)))})

## filter to IDs with non-known genes and aggregate them
within_gene_dups_no_known = within_gene_dups[~within_gene_dups['ID'].isin(within_gene_dups_known['ID'])]
within_gene_dups_no_known = within_gene_dups_no_known.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'GENE': lambda x: '/'.join(sorted(set(x)))})

## reconcat
within_gene_fixed = pd.concat([within_gene_no_dups, within_gene_dups_known, within_gene_dups_no_known], axis = 0)
within_gene_fixed = within_gene_fixed.sort_values(by = 'ID').reset_index(drop = True)

## check for remaining duplicates
if len(within_gene_fixed[within_gene_fixed['ID'].duplicated(keep = False)].index) != 0:
    print(within_gene_fixed[within_gene_fixed['ID'].duplicated(keep = False)].sort_values(by = 'ID'))
    sys.exit('duplicates still remain in within gene df')

# genes that are not within start/stop coordinates
## identify genes
not_within_gene = vep_gene_coord[~((vep_gene_coord['POS'] >= vep_gene_coord['START']) & (vep_gene_coord['POS'] <= vep_gene_coord['STOP']))]
not_within_gene = not_within_gene[~not_within_gene['ID'].isin(within_gene['ID'])]

## identify if closest gene is upstream or downstream
upstream = not_within_gene[not_within_gene['POS'] < not_within_gene['START']]
downstream = not_within_gene[not_within_gene['POS'] > not_within_gene['STOP']]

## filter to known genes to prioritize labeling them, drop ensembl ID, start, and stop columns and then drop duplicates
upstream_known = upstream[upstream['GENE'].isin(known_gene_list)].drop(columns = ['ENSEMBL_ID', 'START', 'STOP']).drop_duplicates()
downstream_known = downstream[downstream['GENE'].isin(known_gene_list)].drop(columns = ['ENSEMBL_ID', 'START', 'STOP']).drop_duplicates()

## check for duplicates in known genes, and if they exist, combine thems
if len(upstream_known[upstream_known['ID'].duplicated(keep = False)].index) != 0:
    upstream_known = upstream_known.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'GENE': lambda x: '/'.join(sorted(set(x)))})

if len(downstream_known[downstream_known['ID'].duplicated(keep = False)].index) != 0:
    downstream_known = downstream_known.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'GENE': lambda x: '/'.join(sorted(set(x)))})

## filter to ids with non-known genes
upstream_no_known = upstream[~upstream['ID'].isin(upstream_known['ID'])]
downstream_no_known = downstream[~downstream['ID'].isin(downstream_known['ID'])]

## filter to non-known gene file to closest variant by position
upstream_no_known['DISTANCE'] = upstream_no_known['START'] - upstream_no_known['POS']
upstream_no_known = upstream_no_known.loc[upstream_no_known.groupby('ID')['DISTANCE'].idxmin()]

downstream_no_known['DISTANCE'] = downstream_no_known['POS'] - downstream_no_known['STOP']
downstream_no_known = downstream_no_known.loc[downstream_no_known.groupby('ID')['DISTANCE'].idxmin()]

## drop ensembl ID, start, stop, and distance columns
upstream_no_known = upstream_no_known.drop(columns = ['ENSEMBL_ID', 'START', 'STOP', 'DISTANCE'])
downstream_no_known = downstream_no_known.drop(columns = ['ENSEMBL_ID', 'START', 'STOP', 'DISTANCE'])

## check for remaining duplicates, and if they exist, combine them
if len(upstream_no_known[upstream_no_known['ID'].duplicated(keep = False)].index) != 0:
    upstream_no_known = upstream_no_known.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'GENE': lambda x: '/'.join(sorted(set(x)))})

if len(downstream_no_known[downstream_no_known['ID'].duplicated(keep = False)].index) != 0:
    downstream_no_known = downstream_no_known.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'GENE': lambda x: '/'.join(sorted(set(x)))})

## reconcat upstream and downstream
upstream_fixed = pd.concat([upstream_known, upstream_no_known], axis = 0)
downstream_fixed = pd.concat([downstream_known, downstream_no_known], axis = 0)

## clean up overlapping ids between upstream and downstream dfs
### make df copies
upstream_tmp = upstream_fixed.copy()
downstream_tmp = downstream_fixed.copy()

### add back in gene coords
vep_gene_coord_sub = vep_gene_coord[['ID', 'GENE', 'ENSEMBL_ID', 'START', 'STOP']]

upstream_tmp = upstream_tmp.merge(vep_gene_coord_sub, on = ['ID', 'GENE'], how = 'inner')

downstream_tmp = downstream_tmp.merge(vep_gene_coord_sub, on = ['ID', 'GENE'], how = 'inner')

### make extra columns
upstream_tmp['DISTANCE'] = upstream_tmp['START'] - upstream_tmp['POS']
upstream_tmp['DATATYPE'] = 'UPSTREAM'
downstream_tmp['DISTANCE'] = upstream_tmp['POS'] - upstream_tmp['STOP']
downstream_tmp['DATATYPE'] = 'DOWNSTREAM'

### identify overlapping variants
upstream_tmp = upstream_tmp[upstream_tmp['ID'].isin(downstream_tmp['ID'])]
downstream_tmp = downstream_tmp[downstream_tmp['ID'].isin(upstream_tmp['ID'])]

### concatenate
both_upstream_downstream = pd.concat([upstream_tmp, downstream_tmp], axis = 0)

### aggregate to variants with the closest distance
both_upstream_downstream = both_upstream_downstream.loc[both_upstream_downstream.groupby('ID')['DISTANCE'].idxmin()]

### split back into upstream and downstream variants
upstream_filt = both_upstream_downstream[both_upstream_downstream['DATATYPE'] == 'UPSTREAM']
downstream_filt = both_upstream_downstream[both_upstream_downstream['DATATYPE'] == 'DOWNSTREAM']
### remove extra columns
upstream_filt = upstream_filt.drop(columns = ['ENSEMBL_ID', 'START', 'STOP', 'DISTANCE', 'DATATYPE'])
downstream_filt = downstream_filt.drop(columns = ['ENSEMBL_ID', 'START', 'STOP', 'DISTANCE', 'DATATYPE'])

### create df without these variants
upstream_fixed_no_overlap = upstream_fixed[~upstream_fixed['ID'].isin([both_upstream_downstream['ID']])]
downstream_fixed_no_overlap = downstream_fixed[~downstream_fixed['ID'].isin([both_upstream_downstream['ID']])]

### reconcate
upstream_fixed = pd.concat([upstream_fixed_no_overlap, upstream_filt], axis = 0)
downstream_fixed = pd.concat([downstream_fixed_no_overlap, downstream_filt], axis = 0)

## add upstream and downstream gene labels
upstream_fixed['GENE'] = 'upstream_' + upstream_fixed['GENE']
downstream_fixed['GENE'] = 'downstream_' + downstream_fixed['GENE']

## concentate upstream and downstream
not_within_gene_fixed = pd.concat([upstream_fixed, downstream_fixed], axis = 0)

# concatenate within/not within gene
vep_gene_fixed = pd.concat([within_gene_fixed, not_within_gene_fixed], axis = 0)

# drop duplicates(for good measure)
vep_gene_fixed = vep_gene_fixed.drop_duplicates()

# check for renaming duplicates
if len(vep_gene_fixed[vep_gene_fixed['ID'].duplicated(keep = False)].index) != 0:
    # identify dups
    vep_gene_fixed_dups = vep_gene_fixed[vep_gene_fixed['ID'].duplicated(keep = False)]

    # make new gene column without upstream and downstream
    vep_gene_fixed_dups = vep_gene_fixed_dups.reset_index(drop = True)
    vep_gene_fixed_dups['OLD_GENE'] = vep_gene_fixed_dups['GENE']
    vep_gene_fixed_dups['OLD_GENE'] = vep_gene_fixed_dups['OLD_GENE'].str.replace('downstream_', '')
    vep_gene_fixed_dups['OLD_GENE'] = vep_gene_fixed_dups['OLD_GENE'].str.replace('upstream_', '')
    vep_gene_fixed_dups_split = vep_gene_fixed_dups.assign(OLD_GENE = vep_gene_fixed_dups['OLD_GENE'].str.split('/')).explode('OLD_GENE')

    # subset original column
    vep_merge = not_within_gene[['ID', 'GENE', 'START', 'STOP']]
    vep_merge = vep_merge.rename(columns = {'GENE' : 'OLD_GENE'})

    # merge
    vep_merge = vep_merge.merge(vep_gene_fixed_dups_split, on = ['ID', 'OLD_GENE'], how = 'inner')

    # calculate distance
    upstream_tmp = vep_merge[vep_merge['GENE'].str.contains('upstream')]
    upstream_tmp['DISTANCE'] = upstream_tmp['START'] - upstream_tmp['POS']
    downstream_tmp = vep_merge[vep_merge['GENE'].str.contains('downstream')]
    downstream_tmp['DISTANCE'] = downstream_tmp['POS'] - downstream_tmp['STOP']
    vep_distance = pd.concat([upstream_tmp, downstream_tmp], axis = 0)

    # filter to known genes and prioritize those
    vep_distance_known = vep_distance[vep_distance['OLD_GENE'].isin(known_gene_list)]
    # drop duplicates in known genes by selecting the closest gene
    vep_distance_known = vep_distance_known.sort_values(by = ['ID', 'DISTANCE']).drop_duplicates(subset = 'ID', keep = 'first')
    
    # remove known gene variants
    vep_distance_no_known = vep_distance[~vep_distance['ID'].isin(vep_distance_known['ID'])]
    # drop duplicates by selecting closest gene
    vep_distance_no_known = vep_distance_no_known.sort_values(by = ['ID', 'DISTANCE']).drop_duplicates(subset = 'ID', keep = 'first')
    
    # make df without dups
    vep_gene_fixed_no_dups = vep_gene_fixed[~vep_gene_fixed['ID'].isin(vep_gene_fixed_dups['ID'])]
    
    # reconcat
    vep_gene_fixed_again = pd.concat([vep_distance_known, vep_distance_no_known], axis = 0)
    vep_gene_fixed_again = vep_gene_fixed_again.drop(columns = ['OLD_GENE', 'START', 'STOP', 'DISTANCE'])
    vep_gene_fixed = pd.concat([vep_gene_fixed_no_dups, vep_gene_fixed_again], axis = 0)

    # one last check for dups
    if len(vep_gene_fixed[vep_gene_fixed['ID'].duplicated(keep = False)].index) != 0:
        print(vep_gene_fixed[vep_gene_fixed['ID'].duplicated(keep = False)].sort_values(by = ['ID']))
        sys.exit('duplicates still present in final dataframe')

else:
    print('no duplicates present in final dataframe')

# remove variants with gene labels from no gene df
vep_no_gene = vep_no_gene[~vep_no_gene['ID'].isin(vep_gene_fixed['ID'])]

# aggregate genes to remove duplicates
print(vep_no_gene)
vep_no_gene = vep_no_gene.groupby(['ID', 'CHR', 'POS', 'ALLELE', 'RSID'], as_index = False).agg({'ENSEMBL_ID': lambda x: '/'.join(sorted(set(x)))})
print(vep_no_gene)

# add in variants with no genes
if len(vep_no_gene.index) != 0:
    vep_no_gene = vep_no_gene.rename(columns = {'ENSEMBL_ID' : 'GENE'})
    vep_fixed = pd.concat([vep_gene_fixed, vep_no_gene], axis = 0)
else:
    vep_fixed = vep_gene_fixed.copy()

print(vep_fixed)

# export file
output_filepath = output_prefix + '.vep_output.cleaned.txt'
vep_fixed.to_csv(output_filepath, sep = '\t', index = None)