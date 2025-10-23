# load packages
import pandas as pd
from manhattan_plot import ManhattanPlot
import argparse as ap

# define arguments
def make_arg_parser():
    parser = ap.ArgumentParser(description = ".")

    parser.add_argument('--annot_input', required = True, help = 'path to annotation filename')

    parser.add_argument('--sumstats_input', required = True, help = 'path to sumstats input filename')

    parser.add_argument('--title', required = True, help = 'title of plots')

    parser.add_argument('--subtitle', required = True, help = 'subtitle of plots')

    parser.add_argument('--annot_chr_col', required = True, help = 'chromosome column name in annotation file')

    parser.add_argument('--annot_pos_col', required = True, help = 'position column name in annotation file')

    parser.add_argument('--annot_id_col', required = True, help = 'ID column name in annotation file')

    parser.add_argument('--annot_gene_col', required = True, help = 'gene column name in annotation file')

    parser.add_argument('--sumstats_chr_col', required = True, help = 'chromosome column name in sumstats file')

    parser.add_argument('--sumstats_pos_col', required = True, help = 'position column name in sumstats file')

    parser.add_argument('--sumstats_id_col', required = True, help = 'ID column name in sumstats file')

    parser.add_argument('--sumstats_pval_col', required = True, help = 'pval column name in sumstats file')

    parser.add_argument('--known_genes', required = True, help = 'path to file with list of known genes')

    parser.add_argument('--sig', required = True, help = 'significance threshold')

    parser.add_argument('--sug', required = True, help = 'suggestive threshold')

    parser.add_argument('--annot', required = True, help = 'annotation threshold')

    parser.add_argument('--plot_sig', required = True, help = 'whether to annotate significant genes (True) or suggestive genes (False)')

    parser.add_argument('--invert', required = True, help = 'whether to invert (True) or not invert (False) the plot')

    parser.add_argument('--vert_table', required = True, help = 'whether to plot table in vertical manhattan plot')

    parser.add_argument('--vert_merge_signal', required = True, help = 'whether to merge signals in vertical manhattan plot')

    parser.add_argument('--vert_chr_pos', required = True, help = 'whether to include chromosome and position in vertical manhattan plot table')

    parser.add_argument('--horiz_table', required = True, help = 'whether to plot table in horizontal manhattan plot')

    parser.add_argument('--horiz_merge_signal', required = True, help = 'whether to merge signals in horizontal manhattan plot')

    parser.add_argument('--horiz_chr_pos', required = True, help = 'whether to include chromosome and position in horizontal manhattan plot')

    parser.add_argument('--output_prefix', required = True, help = 'output prefix')

    return parser

args = make_arg_parser().parse_args()

# make argument variables
annot_input_filename = args.annot_input
sumstats_input_filename = args.sumstats_input
known_genes_filename = args.known_genes

plot_title = args.title
plot_subtitle = args.subtitle

sumstats_chr_col = args.sumstats_chr_col
sumstats_pos_col = args.sumstats_pos_col
sumstats_id_col = args.sumstats_id_col
sumstats_pval_col = args.sumstats_pval_col

annot_chr_col = args.annot_chr_col
annot_pos_col = args.annot_pos_col
annot_id_col = args.annot_id_col
annot_gene_col = args.annot_gene_col

sig_thres = float(args.sig)
sug_thres = float(args.sug)
annot_thres = float(args.annot)
plot_sig_bool = eval(args.plot_sig)

vert_table_bool = eval(args.vert_table)
vert_merge_signal_bool = eval(args.vert_merge_signal)
vert_chr_pos_bool = eval(args.vert_chr_pos)
horiz_table_bool = eval(args.horiz_table)
horiz_merge_signal_bool = eval(args.horiz_merge_signal)
horiz_chr_pos_bool = eval(args.horiz_chr_pos)
invert_bool = eval(args.invert)

output_prefix = args.output_prefix

# annot df
## read in file
annotDF = pd.read_table(annot_input_filename)
## rename columns
annotDF = annotDF.rename(columns = {annot_id_col : 'VariantID',
                                    annot_gene_col : 'ID',
                                    annot_chr_col : '#CHROM',
                                    annot_pos_col : 'POS'})

# known genes
known_genes = open(known_genes_filename).read().splitlines()

# manhatann plotting package- load and clean data
mp = ManhattanPlot(file_path = sumstats_input_filename,
                    title = plot_title,
                    subtitle = plot_subtitle,
                    test_rows = None)
mp.load_data(delim = '\t')
mp.clean_data(col_map={sumstats_chr_col : '#CHROM',
                        sumstats_pos_col : 'POS',
                        sumstats_id_col : 'ID',
                        sumstats_pval_col : 'P'})
mp.add_annotations(annotDF, extra_cols = ['RSID'])
mp.get_thinned_data()

# QQ plot
## create output file
qq_output_filename = output_prefix + '.QQ_plot.png'
mp.qq_plot(save = qq_output_filename, save_res = 150)

# Vertical With Table
## create output file
vert_man_output_filename = output_prefix + '.vertical_manhattan_plot.png'
mp.update_plotting_parameters(sug = sug_thres,
                                annot_thresh = annot_thres,
                                sig = sig_thres,
                                ld_block = 4E5,
                                merge_genes = vert_merge_signal_bool,
                                invert = invert_bool)

mp.full_plot(rep_genes = known_genes,
                 plot_sig = plot_sig_bool,
                 with_table = vert_table_bool,
                 keep_chr_pos = vert_chr_pos_bool,
                 save_res = 150,
                 extra_cols = {'RSID': 'RSID'}, 
                 save = vert_man_output_filename)

# Horizontal Without Table
## create output file
horiz_man_output_filename = output_prefix + '.horizontal_manhattan_plot.png'
mp.update_plotting_parameters(sug = sug_thres,
                                annot_thresh = annot_thres,
                                sig = sig_thres,
                                merge_genes = horiz_merge_signal_bool,
                                ld_block = 4E5,
                                invert = invert_bool,
                                vertical = False)

mp.full_plot(rep_genes = known_genes,
                 plot_sig = plot_sig_bool,
                 rep_boost = False,
                 with_table = horiz_table_bool,
                 keep_chr_pos = horiz_chr_pos_bool,
                 save_res = 150,
                 save = horiz_man_output_filename)