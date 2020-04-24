#!/usr/bin/env python

import json
import sys

corpus, version = sys.argv[1], sys.argv[2]

response = json.load(sys.stdin)

# Note that corpus name and version don't always uniquely identify a zip
# file. e.g. for bg-en
#
#    {
#      "alignment_pairs": 224379,
#      "corpus": "EUbookshop",
#      "documents": 740,
#      "id": 10814,
#      "latest": "True",
#      "preprocessing": "moses",
#      "size": 6068,
#      "source": "bg",
#      "source_tokens": 10002514,
#      "target": "en",
#      "target_tokens": 12799301,
#      "url": "https://object.pouta.csc.fi/OPUS-EUbookshop/v2/moses/bg-en.strict.txt.zip",
#      "version": "v2"
#    },
#    {
#      "alignment_pairs": 224379,
#      "corpus": "EUbookshop",
#      "documents": 740,
#      "id": 10815,
#      "latest": "True",
#      "preprocessing": "moses",
#      "size": 21876,
#      "source": "bg",
#      "source_tokens": 10002514,
#      "target": "en",
#      "target_tokens": 12799301,
#      "url": "https://object.pouta.csc.fi/OPUS-EUbookshop/v2/moses/bg-en.txt.zip",
#      "version": "v2"
#    },

for corpus_version in response['corpora']:
    if (corpus_version['corpus'] == corpus
        and corpus_version['version'] == version):
        print corpus_version['url']
