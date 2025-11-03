# load packages
import pandas as pd
import argparse as ap
from datetime import datetime

# define arguments
def make_arg_parser():
    parser = ap.ArgumentParser(description = '.')
    # sumstats file name
    parser.add_argument('--sumstats', required = True, help = 'sumstats input file')
    # chr column name
    parser.add_argument('--chr_colname', required = True, help = 'chromosome column name in sumstats')
    # pos column name
    parser.add_argument('--pos_colname', required = True, help = 'position column name in sumstats')
    # id column name
    parser.add_argument('--id_colname', required = True, help = 'variant ID column name in sumstate')
    # ref column name
    parser.add_argument('--ref_colname', required = True, help = 'ref allele column name in sumstats')
    # alt column name
    parser.add_argument('--alt_colname', required = True, help = 'alt allele column name in sumstats')
    # input type
    parser.add_argument('--input_type', required = True, choices = ['gwas', 'meta'], help = 'input file type')
    # output prefix
    parser.add_argument('--output_prefix', required = True, help = 'output prefix')

    return parser

args = make_arg_parser().parse_args()

# convert args to variables
sumstats_filepath = args.sumstats
chr_colname = args.chr_colname
pos_colname = args.pos_colname
id_colname = args.id_colname
ref_colname = args.ref_colname
alt_colname = args.alt_colname
input_type = args.input_type
output_prefix = args.output_prefix

# read in input file
sumstats = pd.read_csv(sumstats_filepath, sep = '\t')

# remove variants in one study if meta
if input_type == 'meta':
    print('input type is meta')
    sumstats = sumstats[sumstats['#STUDY'] > 1]

# subset columns
sumstats_sub = sumstats[[chr_colname, pos_colname, id_colname, ref_colname, alt_colname]]

# rename columns
sumstats_sub.rename(columns={chr_colname : '#CHROM',
                                pos_colname : 'POS',
                                id_colname : 'ID',
                                ref_colname : 'REF',
                                alt_colname : 'ALT'} ,inplace = True)

# sort
sumstats_sub.sort_values(by = ['#CHROM', 'POS'], inplace = True)

# add extra columns
sumstats_sub['QUAL'] = '.'
sumstats_sub['FILTER'] = '.'
sumstats_sub['INFO'] = '.'
sumstats_sub['FORMAT'] = '.'

# export file with comment
output_filepath = output_prefix + '.vcf'
with open(output_filepath, 'w') as f:
    f.write('##fileformat=VCFv4.2\n')
    f.write('##fileDate=' + str(datetime.today().date()) + '\n')
    f.write('##made by Katie Cardone for VEP annotations\n')
    sumstats_sub.to_csv(f, sep = '\t', index = False)