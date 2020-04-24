#!/usr/bin/env bash

source common.sh

orig_wd=`pwd`

if [[ -d merged ]]; then
    echo $0: merged directory already exists - aborting 2>&1
    exit 1
fi

mkdir merged

# Merge the corpora for the language pairs in downloads.
cd downloads
for pair in ??-??; do
    x=`echo $pair | cut -d'-' -f 1`
    y=`echo $pair | cut -d'-' -f 2`
    cd $pair
    out_dir="$orig_wd/merged/$pair"
    mkdir $out_dir
    cat */*/*.$pair.$x > $out_dir/opus.$pair.$x
    cat */*/*.$pair.$y > $out_dir/opus.$pair.$y
    cd ..
done
cd ..
