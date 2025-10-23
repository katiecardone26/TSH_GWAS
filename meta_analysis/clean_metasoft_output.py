# load packages
import pandas as pd
import argparse as ap

# define arguments
def make_arg_parser():
    parser = ap.ArgumentParser(description = ".")

    parser.add_argument('--input', required = True, help = 'input file')

    parser.add_argument('--output_prefix', required = True, help = 'output prefix')

    return parser

args = make_arg_parser().parse_args()

# parse arguments
input_file = args.input
output_prefix = args.output_prefix

# read in input files
input = pd.read_csv(input_file, sep = '\t', usecols = list(range(0, 16)))

# add new columns
input[['CHR', 'BP', 'REF', 'ALT']] = input['RSID'].astype(str).str.split(":", expand = True)
input['CHR'] = input['CHR'].str.replace('chr', '')

# create output file
output_file = output_prefix + '.txt'

# export files
input.to_csv(output_file, sep = '\t', na_rep = 'NA', index = None)