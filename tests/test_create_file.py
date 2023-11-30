###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import os
import csv
import pytest
import sys
from create_file import main


def test_main():
    os.chdir("generator/")
    sys.argv = ["opt_result.py", "--path_to_save", "test"]
    main()
    expected_headers = [
        "L",
        "Density",
        "Seed",
        "UDG Radius",
        "CPLEX TTO",
        "Process TTO",
        "Clock TTO",
        "CPLEX TTS",
        "Process TTS",
        "Clock TTS",
        "Solution",
    ]
    # Assert
    with open("data/cplex/test.csv", "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        assert headers == expected_headers

    os.remove("data/cplex/test.csv")
    os.chdir("../")
