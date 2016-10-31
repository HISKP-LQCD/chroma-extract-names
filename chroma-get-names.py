#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import itertools
import pprint
import re
import os
import subprocess

git_grep_pattern = re.compile(r'([^:]+):\s*const std::string name.*"([^"]+)".*;')


def main():
    options = _parse_args()

    lines = subprocess.check_output(['git', 'grep', 'const std::string name']).decode().strip().split('\n')

    data = {}

    for line in lines:
        m = git_grep_pattern.search(line)
        if m:
            path = m.group(1)
            name = m.group(2)
            bits = os.path.dirname(path).split('/')

            enter(data, bits, name)

    pp = pprint.PrettyPrinter()
    pp.pprint(data)

    format_as_dot(data)



def enter(data, bits, name):
    it = data
    for i, bit in zip(itertools.count(), bits):
        is_leaf = i == len(bits) - 1
        if not bit in it:
            if is_leaf:
                print(bits, bit)
                it[bit] = []
            else:
                it[bit] = {}

        if is_leaf:
            try:
                it[bit].append(name)
            except AttributeError as e:
                print(bits)
                print(name)
                raise
        else:
            it = it[bit]


def format_as_dot(data):
    with open('chroma-names.dot', 'w') as f:
        f.write('''digraph {
            rankdir = LR;
            ''')
        f.write('\n'.join(_format_as_dot(data)))
        f.write('\n}')


def get_prefix_key(prefix, key):
    return prefix + '-' + key


def unique(data):
    return list(set(data))


def _format_as_dot(subtree, prefix=''):
    lines = []
    for key, vals in sorted(subtree.items()):
        prefix_key = get_prefix_key(prefix, key)
        lines.append('"{}" [label="{}"];'.format(prefix_key, key))
        if isinstance(vals, dict):
            for val in sorted(vals.keys()):
                lines.append('"{}" -> "{}";'.format(prefix_key, get_prefix_key(prefix_key, val)))

            lines += _format_as_dot(vals, prefix_key)
        elif isinstance(vals, list):
            for val in sorted(unique(vals)):
                lines.append('"{}" [shape=box, label="{}"];'.format(get_prefix_key(prefix_key, val), val))
                lines.append('"{}" -> "{}";'.format(prefix_key, get_prefix_key(prefix_key, val)))

    return lines



def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
