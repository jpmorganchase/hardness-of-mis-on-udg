###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################
import pytest
import os
import shutil
import sys
from io import StringIO
from generator import Generator
from generate import main


@pytest.fixture
def instance():
    return Generator(L=5, density=0.5, r=2 ** 0.5).generate(seed=42)


def test_main_help(capsys):
    with pytest.raises(SystemExit):
        sys.argv = ["generator.py", "-h"]
        main()
    captured = capsys.readouterr()
    assert "Generate unweighted MIS instances" in captured.out


def test_main_all_formats(instance, tmpdir):
    folder = os.path.join(tmpdir, f"instances{os.sep}L{instance.L}")
    sys.argv = [
        "generator.py",
        "-L",
        str(instance.L),
        "-d",
        str(instance.density),
        "-s",
        "42",
        "-r",
        str(instance.r),
        "-f",
        folder,
    ]
    main()
    assert os.path.isdir(folder)
    assert os.path.isfile(os.path.join(folder, instance.name() + ".svg"))
    assert os.path.isfile(os.path.join(folder, instance.name() + ".lp"))
    assert os.path.isfile(os.path.join(folder, instance.name() + ".txt"))
    assert os.path.isfile(os.path.join(folder, instance.name() + ".json"))
    assert os.path.isfile(os.path.join(folder, instance.name() + ".pkl"))
    assert os.path.isfile(os.path.join(folder, instance.name() + ".edgelist"))


def test_main_one_format(instance, tmpdir):
    folder = os.path.join(tmpdir, f"instances{os.sep}L{instance.L}")
    sys.argv = [
        "generator.py",
        "-L",
        str(instance.L),
        "-d",
        str(instance.density),
        "-s",
        "42",
        "-r",
        str(instance.r),
        "-g",
        "-f",
        folder,
    ]
    main()
    assert os.path.isdir(folder)
    assert os.path.isfile(os.path.join(folder, instance.name() + ".svg"))
    assert not os.path.isfile(os.path.join(folder, instance.name() + ".lp"))
    assert not os.path.isfile(os.path.join(folder, instance.name() + ".txt"))
    assert not os.path.isfile(os.path.join(folder, instance.name() + ".json"))
    assert not os.path.isfile(os.path.join(folder, instance.name() + ".pkl"))
    assert not os.path.isfile(os.path.join(folder, instance.name() + ".edgelist"))


def test_main_verbose(instance, capsys):
    ascii_fig = "\n o       o \n |       |\n o       o \n  \\     / \n   o   o   \n  /|\\ / \\ \n o-o-o   o \n |/"
    sys.argv = [
        "generator.py",
        "-L",
        str(instance.L),
        "-d",
        str(instance.density),
        "-s",
        "42",
        "-r",
        str(instance.r),
        "-v",
    ]
    main()
    captured = capsys.readouterr()
    assert ascii_fig in captured.out


def test_main_dry(instance, tmpdir):
    folder = os.path.join(tmpdir, f"instances{os.sep}L{instance.L}")
    sys.argv = [
        "generator.py",
        "-L",
        str(instance.L),
        "-d",
        str(instance.density),
        "-s",
        "42",
        "-r",
        str(instance.r),
        "-n",
    ]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 0
