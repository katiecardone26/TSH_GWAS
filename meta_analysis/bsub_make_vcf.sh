#!/bin/bash

# BSUB parameters
######################################################################

#BSUB -J make_vcf[1-6]
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

#BSUB -o logs/make_vcf.%J.%I.out 
# Filename to append the job's stdout; change to -oo to overwrite.
#'%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -e logs/make_vcf.%J.%I.err 
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
## sumstats filepath
SUMSTATS=(
    "suggestive/AFR.INV_NORMAL_TSH.3_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive.txt"
    "suggestive/EUR.INV_NORMAL_TSH.3_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive.txt"
    "suggestive/AFR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive.txt"
    "suggestive/EUR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive.txt"
    "output/AFR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.cleaned.txt"
    "output/EUR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.cleaned.txt"
)

## output prefix
OUTPUT_PREFIX=(
    "AFR.INV_NORMAL_TSH.3_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive"
    "EUR.INV_NORMAL_TSH.3_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive"
    "AFR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive"
    "EUR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction.suggestive"
    "AFR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction"
    "EUR.INV_NORMAL_TSH.5_inputs.no_correction.union.metasoft_output.no_mean_hetero_correction"
)


# Get the index of the current job
INDEX=$((LSB_JOBINDEX-1))

# Define parallelization variable indices
## sumstats filepath
SUMSTATS_INDEX=${SUMSTATS[$INDEX]}
## output prefix
OUTPUT_PREFIX_INDEX=${OUTPUT_PREFIX[$INDEX]}

# call make vcf script
python make_vcf.py \
--sumstats ${SUMSTATS_INDEX} \
--chr_colname CHR \
--pos_colname BP \
--id_colname RSID \
--ref_colname REF \
--alt_colname ALT \
--input_type meta \
--output_prefix vcf/${OUTPUT_PREFIX_INDEX}