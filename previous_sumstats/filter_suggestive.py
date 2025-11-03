# load packages
import pandas as pd
import argparse as ap
import sys

# define arguments
def make_arg_parser():
    parser = ap.ArgumentParser(description = ".")

    parser.add_argument('--input', required = True, help = 'input file')

    parser.add_argument('--input_type', required = True, choices = ['gwas', 'meta'], help = 'input file type')

    parser.add_argument('--pval_col', required = True, help = 'pval column name')

    parser.add_argument('--pval_threshold', required = True, type = float, help = 'pval threshold for filtering')

    parser.add_argument('--output_prefix', required = True, help = 'output prefix')

    return parser

args = make_arg_parser().parse_args()

# parse arguments
input_file = args.input
input_type = args.input_type
pval_column = args.pval_col
pval_threshold = args.pval_threshold
output_prefix = args.output_prefix

# read in input files
input = pd.read_csv(input_file, sep = '\t')

# clean inputs- filter to suggestive, and filter to intersections if filetype is meta
if input_type == 'gwas':
    print('input type is gwas')
    input_clean = input[input[pval_column] <= pval_threshold]
    print(len(input_clean.index))

elif input_type == 'meta':
    print('input type is meta')
    input_clean = input[input['#STUDY'] > 1]
    input_clean = input_clean[input_clean[pval_column] <= pval_threshold]
    print(len(input_clean.index))

else:
    sys.exit('input type is neither gwas or meta, check code')

# create output file path
output_file = output_prefix + '.suggestive.txt'

# export
input_clean.to_csv(output_file, sep = '\t', index = None)