#!/usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas
import matplotlib.pyplot as pyplot
import os
import subprocess
from functools import reduce
from io import StringIO
import argparse
import re
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator, FuncFormatter)
import sys

def get_keyfile():
    return subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip() + "/out-files.txt"

here = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser(
    description="Produce a breakdown of the grammar by chapter."
)
parser.add_argument(
    "-v", "--verbose",
    help="Print debug information.",
    action="store_true")
parser.add_argument(
    "files",
    help="""Select files to compare.""",
    nargs="*",
    default=[])
parser.add_argument(
    "-f", "--keyfile",
    help="""Key file. By default, it is a file named "out-files.txt"
    in the root of the git repository.""",
    default=get_keyfile())
args = parser.parse_args()

def get_data(files):
    if args.verbose:
        for i in files:
            print("{}: in  {}".format(parser.prog, i), file=sys.stderr)
    return subprocess.run(["texcount", "-sub=chapter"] + files,
                          stdout=subprocess.PIPE).stdout.decode('utf-8')

def counters():
    part = 0
    chapter = 0
    nonchapter = -1
    appendix = -1

    def next_part():
        nonlocal part
        part += 1
        return part

    def next_chapter():
        nonlocal chapter
        chapter += 1
        return chapter

    def next_appendix():
        nonlocal appendix
        appendix += 1
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[appendix]

    def next_nonchapter():
        nonlocal nonchapter
        nonchapter += 1
        return "abcdefghijklmnopqrstuvwxyz"[nonchapter]

    return (next_part, next_chapter, next_appendix, next_nonchapter)

def parse_data(guff):
    pt, ch, ap, nc = counters()
    splitter = re.compile(r"([0-9]+)\+([0-9]+)\+([0-9]+)")

    dat = []
    for line in guff.splitlines():
        if "Part" in line:
            part = pt()
        elif "Chapter" in line:
            separated = splitter.search(line)
            dat.append({
                "part": part,
                "chapter": (nc() if part in [1, 12]
                            else ap() if part in [10, 11]
                            else ch()),
                "name": line[line.find(":") + 1:],
                "text": int(separated.group(1).strip()),
                "headers": int(separated.group(2).strip()),
                "captions": int(separated.group(3).strip()),
            })
    return dat

def plot_data(data):
    global args
    global parser
    dat = pandas.DataFrame(data).set_index(["part", "chapter"], drop=False)
    dat.sort_index(inplace=True)
    dat.drop("chapter", inplace=True, axis=1)
    dat["net"] = dat["text"] + dat["captions"]
    colours = pyplot.rcParams['axes.prop_cycle'].by_key()['color']
    axes = dat.plot.bar(y="net",
                        color=[colours[i] for i in list((dat["part"] - 1) % len(colours))],
                        figsize=(16, 10),
                        width=1)
    axes.yaxis.set_major_locator(MultipleLocator(2000))
    axes.yaxis.set_major_formatter(
        FuncFormatter(lambda x,p: '{:,.0f}'.format(x)))
    axes.yaxis.set_minor_locator(MultipleLocator(500))
    axes.grid(True, axis="y", which="both")
    axes.set_ylabel("Length, words")
    axes.get_legend().remove()
    axes.set_title("Length of the Drsk grammar by chapter")
    axes.axvspan(-0.5, 1.5, alpha=0.2, color="#000000", zorder=-999)
    axes.axvspan(36.5, 45.5, alpha=0.2, color="#000000", zorder=-999)
    fig = axes.get_figure()
    out = os.getcwd() + "/chapter-lengths.svg"
    if args.verbose:
        print("{}: out {}".format(parser.prog, out))
    fig.savefig(out)
    pyplot.close(fig)

if __name__ == "__main__":
    if args.keyfile:
        with open(args.keyfile) as f:
            keyfiles = [i for i in f.read().split("\n") if i]
    plot_data(
        parse_data(
            get_data(
                args.files + keyfiles)))
