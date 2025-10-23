#!/bin/bash

# BSUB parameters
######################################################################

#BSUB -J merge_chunks[1-23]
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

#BSUB -o logs/merge_chunks.%J.%I.out 
# Filename to append the job's stdout; change to -oo to overwrite.
#'%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -e logs/merge_chunks.%J.%I.err
# Filename to append the job's stderr; change to -eo to overwrite. 
# If omitted, stderr is combined with stdout. 
# '%J' becomes the job ID number, '%I' becomes the array index.

#BSUB -R "span[hosts=1]"
# Require all cores to be on the same host (for multi-threaded, non-MPI).

#-#BSUB -B
# Send email notification when the job starts

#-#BSUB -N
# Send email notification when the job finishes; otherwise, summary is written to the output file

#BSUB -R "rusage[mem=25000]"
# Per-process memory reservation, in MB.
# (Ensures the job will have this minimum memory.)

#BSUB -M 25000
# Per-process memory limit, in MB.
# (Ensures the job will not exceed this maximum memory.)

#BSUB -v 25000
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

# get variables from input manifest file and LSB_JOBINDEX
input_manifest="imputed_variant_chunked_input_manifest.tsv"
read chrid chunk start_pos stop_pos < <(awk -v i="$LSB_JOBINDEX" '$1 == i {print $2, $3, $4, $5}' "$input_manifest")
plink2_prefix="chunked_pgen_files/PMBB-Release-2024-3.0_genetic_imputed.${chrid}_chunk${chunk}_${start_pos}_${stop_pos}"

# INFO LOG
echo "====== INPUT FILES ======"
printf "%-20s: %s\n" "input_manifest" "${input_manifest}"
printf "%-20s: %s\n" "LSB_JOBINDEX" "${LSB_JOBINDEX}"
printf "%-20s: %s\n" "chrid" "${chrid}"
printf "%-20s: %s\n" "chunk" "${chunk}"
printf "%-20s: %s\n" "start_pos" "${start_pos}"
printf "%-20s: %s\n" "stop_pos" "${stop_pos}"
printf "%-20s: %s\n" "plink2_prefix" "${plink2_prefix}"
echo "====== OUTPUT FILES ======"
# printf "%-20s: %s\n" "output_file" "${output_file}"
echo "====== OUTPUT FILES ======"

# make merge list
input_manifest="imputed_variant_chunked_input_manifest.tsv"
if [ "$LSB_JOBINDEX" -eq 23 ]; then
    chr_num="chrX"
else
    chr_num=chr${LSB_JOBINDEX}
fi
awk -v i="${chr_num}" '$2 == i {print $2, $3, $4, $5}' "$input_manifest" > merge_lists/file_components/${chr_num}.file_components.txt
awk '{print "chunked_pgen_files/PMBB-Release-2024-3.0_genetic_imputed."$1"_chunk"$2"_"$3"_"$4}' merge_lists/file_components/${chr_num}.file_components.txt > merge_lists/lists/${chr_num}.merge_list.txt

# your code here
plink2 --pmerge-list merge_lists/lists/${chr_num}.merge_list.txt \
--make-pgen \
--out input/merged_files/PMBB-Release-2024-3.0_genetic_imputed.${chr_num}

# SYNTAX TO SUBMIT JOB
# ---------------------------
# submit chromosome 22 chunk5
# bsub -hl -J "jobname[919]" < /path/to/this/script.bsub

# submit all chromosome 3 chunks
# bsub -hl -J "jobname[158-225]" < /path/to/this/script.bsub

# submit all chunks
# bsub -hl -J "jobname[1-980]" < /path/to/this/script.bsub # OR
# bsub -hl < /path/to/this/script.bsub # no need to define new jobname index range if using alå