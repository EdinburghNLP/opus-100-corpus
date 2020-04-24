#!/usr/bin/env python3

""" Splits a parallel corpus into train / dev / test / unused """

import argparse
import os
import random
import shutil
import sys
import tempfile


class SequentialSampler:
    """Samples sequential blocks of sentence pairs from a parallel corpus."""

    def __init__(self, src_file, tgt_file, sample_size):
        self._src_file = src_file
        self._tgt_file = tgt_file
        self._sample_size = sample_size

    def __iter__(self):
        with open(self._src_file) as src_fh, \
             open(self._tgt_file) as tgt_fh:
            i = 0
            done = False
            while not done:
                pairs, indices = [], []
                for j in range(self._sample_size):
                    src_line = src_fh.readline()
                    tgt_line = tgt_fh.readline()
                    if src_line == "":
                        done = True
                        break
                    pair = (src_line.strip(), tgt_line.strip())
                    pairs.append(pair)
                    indices.append(i)
                    i += 1
                yield pairs, indices


class Filter:
    """Filters a list of sentence pairs against a list of banned sentences.

    Assumes that either the set of banned sentences is small-ish or the set of
    candidates is small-ish. If both are very big then this will probably
    break...
    """

    def __init__(self, banned_file):
        # Determine the size of the banned file. If it's below a threshold size
        # then read it into a set and use that to check for matches. Otherwise,
        # check for matches by scanning the file.
        self._banned_file = banned_file
        self._threshold = 1000000
        too_big = False
        with open(self._banned_file) as fh:
            for i, line in enumerate(fh):
                if i == self._threshold:
                    too_big = True
                    break
        if too_big:
            self._banned_set = None
        else:
            self._banned_set = set()
            with open(self._banned_file) as fh:
                for line in fh:
                    self._banned_set.add(line.strip())

    def filter(self, pairs, indices):
        if self._banned_set is None:
            return self._filter_against_file(pairs, indices, self._banned_file)
        else:
            return self._filter_against_set(pairs, indices, self._banned_set)

    def _filter_against_set(self, pairs, indices, banned_set):
        filtered_pairs, filtered_indices = [], []
        for pair, index in zip(pairs, indices):
            if pair[0] in banned_set or pair[1] in banned_set:
                continue
            filtered_pairs.append(pair)
            filtered_indices.append(index)
        return filtered_pairs, filtered_indices

    def _filter_against_file(self, pairs, indices, banned_sents_file):
        # Record the indices of the candidate source / target sides.
        sent_to_candidate_indices = {}
        for i, pair in enumerate(pairs):
            source_sent, target_sent = pair[0], pair[1]
            sent_to_candidate_indices.setdefault(source_sent, [])
            sent_to_candidate_indices[source_sent].append(i)
            sent_to_candidate_indices.setdefault(target_sent, [])
            sent_to_candidate_indices[target_sent].append(i)
        # Check the candidate source / target sides against the list of banned
        # sentences. If any matches are found, record the indices of the pairs
        # containing the source / target side.
        banned = set()
        with open(banned_sents_file) as fh:
            for line in fh:
                sent = line.strip()
                if sent in sent_to_candidate_indices:
                    banned.update(sent_to_candidate_indices[sent])
        # Filter the list of candidate indices to remove the excluded pairs.
        filtered_pairs, filtered_indices = [], []
        for i, (pair, index) in enumerate(zip(pairs, indices)):
            if i not in banned:
                filtered_pairs.append(pair)
                filtered_indices.append(index)
        return filtered_pairs, filtered_indices


def warn(msg):
    sys.stderr.write("%s: warning: %s\n" % (sys.argv[0], msg.strip()))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('in_basename', type=str, metavar='NAME',
                        help='basename of input corpus')

    parser.add_argument('src', type=str, metavar='LANG',
                        help='language code for source language')

    parser.add_argument('tgt', type=str, metavar='LANG',
                        help='language code for target language')

    parser.add_argument('out_basename', type=str, metavar='NAME',
                        help='basename of output corpus')

    parser.add_argument('banned_from_devtest', type=str, metavar='PATH',
                        help='file containing sentences banned from dev/test')

    parser.add_argument('banned_from_training', type=str, metavar='PATH',
                        help='file containing sentences banned from training')

    parser.add_argument('--train-size', metavar='N', type=int, default=1000000,
                        help='size of training set in sentences')

    parser.add_argument('--dev-size', metavar='N', type=int, default=2000,
                        help='size of dev set in sentences')

    parser.add_argument('--test-size', metavar='N', type=int, default=2000,
                        help='size of test set in sentences')

    parser.add_argument('--threshold-size', metavar='N', type=int,
                        default=16000,
                        help='minimum number of sentences to split off dev / '
                             'test set (100% training otherwise)')

    parser.add_argument('--banned-sents', metavar='PATH', type=str,
                        help='file containing banned sentences')

    args = parser.parse_args()

    src_file = args.in_basename + "." + args.src
    tgt_file = args.in_basename + "." + args.tgt

    train_src = args.out_basename + "-train." + args.src
    train_tgt = args.out_basename + "-train." + args.tgt
    dev_src = args.out_basename + "-dev." + args.src
    dev_tgt = args.out_basename + "-dev." + args.tgt
    test_src = args.out_basename + "-test." + args.src
    test_tgt = args.out_basename + "-test." + args.tgt
    unused_src = args.out_basename + "-unused." + args.src
    unused_tgt = args.out_basename + "-unused." + args.tgt

    # Check corpus size. If it's too small to split then use 100% for training.
    corpus_size = 0
    with open(src_file) as f:
        for line in f:
            corpus_size += 1
    if corpus_size < args.threshold_size:
        warn('{}: below threshold size of {} - not creating dev/test'.format(
            args.in_basename, args.threshold_size))
        shutil.copyfile(src_file, train_src)
        shutil.copyfile(tgt_file, train_tgt)
        sys.exit(0)

    # Define the sampling + filtering function to use for dev/test and train.
    def sample_and_filter(sampler, filt, desired_size, out_fh):
        out_indices = []
        for pairs, indices in sampler:
            num_required = desired_size - len(out_indices)
            filtered_pairs, filtered_indices = filt.filter(pairs, indices)
            if len(filtered_pairs) > num_required:
                filtered_pairs = filtered_pairs[:num_required]
                filtered_indices = filtered_indices[:num_required]
            out_indices += filtered_indices
            for pair in filtered_pairs:
                print(pair[0], file=out_fh)
                print(pair[1], file=out_fh)
            assert len(out_indices) <= desired_size
            if len(out_indices) == desired_size:
                break
        return out_indices

    # Sample devtest sentence pairs.

    desired_size = args.dev_size + args.test_size
    sample_size = desired_size * 2
    sampler = SequentialSampler(src_file, tgt_file, sample_size)
    filt = Filter(args.banned_from_devtest)

    with open(args.banned_from_training, 'a') as banned_fh:
        devtest_indices = sample_and_filter(sampler, filt, desired_size,
                                            banned_fh)

    # Split indices into dev / test

    if len(devtest_indices) == desired_size:
        dev_indices = set(devtest_indices[0:args.dev_size])
        test_indices = set(devtest_indices[args.dev_size:])
    else:
        warn("fewer dev/test sentence pairs than requested after filtering")
        desired_dev_ratio = args.dev_size / desired_size
        adjusted_dev_size = int(len(devtest_indices) * desired_dev_ratio)
        dev_indices = set(devtest_indices[0:adjusted_dev_size])
        test_indices = set(devtest_indices[adjusted_dev_size:])
        warn("found {} dev sentence pairs (out of {})".format(
             len(dev_indices), args.dev_size))
        warn("found {} test sentence pairs (out of {})".format(
             len(test_indices), args.test_size))

    # Create a temporary directory for intermediate unused files.
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_unused_src = os.path.join(tmp_dir, 'unused_src')
        tmp_unused_tgt = os.path.join(tmp_dir, 'unused_tgt')

        # Write dev / test / intermediate unused files.

        write_files(src_file, tgt_file, [dev_indices, test_indices],
                    [[dev_src, dev_tgt], [test_src, test_tgt]],
                    tmp_unused_src, tmp_unused_tgt)

        # Sample training sentence pairs from intermediate unused files.

        desired_size = args.train_size
        sample_size = desired_size * 2
        sampler = SequentialSampler(tmp_unused_src, tmp_unused_tgt, sample_size)
        filt = Filter(args.banned_from_training)

        with open(args.banned_from_devtest, 'a') as banned_fh:
            train_indices = sample_and_filter(sampler, filt, desired_size,
                                              banned_fh)

        if len(train_indices) < desired_size:
            warn("fewer training sentence pairs than requested after filtering")
            warn("found {} training sentence pairs (out of {})".format(
             len(train_indices), args.train_size))

        # Write training and unused files.
        write_files(tmp_unused_src, tmp_unused_tgt, [train_indices],
                    [[train_src, train_tgt]], unused_src, unused_tgt)


def write_files(src_file, tgt_file, index_lists, out_file_pairs,
                unused_src, unused_tgt):
    assert len(index_lists) == len(out_file_pairs)

    index_sets = [set(index_list) for index_list in index_lists]
    out_fh_pairs = [(open(f1, "w"), open(f2, "w"))
                    for (f1, f2) in out_file_pairs]

    with open(src_file) as src_fh, \
         open(tgt_file) as tgt_fh, \
         open(unused_src, "w") as unused_src_fh, \
         open(unused_tgt, "w") as unused_tgt_fh:
        i = 0
        while True:
            src_line = src_fh.readline()
            tgt_line = tgt_fh.readline()
            if src_line == '':
                break
            unused = True
            for j, index_set in enumerate(index_sets):
                if i not in index_set:
                    continue
                print(src_line.strip(), file=out_fh_pairs[j][0])
                print(tgt_line.strip(), file=out_fh_pairs[j][1])
                unused = False
                break
            if unused:
                print(src_line.strip(), file=unused_src_fh)
                print(tgt_line.strip(), file=unused_tgt_fh)
            i += 1


if __name__ == '__main__':
    main()
