#!/bin/bash


DEMUX_DIR=${1?'please provide demux dir'}
CUTOFF_DATE=${2-2017-01-01}

# remove all unecessary //, including trailing
DEMUX_DIR=$(readlink -m ${DEMUX_DIR})

# find all fastq files that are older than certain date
# filter out the X FCs only
FASTQS=$(find ${DEMUX_DIR}/{*ALXX,*CCXX} -name *.fastq.gz ! -newermt ${CUTOFF_DATE})

# get the rundirs
RUN_DIRS=()
for FASTQ in ${FASTQS}; do
    # trailing slash has been removed from $DEMUX_DIR
    # remove it from the FASTQ path
    RUN_DIR=${FASTQ##${DEMUX_DIR}/}

    # keep the first part of the path
    # only works when there is no left over leading /
    RUN_DIR=${RUN_DIR%%/*}

    RUN_DIRS+=(${RUN_DIR})
done

# make RUN_DIRS uniq
UNIQ_RUN_DIRS=$(echo ${RUN_DIRS[@]} | tr ' ' '\n' | sort -u)

# print
for RUN_DIR in ${UNIQ_RUN_DIRS[@]}; do
    echo ${RUN_DIR}
done
