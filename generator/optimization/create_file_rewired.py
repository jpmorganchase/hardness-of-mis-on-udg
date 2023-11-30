###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
from csv import writer
import os
import argparse


def main():
    """
    this function only creates an empty csv file the correct headings to populate everytime that we optimize an instance.
    """
    parser = argparse.ArgumentParser(
        prog="opt_result.py",
        description="",
    )

    parser.add_argument("-path", "--path_to_save", required=True, type=str, help="")

    args = parser.parse_args()

    with open(
        os.path.join("data", "cplex", args.path_to_save + ".csv"), "a"
    ) as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(
            [
                "L",
                "Density",
                "Seed",
                "UDG Radius",
                "Frac Rewired",
                "CPLEX TTO",
                "Process TTO",
                "Clock TTO",
                "CPLEX TTS",
                "Process TTS",
                "Clock TTS",
                "Solution",
            ]
        )
        f_object.close()


if __name__ == "__main__":
    main()
