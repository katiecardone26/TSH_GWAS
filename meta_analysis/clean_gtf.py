# load modules
import pandas as pd
import argparse as ap
import numpy as np
import sys

# define arguments
def make_arg_parser():
    parser = ap.ArgumentParser(description = ".")

    parser.add_argument('--coords', required = True, help = 'gene coordinate file')

    parser.add_argument('--ref', required = True, help = 'refseq file')

    parser.add_argument('--output_prefix', required = True, help = 'output prefix')

    return parser

args = make_arg_parser().parse_args()

# parse arguments
coords_file = args.coords
ref_file = args.ref
output_prefix = args.output_prefix

# read in input files
gtf = pd.read_csv(coords_file, header = None, low_memory = False)
ref = pd.read_csv(ref_file, sep = '\s+')

# filter to genes
gtf_gene = gtf[gtf[2].isin(['gene'])]

# remove annotations without gene names
gtf_gene_name = gtf_gene[gtf_gene[8].str.contains('gene_name')]

# subset and rename columns
gtf_sub = gtf_gene_name[[0, 3, 4, 8]]
gtf_sub.rename(columns = {0 : 'CHR', 3 : 'START', 4 : 'STOP'}, inplace = True)
gtf_sub_no_gene_name = gtf_gene[[0, 3, 4, 8]]
gtf_sub_no_gene_name.rename(columns = {0 : 'CHR', 3 : 'START', 4 : 'STOP'}, inplace = True)

# split column with gene information
gtf_sub[[0, 1, 2, 3, 4, 5]] = gtf_sub[8].str.split(';', expand = True)
gtf_sub_no_gene_name[[0, 1, 2, 3, 4, 5]] = gtf_sub_no_gene_name[8].str.split(';', expand = True)

# filter and rename again
gtf_split = gtf_sub[['CHR', 'START', 'STOP', 0, 2]]
gtf_split.rename(columns = {0 : 'ENS_ID', 2 : 'GENE'}, inplace = True)
gtf_split['GENE'] = gtf_split['GENE'].replace(['gene_sourcehavana', np.nan])
gtf_split_no_gene_name = gtf_sub_no_gene_name[['CHR', 'START', 'STOP', 0, 2]]
gtf_split_no_gene_name.rename(columns = {0 : 'ENS_ID', 2 : 'GENE'}, inplace = True)
# clean up gene column
gtf_split['GENE'] = gtf_split['GENE'].str.replace('gene_name ', '')
gtf_split['GENE'] = gtf_split['GENE'].str.replace('"', '')
gtf_split['GENE'] = gtf_split['GENE'].str.replace(' ', '')
gtf_split_no_gene_name['GENE'] = gtf_split_no_gene_name['GENE'].str.replace('gene_name ', '')
gtf_split_no_gene_name['GENE'] = gtf_split_no_gene_name['GENE'].str.replace('"', '')
gtf_split_no_gene_name['GENE'] = gtf_split_no_gene_name['GENE'].str.replace(' ', '')
gtf_split_no_gene_name['GENE'] = gtf_split_no_gene_name['GENE'].replace(['gene_sourceensembl',
                                                                            'gene_sourceensembl_havana',
                                                                            'gene_sourcehavana',
                                                                            'gene_sourcehavana_tagene',
                                                                            'gene_sourcemirbase'], np.nan)

# clean up ensembl ID column
gtf_split['ENS_ID'] = gtf_split['ENS_ID'].str.replace('gene_id ', '')
gtf_split['ENS_ID'] = gtf_split['ENS_ID'].str.replace('"', '')
gtf_split['ENS_ID'] = gtf_split['ENS_ID'].str.replace(' ', '')
gtf_split_no_gene_name['ENS_ID'] = gtf_split_no_gene_name['ENS_ID'].str.replace('gene_id ', '')
gtf_split_no_gene_name['ENS_ID'] = gtf_split_no_gene_name['ENS_ID'].str.replace('"', '')
gtf_split_no_gene_name['ENS_ID'] = gtf_split_no_gene_name['ENS_ID'].str.replace(' ', '')

# filter ref df
# drop predicted
ref_no_pred = ref[~ref['db_name'].str.contains('predicted')]
# subset and get unique genes
ref_sub = ref_no_pred[['gene_stable_id']]
ref_sub.drop_duplicates(inplace = True)

# filter gtf to autosomes
gtf_autosomes = gtf_split[~gtf_split['CHR'].str.contains('|'.join(['KI', 'MT', 'GL', 'X', 'Y']))]
gtf_autosomes_no_gene_name = gtf_split_no_gene_name[~gtf_split_no_gene_name['CHR'].str.contains('|'.join(['KI', 'MT', 'GL', 'X', 'Y']))]
gtf_all = gtf_split[~gtf_split['CHR'].str.contains('|'.join(['KI', 'GL']))]

# only keep refseq genes
gtf_ref = gtf_autosomes[gtf_autosomes['ENS_ID'].isin(ref_sub['gene_stable_id'])]
gtf_ref_all = gtf_all[gtf_all['ENS_ID'].isin(ref_sub['gene_stable_id'])]

# add 500kb upstream and downstream
gtf_ref['START_500kb_upstream'] = gtf_ref['START'] - 500000
gtf_ref['STOP_500kb_downstream'] = gtf_ref['STOP'] + 500000

gtf_ref_all['START_500kb_upstream'] = gtf_ref_all['START'] - 500000
gtf_ref_all['STOP_500kb_downstream'] = gtf_ref_all['STOP'] + 500000

gtf_autosomes['START_500kb_upstream'] = gtf_autosomes['START'] - 500000
gtf_autosomes['STOP_500kb_downstream'] = gtf_autosomes['STOP'] + 500000

gtf_autosomes_no_gene_name['START_500kb_upstream'] = gtf_autosomes_no_gene_name['START'] - 500000
gtf_autosomes_no_gene_name['STOP_500kb_downstream'] = gtf_autosomes_no_gene_name['STOP'] + 500000

# export file
gtf_ref.to_csv((output_prefix + '.gene_start_stop.gene_name.autosomes.refseq.exp_validated.500kb_upstream_downstream.gtf.txt'), sep = '\t', index = None, na_rep = 'NaN')

gtf_ref_all.to_csv((output_prefix + '.gene_start_stop.gene_name.all_chr.refseq.exp_validated.500kb_upstream_downstream.gtf.txt'), sep = '\t', index = None, na_rep = 'NaN')

gtf_autosomes.to_csv((output_prefix + '.gene_start_stop.gene_name.autosomes.500kb_upstream_downstream.gtf.txt'), sep = '\t', index = None, na_rep = 'NaN')

gtf_autosomes_no_gene_name.to_csv((output_prefix + '.gene_start_stop.autosomes.500kb_upstream_downstream.gtf.txt'), sep = '\t', index = None, na_rep = 'NaN')

gtf_all.to_csv((output_prefix + '.gene_start_stop.gene_name.all_chr.500kb_upstream_downstream.gtf.txt'), sep = '\t', index = None, na_rep = 'NaN')