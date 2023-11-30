###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import json
import sys
from pprint import pprint

import pytest

from solver import main


def test_main(tmp_path, capsys):  # Added capsys parameter
    instance = {
        "problem": {
            "type": "mis",
            "meta": {"params": {"L": 2}},
            "edges": [
                {"ids": [0, 1]},
                {"ids": [0, 2]},
                {"ids": [1, 2]},
                {"ids": [2, 3]},
                {"ids": [2, 4]},
                {"ids": [3, 4]},
            ],
        }
    }
    instance_file = tmp_path / "instance.json"
    with open(instance_file, "w") as f:
        json.dump(instance, f)

    # Call the main function with the instance file as argument
    sys.argv = ["solver.py", str(instance_file)]
    main(sys.argv)

    # Check that the output is correct
    captured = capsys.readouterr()
    assert "file: {}\n".format(instance_file) in captured.out
    print(captured)
    assert "|mis|=2\n" in captured.out
    assert "degeneracy=4\n" in captured.out
    assert "solutions:\n" in captured.out
    assert "[0, 4]\n" in captured.out
    assert "[1, 3]\n" in captured.out
