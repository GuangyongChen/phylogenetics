import argparse
from phylogenetics.utils import load_homologset
from phylogenetics.phyml import run_phyml
from phylogenetics.names import switch

def main():

    parser = argparse.ArgumentParser(description="""
    Build a tree from homologset via PhyML.
    """)

    parser.add_argument("-i", "--input", help="Input pickle file containing homologset.", type=str)
    parser.add_argument("-o", "--output", help="Output pickle filename. (No extension needed, returns .pickle)", type=str)
    parser.add_argument("--labels", help="List of tree labels", dtype=list, default=["id"])
    args = parser.parse_args()

    hs = load_homologset(args.input)
    hs2 = run_phyml(hs, args.output, dtype=args.dtype, rm_tmp=False)

    switch(args.output+".nwk",hs2, "id",labels)

    hs2.write(args.output + ".pickle", format="pickle")

if __name__ == "__main__":
    main()
