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
import matplotlib.ticker as ticker
import os
import subprocess
from functools import reduce
from io import StringIO
import argparse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys

def get_keyfile():
    return subprocess.run(
        ['git', 'rev-parse', '--show-toplevel'],
        stdout=subprocess.PIPE).stdout.decode('utf-8').rstrip() + "/key-files.txt"

here = os.path.dirname(os.path.abspath(__file__))
parser = argparse.ArgumentParser(
    description="Produce a history of the file length of the grammar."
)
parser.add_argument(
    "-d",
    "--date-limit",
    help="""The earliest time that is included.
    This can either be a simple date in YYYY-MM-DD format,
    or it could be a relative date in the form Nx,
    where x is m for month, w for week or d for day,
    and N is an integer.""")
parser.add_argument(
    "-v", "--verbose",
    help="Print debug information.",
    action="store_true")
parser.add_argument(
    "-y",
    "--ylimit",
    help="""Chop the y-axis.
    This cuts the y-axis at a point
    which helps exaggerate the change.""",
    action="store_true")
parser.add_argument(
    "-f", "--keyfile",
    help="""File that lists the key files.
    Filenames listed in this file will be added to the list of files to scan.
    By default, it is a file named "key-files.txt"
    in the root of the git repository.""",
    default=get_keyfile()
)
parser.add_argument(
    "files",
    help="""Select files to compare.""",
    nargs="*",
    default=[])
args = parser.parse_args()

def get_limit(refdate, limit_arg):
    if limit_arg.lower().endswith("d"):
        limit = refdate - timedelta(days=int(limit_arg[:-1]))
    elif limit_arg.lower().endswith("w"):
        limit = refdate - timedelta(days=int(limit_arg[:-1]) * 7)
    elif limit_arg.lower().endswith("m"):
        limit = refdate + relativedelta(months=-int(limit_arg[:-1]))
    else:
        limit = pandas.to_datetime(limit_arg)
    return limit

def get_stats(filenames):
    global parser
    if args.verbose:
        for i in filenames:
            print("{}: in  {}".format(parser.prog, i), file=sys.stderr)
    csv = subprocess.run([here + "/length-hist"] + filenames,
                         stdout=subprocess.PIPE).stdout.decode('utf-8')
    return pandas.read_csv(StringIO(csv))

def parse_data(dat):
    dat["date"] = pandas.to_datetime(dat["date"])
    dat.set_index("date", inplace=True)
    dat.sort_index(inplace=True)
    return dat

def plot_data(data, args):
    global parser
    axes = data.plot.area(figsize=(16,10), linewidth=0)
    axes.set_title("Growth of the Drsk grammar")
    axes.grid(which="both")
    axes.set_ylabel("Length, characters")
    axes.legend(loc="lower right")
    axes.text(0.02, 0.98,
              "Current standings:\n"
              + '\n'.join(str(data.iloc[-1]).split('\n')[:-1]),
              transform=axes.transAxes, family="monospace",
              verticalalignment="top")
    axes.get_yaxis().set_major_formatter(
        ticker.FuncFormatter(lambda x, p: '{:,}'.format(int(x))))

    if args.ylimit:
        axes.set_ylim(bottom=data.min().max() * 0.8)

    if args.date_limit:
        axes.set_xlim(left=get_limit(data.index.max(), args.date_limit))

    fig = axes.get_figure()
    out = os.getcwd() + "/history.svg"
    if args.verbose:
        print("{}: out {}".format(parser.prog, out), file=sys.stderr)
    fig.savefig(out)
    pyplot.close(fig)

if __name__ == "__main__":
    if args.keyfile:
        with open(args.keyfile) as f:
            keyfiles = [i for i in f.read().split("\n") if i]
    plot_data(parse_data(get_stats(args.files + keyfiles)), args)
