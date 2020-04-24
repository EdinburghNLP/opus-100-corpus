#!/usr/bin/env bash

source common.sh

orig_wd=`pwd`

if [[ -d split ]]; then
    echo $0: split directory already exists - aborting 2>&1
    exit 1
fi

mkdir split

function split_pair {
    pair=$1
    x=`echo $pair | cut -d'-' -f 1`
    y=`echo $pair | cut -d'-' -f 2`
    cd $pair
    in_base=opus.$pair
    if [[ ! -f $in_base.$x ]]; then
        echo $in_base.$x not found
        cd ..
        return
    fi
    out_dir="$orig_wd/split/$pair"
    mkdir -p $out_dir
    # Split corpus - will skip if corpus is too small
    $orig_wd/split.py \
        $in_base \
        $x \
        $y \
        $out_dir/opus.$pair \
        $orig_wd/split/banned-from-devtest.txt \
        $orig_wd/split/banned-from-training.txt
    # Remove $out_dir if it's empty (corpus was too small)
    rmdir --ignore-fail-on-non-empty $out_dir
    cd ..
}

touch split/banned-from-devtest.txt
touch split/banned-from-training.txt

cd shuffled

# English-centric language pairs
for tgt in $tgt_langs; do
    split_pair `opus_pair_name en $tgt`
done

# Zero-shot language pairs
for src in $zero_shot_langs; do
    for tgt in $zero_shot_langs; do
        if [[ $src != $tgt ]]; then
            split_pair `opus_pair_name $src $tgt`
        fi
    done
done
