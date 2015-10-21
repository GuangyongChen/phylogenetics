#!/usr/bin/env python

# ----------------------------------------------------
# Simple script for running a reverse blast against an
# organism name
# ----------------------------------------------------

import os, glob, argparse
from phylogenetics.base import Homolog, HomologSet
from phylogenetics.blast import to_homologset

def main():
    """
        Run reverse blast.
    """
    # Build arguments and grab arguments
    parser = argparse.ArgumentParser(description="""
    Take XML files in the current directory and turn them into a Homolog object
    """)

    parser.add_argument("extension", help="File extension for all blast results to grab", dtype=str)
    parser.add_argument("output", help="Output filename, no extension. Will return .pickle", dtype=str)
    args = parser.parse_args()

    # get the blast result files in current directory
    cwd = os.getcwd()
    path = os.path.join(cwd, "*", args.extension)
    files = glob.glob(path)

    # Convert to homologset
    hs = to_homologset(files)
    hs.write(args.output + ".pickle", format="pickle")

if __name__ == "__main__":
    main()
