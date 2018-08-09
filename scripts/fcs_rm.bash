#!/bin/bash

shopt -s expand_aliases
source ~/.bashrc

set -eu

FCS_FILE=${1?'please provide a file with rundirs'}

TMP_RUNNING_JOBS=$(mktemp)
myjobinfo > ${TMP_RUNNING_JOBS}

while read RUN; do
    echo ${RUN}
    IFS=_ read -ra RUN_PARTS <<< "${RUN}"
    unset $IFS

    FC=${RUN_PARTS[3]}
    FC=${FC:1}
    samples=$(cgstats samples --flowcell ${FC})

    DELETE=1
    for sample in ${samples[@]}; do
        if grep -qs ${sample} ${TMP_RUNNING_JOBS}; then
            echo "${sample} RUNNING"
            DELETE=0
            break
        fi
    done

    if [[ $DELETE == 1 ]]; then
        rm -rf /mnt/hds/proj/bioinfo/DEMUX/${RUN}/Unaligned*/
        rm -rf /mnt/hds/proj/bioinfo/DEMUX/${RUN}/l?t??/
    fi

    cg set flowcell ${FC} --status removed
done < ${FCS_FILE}
