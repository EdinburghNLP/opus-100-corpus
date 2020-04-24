#!/usr/bin/env bash

source ../common.sh

orig_wd=`pwd`

function get_pair {
    x=$1
    y=$2
    if [[ $x == $y ]]; then 
        return
    fi
    pair_name=`opus_pair_name $x $y`
    if [[ -d $pair_name ]]; then
        return
    fi
    mkdir $pair_name
    cd $pair_name
    # Query the OPUS API to determine the available corpora for this pair
    wget "http://opus.nlpl.eu/opusapi/?source=$x&target=$y&preprocessing=moses" -O response.json
    corpora=`$orig_wd/list-corpora.py < response.json`
    for corpus in $corpora; do
        mkdir $corpus
        cd $corpus
        versions=`$orig_wd/list-versions.py $corpus < ../response.json`
        for version in $versions; do
            mkdir $version
            cd $version
            urls=`$orig_wd/list-urls.py $corpus $version < ../../response.json`
            wget $urls > stdout-wget.txt 2> stderr-wget.txt
            cd ..
        done
        cd ..
    done
    cd ..
}

# Supervised language pairs
for tgt in $tgt_langs; do
    get_pair en $tgt
done

# Zero-shot language pairs
for src in $zero_shot_langs; do
    for tgt in $zero_shot_langs; do
        get_pair $src $tgt
    done
done
