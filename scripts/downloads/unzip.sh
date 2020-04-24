#!/usr/bin/env bash

for pair_dir in ??-??; do
    cd $pair_dir
    for name in *; do
        if [[ ! -d $name ]]; then
            continue
        fi
        cd $name
        versions=`ls -d v*`
        for version in $versions; do
            cd $version
            for zip_file in *zip; do
                unzip -o $zip_file > stdout-unzip.txt 2> stderr-unzip.txt
            done
            cd ..
        done
        cd ..
    done
    cd ..
done
