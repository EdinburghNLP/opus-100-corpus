#!/usr/bin/env python

import json
import sys

response = json.load(sys.stdin)

corpus_names = set()
for corpus_version in response['corpora']:
    corpus_names.add(corpus_version['corpus'])

for name in sorted(corpus_names):
    print name
