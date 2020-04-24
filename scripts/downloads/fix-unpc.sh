#!/usr/bin/env bash

for pair_dir in ??-??; do
    x=`echo $pair_dir | cut -d'-' -f 1`
    y=`echo $pair_dir | cut -d'-' -f 2`
    cd $pair_dir
    for name in UNPC; do
        if [[ ! -d $name ]]; then
            continue
        fi
        cd $name
        versions=`ls -d v*`
        for version in $versions; do
            cd $version
            mkdir tmp
            mv UNPC.$pair_dir.?? tmp
            cp tmp/UNPC.$pair_dir.$x UNPC.$pair_dir.$y
            cp tmp/UNPC.$pair_dir.$y UNPC.$pair_dir.$x
            cd ..
        done
        cd ..
    done
    cd ..
done
