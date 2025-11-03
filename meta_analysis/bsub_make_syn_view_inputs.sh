#!/bin/bash

# BSUB parameters
######################################################################

#BSUB -J syn_view_inputs[1-4]
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
# of the current sub-job

#BSUB -o logs/syn_view_inputs.%J.%I.out 
# Filename to append the job's stdout; change to -oo to overwrite.
#'%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -e logs/syn_view_inputs.%J.%I.err
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
GENE=(
        'PDE8B'
        'PDE10A'
        'PTCSC2'
        'ATP5MGP4'
)

# Get the index of the current job
INDEX=$((LSB_JOBINDEX-1))

# Define parallelization variable indices
GENE_INDEX=${GENE[$INDEX]}

# load/unload modules
module unload python
module load python

# define sumstats dir
SUMSTATS_DIR='output'
VEP_DIR='vep_output'

# command
python make_syn_view_inputs.py \
--sumstats_list ${SUMSTATS_DIR}/AFR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.cleaned.txt,${SUMSTATS_DIR}/EUR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.cleaned.txt \
--vep_list ${VEP_DIR}/AFR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.vep_output.cleaned.txt,${VEP_DIR}/EUR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.vep_output.cleaned.txt \
--beta_col_list AFR:es,EUR:es \
--pval_col_list AFR:pval,EUR:pval \
--pval_thres 5e-8 \
--pval_colname PVALUE_RE \
--beta_colname BETA_RE \
--id_colname RSID \
--chr_colname CHR \
--pos_colname BP \
--gene ${GENE_INDEX} \
--output_prefix synthesis_view/TSH.5_inputs.metasoft.${GENE_INDEX}