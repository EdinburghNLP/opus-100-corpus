#!/usr/bin/env python

import json
import sys

corpus = sys.argv[1]

response = json.load(sys.stdin)

versions = set()
for corpus_version in response['corpora']:
    if corpus_version['corpus'] == corpus:
        versions.add(corpus_version['version'])

for version in sorted(versions):
    print version
