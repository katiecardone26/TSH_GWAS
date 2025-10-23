#!/bin/bash

# BSUB parameters
######################################################################

#BSUB -J combine_outputs[1-8]
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

#BSUB -o logs/combine_outputs.%J.%I.stdout 
# Filename to append the job's stdout; change to -oo to overwrite.
#'%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -e logs/combine_outputs.%J.%I.stderr 
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
## ancestry
ANCESTRY=(
    "AFR"
    "AFR"
    "AFR"
    "AFR"
    "EUR"
    "EUR"
    "EUR"
    "EUR"
)

## correction
CORRECTION=(
    "no_correction"
    "no_correction"
    "adjusted_se"
    "adjusted_se"
    "no_correction"
    "no_correction"
    "adjusted_se"
    "adjusted_se"
)

## variant
VARIANTS=(
    "intersect"
    "union"
    "intersect"
    "union"
    "intersect"
    "union"
    "intersect"
    "union"
)

# Get the index of the current job
INDEX=$((LSB_JOBINDEX-1))

# Define parallelization variable indices
## ancestry
ANCESTRY_INDEX=${ANCESTRY[$INDEX]}
## correction
CORRECTION_INDEX=${CORRECTION[$INDEX]}
## variant
VARIANTS_INDEX=${VARIANTS[$INDEX]}

# Call Rscript
Rscript combine_outputs.R \
--uncorrected_input output/${ANCESTRY_INDEX}.INV_NORM_TSH.3_inputs.${CORRECTION_INDEX}.${VARIANTS_INDEX}.metasoft_output.no_mean_hetero_correction.txt_cleaned \
--corrected_input output/${ANCESTRY_INDEX}.INV_NORM_TSH.3_inputs.${CORRECTION_INDEX}.${VARIANTS_INDEX}.metasoft_output.mean_hetero_correction.txt_cleaned \
--output combined_outputs/${ANCESTRY_INDEX}.INV_NORM_TSH.3_inputs.${CORRECTION_INDEX}.${VARIANTS_INDEX}.metasoft_output_combined.txt \

