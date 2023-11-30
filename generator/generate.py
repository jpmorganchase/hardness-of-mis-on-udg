###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################

"""generate.py: Command line interface for the MIS generator."""

__author__ = "Ruben S. Andrist"
__email__ = "randrist@amazon.com"

import argparse
import os
import sys

from generator import Generator


def main():
    parser = argparse.ArgumentParser(
        prog="generator.py",
        description="Generate unweighted MIS instances on Union Jack lattices",
    )

    parser.add_argument("-L", type=int, required=True, help="The size of the lattice")
    parser.add_argument(
        "-d",
        "--density",
        type=float,
        default=0.8,
        help="Portion of the sites that are occupied (default = 0.8)",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        required=False,
        help="The specific seed to generate (uses a random one if not specified)",
    )
    parser.add_argument(
        "-r",
        "--radius",
        default=2 ** 0.5,
        type=float,
        help="Radius of interaction. (default sqrt(2), i.e Union-Jack grid)",
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default=("instances" + os.sep + "L{L}"),
        help="Folder where the files should be stored (default: instances/L{L})",
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Generate all output formats (assumed if none selected).",
    )

    parser.add_argument(
        "-j", "--json", action="store_true", help="Edge list in json format."
    )
    parser.add_argument(
        "-m", "--metis", action="store_true", help="Adjacency list in metis 4.0 format."
    )
    parser.add_argument(
        "-g", "--svg", action="store_true", help="A vector rendering of the lattice."
    )
    parser.add_argument(
        "-c",
        "--cplex",
        action="store_true",
        help="A cplex lp formulation of the instance.",
    )
    parser.add_argument(
        "-p",
        "--pickle",
        action="store_true",
        help="Adjacency matrix in pickled format.",
    )
    parser.add_argument(
        "-e", "--edgelist", action="store_true", help="Edgelist in txt file: x0, x1"
    )

    parser.add_argument(
        "-n", "--dry", action="store_true", help="don't generate any files"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="show an ascii rendering on screen.",
    )

    args = parser.parse_args()
    if not (
        args.json
        or args.metis
        or args.svg
        or args.cplex
        or args.pickle
        or args.edgelist
    ):
        args.all = True

    instance = Generator(L=args.L, density=args.density, r=args.radius).generate(
        seed=args.seed, verbose=args.verbose or args.dry
    )

    if args.dry:
        sys.exit(0)

    folder = args.folder.format(L=args.L, d=args.density, s=args.seed, r=args.radius)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    path = os.path.join(folder, instance.name())

    if args.all or args.svg:
        with open(f"{path}.svg", "w") as fh:
            print(f"writing {path}.svg (rendering)")
            fh.write(instance.svg())

    if args.all or args.cplex:
        with open(f"{path}.lp", "w") as fh:
            print(f"writing {path}.lp (cplex format)")
            fh.write(instance.cplex())

    if args.all or args.metis:
        with open(f"{path}.txt", "w") as fh:
            print(f"writing {path}.txt (metis format)")
            fh.write(instance.metis())

    if args.all or args.json:
        with open(f"{path}.json", "w") as fh:
            print(f"writing {path}.json (json edge list)")
            fh.write(instance.json())

    if args.all or args.pickle:
        print(f"writing {path}.pkl (pickled adj-matrix)")
        instance.pickle(f"{path}.pkl")

    if args.all or args.edgelist:
        with open(f"{path}.edgelist", "w") as fh:
            print(f"writing {path}.edgelist (txt edge list)")
            fh.write(instance.edgelist())


if __name__ == "__main__":
    main()
