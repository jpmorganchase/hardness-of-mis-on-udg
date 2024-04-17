###############################################################################
# // SPDX-License-Identifier: Apache-2.0
# // Copyright 2023: Amazon Web Services, Inc
###############################################################################

"""solver.py: Solves unweighted MIS instances on Union Jack Lattices."""

__author__ = "Ruben S. Andrist"
__email__ = "randrist@amazon.com"

import json
import sys


def main(argv):
    # Usage: python solver.py some_instance.json
    assert len(argv) == 2
    assert argv[-1][-5:] == ".json"
    with open(argv[-1]) as fh:
        instance = json.load(fh)
    assert instance["problem"]["type"] == "mis"

    # This solver uses the union jack size as an input
    # (it is not a solver for generic graphs)
    L = instance["problem"]["meta"]["params"]["L"]

    # Translate edge list to adjacency list
    nn = []
    N = len(nn)
    for e in instance["problem"]["edges"]:
        a, b = e["ids"]
        N = max(N, a + 1, b + 1)
        if N > len(nn):
            nn += [[] for _ in range(N - len(nn))]
        nn[a] += [b]
        nn[b] += [a]

    # Sweeping line solver
    #
    # We keep track of the best score (=mis size) for each possible assignment
    # on the "frontier" (i.e., those nodes already treated but connected to
    # nodes which haven't been treated yet).
    #
    # NOTE: This involves keeping track of at most 2^(L+1) variants since
    # the size of the frontier is limited by the size of the lattice.

    # Keep track of up to `max_candidates` actual assignments for printing
    # after solution (the rest is just counted).
    max_candidates = 5

    # Our initial variant set has only one entry with
    # - the key "", meaning no nodes in the frontier (we haven't handled any)
    # - the three values score=0, assignments=[""], count=1
    #
    # NOTE: The difference between the `key` and `assignments` is that the former
    # only keeps track of the last `L+1` nodes, while assignments keeps up
    # to `max_candidates` possible full assignments.
    variants = {"": [0, [""], 1]}

    # Handle each of the nodes in the lattice.
    for i in range(N):
        # The new variant set we build while handling node `i`
        nv = {}
        for k, vs in variants.items():
            cost, assignments, count = vs

            # Check whether, for this variant, there is a neighbor
            # set (this chan be checked purely in the key). If there
            # is one set, it means we only need to generate child
            # variants by appending '0', but not '1'.
            neighbor_is_set = False
            for j in nn[i]:
                if j >= i:
                    continue
                if k[j - i] == "1":
                    neighbor_is_set = True
                    break

            # Generate child variants by appending '0'
            nk = k[-L - 1 :] + "0"
            if nk not in nv or cost > nv[nk][0]:
                # We found a better score -> overwrite
                na = [a + "0" for a in assignments]
                nv[nk] = [cost, na, count]
            elif cost == nv[nk][0]:
                # We found a maching score, add the count
                nv[nk][1] += [a + "0" for a in assignments]
                nv[nk][1] = nv[nk][1][:max_candidates]
                nv[nk][2] += count

            # If no neighbor is set, also create child variants appending '1'
            if not neighbor_is_set:
                nk = k[-L - 1 :] + "1"
                if nk not in nv or cost + 1 > nv[nk][0]:
                    # We found a better score -> overwrite
                    na = [a + "1" for a in assignments]
                    nv[nk] = [cost + 1, na, count]
                elif cost + 1 == nv[nk][0]:
                    # We found a matching score, add the count
                    nv[nk][1] += [a + "1" for a in assignments]
                    nv[nk][1] = nv[nk][1][:max_candidates]
                    nv[nk][2] += count

        # Swap the new variants into the main one
        variants = nv

    # Find the best score in all the final variants
    best = 0
    candidates = []
    best_count = 0
    for _, vs in variants.items():
        cost, assignments, count = vs
        if cost > best:
            best = cost
            best_count = count
            candidates = assignments
        elif cost == best:
            best_count += count
            candidates += assignments

    # Print results to the screen
    print("file:", argv[-1])
    print(f"|mis|={best}")
    print(f"degeneracy={best_count}")
    if best_count <= max_candidates:
        print("\nsolutions:")
    else:
        print(f"first {max_candidates} solutions:")

    for candidate in candidates[:max_candidates]:
        print([i for i, v in enumerate(candidate) if v == "1"])
    print()
    print("NOTE: Node indices are 0-indexed!")


if __name__ == "__main__":
    main(sys.argv)
