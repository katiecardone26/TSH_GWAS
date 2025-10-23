#!/bin/bash

# BSUB parameters
######################################################################

#BSUB -J smartpca[1-2]
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

#BSUB -o logs/smartpca.%J.%I.out 
# Filename to append the job's stdout; change to -oo to overwrite.
#'%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -e logs/smartpca.%J.%I.err
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

#BSUB -n 8
# Number of cores to reserve (on one or more hosts: ; see below).
# The variable $LSB_HOSTS lists allocated hosts like "hostA hostA hostB";
# the variable $LSB_MCPU_HOSTS lists allocated hosts like "hostA 2 hostB 1")

#-#BSUB -R "span[ptile=1]"
# Maximum number of cores to reserve on each host (for MPI).

#BSUB -R "select[ostype>=CENT7]"
# Require that the job runs on CentOS 7 host(s).

######################################################################

# define parallelization variables
OUTPUT_PREFIX=(
        'PMBB_v3.TSH.GWAS.EUR'
        'PMBB_v3.TSH.GWAS.AFR'
)

# Get the index of the current job
INDEX=$((LSB_JOBINDEX-1))

# Define parallelization variable indices
OUTPUT_PREFIX_INDEX=${OUTPUT_PREFIX[$INDEX]}

# create par file
genotypename="output/ld_prune/${OUTPUT_PREFIX_INDEX}.ld_prune.all_chr.eigenstratgeno"
snpname="output/ld_prune/${OUTPUT_PREFIX_INDEX}.ld_prune.all_chr.snp"
indivname="output/ld_prune/${OUTPUT_PREFIX_INDEX}.ld_prune.all_chr.ind"
evecoutname="output/pca/${OUTPUT_PREFIX_INDEX}.PCA.eigenvec"
evaloutname="output/pca/${OUTPUT_PREFIX_INDEX}.PCA.eigenval"
numoutevec="20"
numoutlieriter="0"
altnormstyle="NO"
fastmode="NO"
numthreads="8"

echo "genotypename:    $genotypename" > smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "snpname:         $snpname" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "indivname:       $indivname" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "evecoutname:     $evecoutname" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "evaloutname:     $evaloutname" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "numoutevec:      $numoutevec" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "numoutlieriter:  $numoutlieriter" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "altnormstyle:    $altnormstyle" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "fastmode:        $fastmode" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par
echo "numthreads:      $numthreads" >> smartPCA.${OUTPUT_PREFIX_INDEX}.par

# load modules
module purge
module load openblas
module load gsl
module load eigensoft

# command
smartpca -p smartPCA.${OUTPUT_PREFIX_INDEX}.par