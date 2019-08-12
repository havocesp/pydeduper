#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pprint import pprint
from typing import List
from pathlib import Path
from argparse import ArgumentParser
import mimetypes
# import sh
# from zlib import crc32
from filecmp import cmp, clear_cache, dircmp
from zlib import crc32

UNITS = ['bytes', 'KB', 'MB', 'GB', 'TB']

def get_human_filesize(f):
    unit = UNITS[0]
    size = f[0]
    if f[0] > 1024:
        for n_exp, unit in enumerate(UNITS):
            prev_size = f[0] // (1024 ** n_exp + 1)
            if prev_size <= 1.0:
                unit = UNITS[UNITS.index(unit) - 1]
                break
            size = prev_size

    return f'{size} {unit}'

def is_hidden(path) -> bool:
    return any(e.startswith('.') for e in path.parts)

def main(args):
    # extract al absolute paths of directories supplied as arguments
    paths = [Path(p).resolve() for p in args.path if Path(p).is_dir()]

    files = list()

    if args.verbose:
        print(paths)

    # extract size and Path as tuple
    for path in paths:
        files.extend([(e.stat().st_size, e) for e in path.rglob('*') if e.is_file() and not is_hidden(e)])

    # sort all files by size
    files = sorted(files, key=lambda o: o[0])

    if args.verbose:
        print("\n".join([f"{f[0]:12d}:{f[1]}" for f in files]))

    for f1, f2 in zip(files, files[1:]):

        # if both files size match's may be a duplicate case
        if f1[0] == f2[0]:
            # nn, ns, nf = files[n + 1]
            print(f' - "{f1[1]}" - "{f2[1]}": ', end=' ')
            # the second test to known if are duplicate files is to calculate crc32 hash and compare it
            hash1 = crc32(f1[1].read_bytes())
            hash2 = crc32(f2[1].read_bytes())
            if args.verbose:
                print(f'{hash1} -> {hash2}')

            # if hash's match's also 98% of possibilities of duplication case
            if hash1 == hash2:
                human_size = get_human_filesize(f1)

                print(f' - BORRADO ({human_size}): {f1[1]}')
                if not args.dry:
                    if not args.confirm or input(f' - Remove file "{f1[1]}" (y/n): ') == 'y':
                        f1[1].unlink()


if __name__ == '__main__':
    sys.argv.extend(['--dry', '--confirm', '/media/godmin/Trastero/videos/tripleequis/videos'])
    # sys.argv.extend(['-p', str(Path.home().joinpath('Backups', 'videos'))])
    parser = ArgumentParser()
    parser.add_argument('path', metavar='PATH', default=Path.cwd(), nargs='+', help='File or directory path where search for duplicates.')
    parser.add_argument('--dry', action='store_true', help='No actually delete any files.')
    parser.add_argument('--verbose', action='store_true', help='Give more operation details.')
    parser.add_argument('--hidden', action='store_true', help='Include hidden files.')
    parser.add_argument('--confirm', action='store_true', help='Request confirmation before remove any file.')
    args = parser.parse_args()

    main(args)
