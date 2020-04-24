#!/usr/bin/env bash

cd downloads
./get.sh > stdout-get.txt 2> stderr-get.txt
./unzip.sh > stdout-unzip.txt 2> stderr-unzip.txt
# When the OPUS-100 corpus was created the languages were flipped in the UNPC
# corpora downloard from OPUS. This now appears to have been fixed.
#./fix-unpc.sh > stdout-fix-unpc.txt 2> stderr-fix-unpc.txt
cd ../

./merge.sh > stdout-merge.txt 2> stderr-merge.txt
./shuffle.sh > stdout-shuffle.txt 2> stderr-shuffle.txt
./split.sh > stdout-split.txt 2> stderr-split.txt
