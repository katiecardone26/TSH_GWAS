#!/bin/bash

# BSUB parameters
######################################################################

#BSUB -J make_plots
# Job name and (optional) job array properties, in the format
#   "jobname"
# for a simple job, or
#   "jobname[min-max:step]%limit"
# for an array job, where
#   'jobname' is the label shown in job status and summary displays
#   'min' is the first array index
#   'max' is the last array index
#   'step' is the step value between array indecies
#   'limit' is the number of array sub-jobs that can run at once
# In an array job, the variable $LSB_JOBINDEX will contain the index
# of the current sub-job.

#BSUB -o logs/make_plots.%J.%I.out 
# Filename to append the job's stdout; change to -oo to overwrite.
#'%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -e logs/make_plots.%J.%I.err 
# Filename to append the job's stderr; change to -eo to overwrite. 
# If omitted, stderr is combined with stdout. 
# '%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -R "span[hosts=1]"
# Require all cores to be on the same host (for multi-threaded, non-MPI).

#-#BSUB -B
# Send email notification when the job starts

#-#BSUB -N
# Send email notification when the job finishes; otherwise, summary is written to the output file

#BSUB -R "rusage[mem=200000]"
# Per-process memory reservation, in MB.
# (Ensures the job will have this minimum memory.)

#BSUB -M 200000
# Per-process memory limit, in MB.
# (Ensures the job will not exceed this maximum memory.)

#BSUB -v 200000
# Total process virtual (swap) memory limit, in MB.

#-#BSUB -W 24:00
# Wall time limit, in the format "hours:minutes".
#-#BSUB -n 1
# Number of cores to reserve (on one or more hosts: ; see below).
# The variable $LSB_HOSTS lists allocated hosts like "hostA hostA hostB";
# the variable $LSB_MCPU_HOSTS lists allocated hosts like "hostA 2 hostB 1")

#-#BSUB -R "span[ptile=1]"
# Maximum number of cores to reserve on each host (for MPI).

#BSUB -R "select[ostype>=CENT7]"
# Require that the job runs on CentOS 7 host(s).

######################################################################

# define parallelization variables
PREFIX=(
    "formatted_invnormTSH_overall_130421_invvar1.txt-QCfiltered_GC.clean.b38"
)

TITLE=(
    "EUR TSH Paper Results"
)

SUBTITLE=(
    "271040"
)

INVERT=(
    "True"
)
# Get the index of the current job
INDEX=$((LSB_JOBINDEX-1))

# Define parallelization variable indices
PREFIX_INDEX=${PREFIX[$INDEX]}
TITLE_INDEX=${TITLE[$INDEX]}
SUBTITLE_INDEX=${SUBTITLE[$INDEX]}
INVERT_INDEX=${INVERT[$INDEX]}

# script
python manhattan_plotting_script.py \
    --annot_input vep_output/${PREFIX_INDEX}.suggestive.merge_genes.vep_output.cleaned.txt \
    --sumstats_input ${PREFIX_INDEX}.txt.gz \
    --title "${TITLE_INDEX}" \
    --subtitle "n = ${SUBTITLE_INDEX}" \
    --sumstats_chr_col 'CHR' \
    --sumstats_pos_col POS \
    --sumstats_id_col rsid \
    --sumstats_pval_col P.value \
    --annot_chr_col CHR \
    --annot_pos_col POS \
    --annot_id_col ID \
    --annot_gene_col GENE \
    --known_genes INV_NORMAL_TSH.known_genes.txt \
    --sig 5e-25 \
    --sug 5e-25 \
    --annot 5e-25 \
    --vert_table True \
    --vert_merge_signal True \
    --vert_chr_pos False \
    --horiz_table True \
    --horiz_merge_signal False \
    --horiz_chr_pos False \
    --plot_sig True \
    --plot_sig True \
    --invert ${INVERT_INDEX} \
    --output_prefix plots/${PREFIX_INDEX}
