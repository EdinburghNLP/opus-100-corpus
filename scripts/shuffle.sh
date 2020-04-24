#!/usr/bin/env bash

orig_wd=`pwd`

if [[ -d shuffled ]]; then
    echo $0: shuffled directory already exists - aborting 2>&1
    exit 1
fi

mkdir shuffled

cd merged

for pair in ??-??; do
    x=`echo $pair | cut -d'-' -f 1`
    y=`echo $pair | cut -d'-' -f 2`
    cd $pair
    x_file=opus.$pair.$x
    y_file=opus.$pair.$y
    if [[ ! -f $x_file ]]; then
        echo $x_file not found
        cd ..
        continue
    fi
    if [[ ! -f $y_file ]]; then
        echo $y_file not found
        cd ..
        continue
    fi
    $orig_wd/shuffle.py $x_file $y_file
    out_dir="$orig_wd/shuffled/$pair"
    rm -rf $out_dir
    mkdir -p $out_dir
    mv $x_file.shuf $out_dir/$x_file
    mv $y_file.shuf $out_dir/$y_file
    cd ..
done
